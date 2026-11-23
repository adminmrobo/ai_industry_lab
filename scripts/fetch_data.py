"""ai_industry_lab 데이터 수집 스크립트 (GitHub Actions에서 실행).

- 주가(일별 수정종가): Yahoo Finance (yfinance)
- 컨센서스 스냅샷(목표주가·투자의견): Yahoo Finance (yfinance .info)
- 현금흐름표(분기·연간): Yahoo Finance (yfinance)
- 거시지표: FRED (fredgraph.csv, API 키 불필요)

결과는 data/ 폴더에 저장되고, 워크플로가 바뀐 경우에만 커밋한다.
"""
from __future__ import annotations

import io
import json
import re
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# 그림(Bloomberg) 속 상장사 7곳 + 영상(50 AI Companies) 속 상장사 5곳 + 비교 지수
IMAGE_TICKERS = ["NVDA", "MSFT", "AMD", "ORCL", "INTC", "CRWV", "NBIS"]
VIDEO_TICKERS = ["GOOGL", "META", "QCOM", "TSLA", "SNOW"]
BENCH = ["^GSPC", "^NDX", "^SOX"]
ALL = IMAGE_TICKERS + VIDEO_TICKERS + BENCH

FRED = {
    "DGS10": "미 국채 10년 금리(%)",
    "DGS2": "미 국채 2년 금리(%)",
    "DGS3MO": "미 국채 3개월 금리(%)",
    "DFF": "연방기금 실효금리(%)",
    "T10Y2Y": "10년-2년 금리차(%p)",
    "UMCSENT": "미시간대 소비자심리지수",
    "PAYEMS": "비농업 고용자 수(천 명)",
    "UNRATE": "실업률(%)",
    "CPIAUCSL": "소비자물가지수(CPI)",
    "CPILFESL": "근원 CPI",
    "VIXCLS": "VIX 변동성지수",
    "BAMLH0A0HYM2": "하이일드 스프레드(%p)",
    "DTWEXBGS": "달러 지수(광의)",
    # 연준 Z.1 금융계정(미국판 자금순환표) 후보 - 제목을 함께 받아 확인한다
    "BOGZ1FA105000005Q": "Z.1 비금융기업 순대출(+)/순차입(-)",
    "BOGZ1FA106000105Q": "Z.1 비금융기업 내부자금(후보)",
    "BOGZ1FA105050005Q": "Z.1 비금융기업 자본지출(후보)",
    "NCBCMDPMVCE": "Z.1 비금융기업 부채/시가총액(후보)",
    "BCNSDODNS": "Z.1 비금융기업 부채 잔액(후보)",
}

UA = {"User-Agent": "Mozilla/5.0 (ai_industry_lab data fetch)"}
meta: dict = {"fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": {}}


def log(key, ok, note=""):
    meta["status"][key] = {"ok": ok, "note": note}
    print(("OK  " if ok else "ERR ") + key, note)


def fetch_prices():
    import yfinance as yf

    df = yf.download(ALL, start="2018-01-01", auto_adjust=True, progress=False, group_by="column", threads=True)
    close = df["Close"].copy()
    vol = df["Volume"].copy()
    close.index = close.index.strftime("%Y-%m-%d")
    vol.index = vol.index.strftime("%Y-%m-%d")
    close.round(4).to_csv(DATA / "prices.csv", index_label="date")
    vol.to_csv(DATA / "volumes.csv", index_label="date")
    log("prices", True, f"{close.shape[0]} rows, last {close.index[-1]}")


def fetch_consensus_and_cashflow():
    import yfinance as yf

    keys = [
        "longName", "currency", "currentPrice", "previousClose", "marketCap",
        "targetMeanPrice", "targetMedianPrice", "targetHighPrice", "targetLowPrice",
        "recommendationKey", "recommendationMean", "numberOfAnalystOpinions",
        "trailingPE", "forwardPE", "trailingEps", "forwardEps",
        "totalRevenue", "revenueGrowth", "grossMargins", "operatingMargins",
        "freeCashflow", "operatingCashflow", "totalCash", "totalDebt", "sector", "industry",
    ]
    cons, cf_out = {}, {}
    rows_want = {
        "Operating Cash Flow": "ocf",
        "Investing Cash Flow": "icf",
        "Financing Cash Flow": "fcf_fin",
        "Capital Expenditure": "capex",
        "Free Cash Flow": "fcf",
        "Issuance Of Debt": "debt_issued",
        "Repayment Of Debt": "debt_repaid",
        "Repurchase Of Capital Stock": "buyback",
        "Common Stock Issuance": "stock_issued",
        "Cash Dividends Paid": "dividends",
        "Changes In Cash": "cash_change",
    }
    for t in IMAGE_TICKERS + VIDEO_TICKERS:
        tk = yf.Ticker(t)
        try:
            info = tk.info or {}
            cons[t] = {k: info.get(k) for k in keys}
            log(f"consensus:{t}", True)
        except Exception as e:  # noqa: BLE001
            log(f"consensus:{t}", False, repr(e)[:200])
        out = {}
        for freq, attr in (("quarterly", "quarterly_cashflow"), ("annual", "cashflow")):
            try:
                cf = getattr(tk, attr)
                ser = {}
                if cf is not None and not cf.empty:
                    for raw, short in rows_want.items():
                        if raw in cf.index:
                            s = cf.loc[raw].dropna()
                            ser[short] = {d.strftime("%Y-%m-%d"): float(v) for d, v in s.items()}
                out[freq] = ser
            except Exception as e:  # noqa: BLE001
                log(f"cashflow:{t}:{freq}", False, repr(e)[:200])
        try:
            inc = tk.quarterly_income_stmt
            if inc is not None and not inc.empty:
                for raw, short in (("Total Revenue", "revenue"), ("Net Income", "net_income"), ("Operating Income", "op_income")):
                    if raw in inc.index:
                        s = inc.loc[raw].dropna()
                        out.setdefault("quarterly", {})[short] = {d.strftime("%Y-%m-%d"): float(v) for d, v in s.items()}
        except Exception as e:  # noqa: BLE001
            log(f"income:{t}", False, repr(e)[:200])
        cf_out[t] = out
        time.sleep(1.0)
    snap = {"snapshot_utc": meta["fetched_at_utc"], "source": "Yahoo Finance via yfinance", "data": cons}
    (DATA / "consensus.json").write_text(json.dumps(snap, ensure_ascii=False, indent=1))
    (DATA / "cashflow.json").write_text(json.dumps({"source": "Yahoo Finance via yfinance", "data": cf_out}, ensure_ascii=False, indent=1))
    # 컨센서스는 날짜별 이력으로도 남긴다(매일 쌓임)
    hist = DATA / "consensus_history"
    hist.mkdir(exist_ok=True)
    (hist / f"{meta['fetched_at_utc'][:10]}.json").write_text(json.dumps(snap, ensure_ascii=False))


def fred_title(sid: str) -> str:
    try:
        html = requests.get(f"https://fred.stlouisfed.org/series/{sid}", headers=UA, timeout=30).text
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    except Exception:  # noqa: BLE001
        return ""


def fetch_fred():
    frames, titles = [], {}
    for sid, ko in FRED.items():
        try:
            r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA, timeout=60)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            df.columns = ["date", sid]
            df[sid] = pd.to_numeric(df[sid], errors="coerce")
            df = df[df["date"] >= "2015-01-01"].set_index("date")
            frames.append(df)
            titles[sid] = {"ko": ko, "fred_title": fred_title(sid)}
            log(f"fred:{sid}", True, titles[sid]["fred_title"][:90])
        except Exception as e:  # noqa: BLE001
            log(f"fred:{sid}", False, repr(e)[:200])
        time.sleep(0.5)
    if frames:
        allf = pd.concat(frames, axis=1).sort_index()
        allf.to_csv(DATA / "macro.csv", index_label="date")
    (DATA / "macro_meta.json").write_text(json.dumps(titles, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    for fn in (fetch_prices, fetch_fred, fetch_consensus_and_cashflow):
        try:
            fn()
        except Exception:  # noqa: BLE001
            log(fn.__name__, False, traceback.format_exc()[-400:])
    (DATA / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
