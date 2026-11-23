"""data/ 원자료로 페이지용 JSON(site/*.json)을 만든다. Actions에서 수집 직후 함께 실행된다."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, SITE = ROOT / "data", ROOT / "data" / "site"
SITE.mkdir(parents=True, exist_ok=True)

IMAGE = ["NVDA", "MSFT", "AMD", "ORCL", "INTC", "CRWV", "NBIS"]
VIDEO = ["GOOGL", "META", "QCOM", "TSLA", "SNOW"]
BENCH = {"^NDX": "나스닥100", "^SOX": "필라델피아 반도체", "^GSPC": "S&P 500"}
NAMES = {"NVDA": "NVIDIA", "MSFT": "Microsoft", "AMD": "AMD", "ORCL": "Oracle", "INTC": "Intel",
         "CRWV": "CoreWeave", "NBIS": "Nebius", "GOOGL": "Alphabet", "META": "Meta", "QCOM": "Qualcomm",
         "TSLA": "Tesla", "SNOW": "Snowflake"}
GROUPS = {
    "그림 7개사(순환 고리)": IMAGE,
    "영상 5개사(고리 바깥)": VIDEO,
    "칩(NVDA·AMD·INTC·QCOM)": ["NVDA", "AMD", "INTC", "QCOM"],
    "클라우드·네오클라우드(ORCL·CRWV·NBIS)": ["ORCL", "CRWV", "NBIS"],
    "빅테크(MSFT·GOOGL·META)": ["MSFT", "GOOGL", "META"],
}
BASE, W0, W1 = "2025-10-07", "2025-07-07", "2026-01-07"


def r(x, n=4):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), n)


def lst(s: pd.Series, n=4):
    return [r(v, n) for v in s.tolist()]


prices = pd.read_csv(DATA / "prices.csv", index_col=0, parse_dates=True).sort_index()
macro = pd.read_csv(DATA / "macro.csv", index_col=0, parse_dates=True).sort_index()
meta = json.loads((DATA / "meta.json").read_text())
macro_meta = json.loads((DATA / "macro_meta.json").read_text())
events = json.loads((DATA / "static" / "events.json").read_text())
private = json.loads((DATA / "static" / "private_valuations.json").read_text())

# ============================================================ 1단계
win = prices.loc[W0:W1]
base_row = prices.loc[:BASE].iloc[-1]
stage1 = {"base": BASE, "window": [W0, W1], "dates": win.index.strftime("%Y-%m-%d").tolist(),
          "names": NAMES | BENCH, "tickers": IMAGE, "bench": list(BENCH), "series": {}, "summary": {}}
ndx_ret = prices["^NDX"].pct_change()
for t in IMAGE + list(BENCH):
    s = win[t]
    stage1["series"][t] = {"close": lst(s, 2), "index": lst(s / base_row[t] * 100, 2)}
    pre, post = s.loc[:BASE], s.loc[BASE:]
    peak = s.cummax()
    stage1["summary"][t] = {
        "start": r(s.iloc[0], 2), "base": r(base_row[t], 2), "end": r(s.iloc[-1], 2),
        "pre_pct": r((pre.iloc[-1] / pre.iloc[0] - 1) * 100, 1),
        "post_pct": r((post.iloc[-1] / post.iloc[0] - 1) * 100, 1),
        "max_dd_pct": r(((s / peak) - 1).min() * 100, 1),
        "high": r(s.max(), 2), "high_date": s.idxmax().strftime("%Y-%m-%d"),
        "low": r(s.min(), 2), "low_date": s.idxmin().strftime("%Y-%m-%d"),
    }
# 종목별로 '발표 반응 구간'(반응일~4거래일 뒤)을 모아 둔다 → 베타 추정에서 제외
event_days = {}
for ev in events:
    i0 = prices.index.searchsorted(pd.Timestamp(ev["react"]))
    for t in ev["tickers"]:
        event_days.setdefault(t, set()).update(prices.index[i0:i0 + 5])
reactions = []
for ev in events:
    for t in ev["tickers"]:
        if t not in prices.columns:
            continue
        ret = prices[t].pct_change()
        idx = prices.index.searchsorted(pd.Timestamp(ev["react"]))
        if idx >= len(prices.index):
            continue
        d0 = prices.index[idx]
        d5 = prices.index[min(idx + 4, len(prices.index) - 1)]
        day = ret.loc[d0]
        ab = day - ndx_ret.loc[d0]
        cum5 = (1 + ret.loc[d0:d5]).prod() - 1
        cum5n = (1 + ndx_ret.loc[d0:d5]).prod() - 1
        # 시장모형: 반응일 130~11거래일 전(120일) 구간에서 종목 수익률 = a + b × 나스닥100 수익률 추정
        est_all = pd.concat([ret, ndx_ret], axis=1).iloc[max(0, idx - 130): idx - 10].dropna()
        est = est_all[~est_all.index.isin(event_days.get(t, set()))]
        beta = alpha = mm_ab = mm_car5 = None
        beta_raw = float(np.polyfit(est_all.iloc[:, 1], est_all.iloc[:, 0], 1)[0]) if len(est_all) >= 60 else None
        if len(est) >= 60:
            b_, a_ = np.polyfit(est.iloc[:, 1], est.iloc[:, 0], 1)
            beta, alpha = float(b_), float(a_)
            win5 = pd.concat([ret, ndx_ret], axis=1).loc[d0:d5]
            ar = win5.iloc[:, 0] - (alpha + beta * win5.iloc[:, 1])
            mm_ab, mm_car5 = float(ar.iloc[0]), float(ar.sum())
        reactions.append({"date": ev["date"], "react": d0.strftime("%Y-%m-%d"), "ticker": t, "title": ev["title"],
                          "day_pct": r(day * 100, 2), "abn_pct": r(ab * 100, 2),
                          "cum5_pct": r(cum5 * 100, 2), "abn5_pct": r((cum5 - cum5n) * 100, 2),
                          "beta": r(beta, 2), "mm_abn_pct": r(mm_ab * 100 if mm_ab is not None else None, 2),
                          "mm_car5_pct": r(mm_car5 * 100 if mm_car5 is not None else None, 2), "est_n": int(len(est)),
                          "est_excluded": int(len(est_all) - len(est)), "beta_raw": r(beta_raw, 2),
                          "days_after": int(min(4, len(prices.index) - 1 - idx)), "recent": bool(ev.get("recent"))})
R0 = W1
rec = prices.loc[R0:]
rbase = prices.loc[:R0].iloc[-1]
stage1["recent"] = {"base": R0, "dates": rec.index.strftime("%Y-%m-%d").tolist(),
                    "series": {t: {"close": lst(rec[t], 2), "index": lst(rec[t] / rbase[t] * 100, 2)} for t in IMAGE + list(BENCH) + ["GOOGL", "SNOW"]},
                    "summary": {t: {"pct": r((rec[t].dropna().iloc[-1] / rbase[t] - 1) * 100, 1),
                                    "max_dd_pct": r(((rec[t] / rec[t].cummax()) - 1).min() * 100, 1)} for t in IMAGE + list(BENCH)}}
stage1["names"].update({"GOOGL": "Alphabet", "SNOW": "Snowflake"})
stage1["events"] = events
stage1["reactions"] = reactions
stage1["private"] = private
(SITE / "stage1.json").write_text(json.dumps(stage1, ensure_ascii=False))

# ============================================================ 3단계
eq = IMAGE + VIDEO
# --- 월별 패널
mp = prices[eq + list(BENCH)].resample("ME").last()
mret = mp.pct_change()
grp = {}
for g, mem in GROUPS.items():
    gr = mret[mem].mean(axis=1, skipna=True)  # 동일가중, 상장 전 종목은 빠짐
    first = mp[mem].dropna(how="all").index[0]
    idx = (1 + gr.loc[first:].fillna(0)).cumprod() * 100
    idx.iloc[0] = 100.0
    grp[g] = idx
grp = pd.DataFrame(grp)
_cons = json.loads((DATA / "consensus.json").read_text())["data"]
shares = {t: (_cons[t]["marketCap"] / _cons[t]["currentPrice"]) for t in eq
          if _cons.get(t, {}).get("marketCap") and _cons[t].get("currentPrice")}
grp_cw = {}
for g, mem in GROUPS.items():
    mcap_prev = mp[mem].shift(1).mul(pd.Series({t: shares.get(t, np.nan) for t in mem}))
    w = mcap_prev.div(mcap_prev.sum(axis=1), axis=0)
    gr = (mret[mem] * w).sum(axis=1, min_count=1)
    first = mp[mem].dropna(how="all").index[0]
    idx = (1 + gr.loc[first:].fillna(0)).cumprod() * 100
    idx.iloc[0] = 100.0
    grp_cw[g] = idx
grp_cw = pd.DataFrame(grp_cw)
first_month = {t: (mp[t].first_valid_index().strftime("%Y-%m") if mp[t].first_valid_index() is not None else "9999-12") for t in eq}
group_entries = {g: [{"ticker": t, "month": first_month[t]} for t in mem if "2018-01" < first_month[t] < "9999"] for g, mem in GROUPS.items()}

mm = pd.DataFrame(index=mp.index)
for sid in ["DGS10", "DGS2", "DGS3MO", "DFF", "T10Y2Y", "VIXCLS", "BAMLH0A0HYM2", "DTWEXBGS"]:
    mm[sid] = macro[sid].resample("ME").mean()
for sid in ["UMCSENT", "UNRATE", "PAYEMS", "CPIAUCSL", "CPILFESL"]:
    m = macro[sid].dropna()
    m.index = m.index + pd.offsets.MonthEnd(0)
    mm[sid] = m
mm["NFP_CHG"] = mm["PAYEMS"].diff()
mm["CPI_YOY"] = mm["CPIAUCSL"].pct_change(12) * 100
mm["CORE_YOY"] = mm["CPILFESL"].pct_change(12) * 100
MACRO_VARS = {
    "DGS10": ("미 국채 10년 금리", "%"), "DGS2": ("미 국채 2년 금리", "%"), "DFF": ("연방기금 실효금리", "%"),
    "T10Y2Y": ("10년-2년 금리차", "%p"), "UMCSENT": ("미시간대 소비자심리지수", "pt"),
    "NFP_CHG": ("비농업 고용 월간 증감", "천 명"), "UNRATE": ("실업률", "%"),
    "CPI_YOY": ("CPI 상승률(전년 대비)", "%"), "CORE_YOY": ("근원 CPI 상승률", "%"),
    "VIXCLS": ("VIX 변동성지수", "pt"), "BAMLH0A0HYM2": ("하이일드 스프레드", "%p"), "DTWEXBGS": ("달러 지수(광의)", "pt"),
}
start = "2018-01-31"
mp_s, mm_s, grp_s = mp.loc[start:], mm.loc[start:], grp.loc[start:]
monthly = {"dates": mp_s.index.strftime("%Y-%m").tolist(),
           "price": {t: lst(mp_s[t], 2) for t in eq + list(BENCH)},
           "group": {g: lst(grp_s[g], 2) for g in GROUPS},
           "group_cw": {g: lst(grp_cw.loc[start:][g], 2) for g in GROUPS},
           "macro": {k: lst(mm_s[k], 3) for k in MACRO_VARS}}

# --- 상관(월간): 월 수익률 vs 거시 변수 변화
chg = pd.DataFrame({
    "Δ10년 금리": mm["DGS10"].diff(), "Δ2년 금리": mm["DGS2"].diff(), "Δ금리차": mm["T10Y2Y"].diff(),
    "Δ소비자심리": mm["UMCSENT"].diff(), "고용 증감": mm["NFP_CHG"], "ΔCPI 상승률": mm["CPI_YOY"].diff(),
    "ΔVIX": mm["VIXCLS"].diff(), "Δ하이일드": mm["BAMLH0A0HYM2"].diff(), "Δ달러": mm["DTWEXBGS"].pct_change() * 100,
})
cols = eq + list(GROUPS)
gret = grp.pct_change()
corr_rows, nobs, sig = [], [], []
for c in cols:
    y = mret[c] if c in mret else gret[c]
    row, nrow, srow = [], [], []
    for k in chg.columns:
        d = pd.concat([y, chg[k]], axis=1).loc[start:].dropna()
        cc = d.corr().iloc[0, 1] if len(d) >= 18 else None
        row.append(r(cc, 3))
        nrow.append(int(len(d)))
        # 피셔 z 변환: |atanh(r)|·√(n−3) > 1.96 이면 5% 수준에서 0과 다르다고 본다
        srow.append(bool(cc is not None and abs(np.arctanh(cc)) * np.sqrt(len(d) - 3) > 1.96))
    corr_rows.append(row)
    nobs.append(nrow)
    sig.append(srow)
corr_month = {"rows": [NAMES.get(c, c) for c in cols], "row_ids": cols, "cols": list(chg.columns), "z": corr_rows, "n": nobs, "sig": sig}

# --- 롤링 상관(일간 60거래일): 일 수익률 vs 일간 거시 변화
dret = prices[eq + list(BENCH)].pct_change()
dm = pd.DataFrame({"Δ10년 금리": macro["DGS10"].diff(), "ΔVIX": macro["VIXCLS"].diff(),
                   "Δ하이일드": macro["BAMLH0A0HYM2"].diff(), "Δ달러": macro["DTWEXBGS"].pct_change()})
dm = dm.reindex(dret.index)
roll = {}
for k in dm.columns:
    out = {}
    for t in eq:
        d = pd.concat([dret[t], dm[k]], axis=1).dropna()
        rc = d.iloc[:, 0].rolling(60, min_periods=50).corr(d.iloc[:, 1])
        out[t] = rc
    df = pd.DataFrame(out).loc["2019-01-01":]
    df = df.resample("W-FRI").last()
    roll[k] = {"dates": df.index.strftime("%Y-%m-%d").tolist(), "z": {t: lst(df[t], 3) for t in eq}}

# --- Z.1(미국 자금순환) 비금융기업: 자금 부족 = 설비투자 - 총저축(내부자금)
z1 = macro[["BOGZ1FA105050005Q", "BOGZ1FA106000105Q", "NCBCMDPMVCE", "BCNSDODNS"]].dropna(how="all")
z1 = z1.loc["2010-01-01":]
gap = (z1["BOGZ1FA105050005Q"] - z1["BOGZ1FA106000105Q"]) / 1000.0
qgrp = grp.resample("QE").last()
qgrp.index = qgrp.index - pd.offsets.QuarterBegin(startingMonth=1)
z1q = {"dates": z1.index.strftime("%Y-%m-%d").tolist(),
       "capex_bn": lst(z1["BOGZ1FA105050005Q"] / 1000, 1), "saving_bn": lst(z1["BOGZ1FA106000105Q"] / 1000, 1),
       "gap_bn": lst(gap, 1), "debt_to_equity_pct": lst(z1["NCBCMDPMVCE"], 2), "debt_bn": lst(z1["BCNSDODNS"] / 1000, 1),
       "group_q": {g: lst(qgrp[g].reindex(z1.index), 2) for g in GROUPS}}

# --- 현금흐름표·컨센서스
cf = json.loads((DATA / "cashflow.json").read_text())["data"]
cons = json.loads((DATA / "consensus.json").read_text())
cons_rows = []
for t in eq:
    v = cons["data"].get(t, {})
    cp, tm = v.get("currentPrice"), v.get("targetMeanPrice")
    cons_rows.append({"ticker": t, "name": NAMES[t], "group": "image" if t in IMAGE else "video",
                      "price": cp, "target_mean": tm, "target_high": v.get("targetHighPrice"), "target_low": v.get("targetLowPrice"),
                      "upside_pct": r((tm / cp - 1) * 100, 1) if cp and tm else None,
                      "rec": v.get("recommendationKey"), "rec_mean": v.get("recommendationMean"),
                      "n": v.get("numberOfAnalystOpinions"), "mcap_bn": r((v.get("marketCap") or 0) / 1e9, 1),
                      "fpe": r(v.get("forwardPE"), 1), "tpe": r(v.get("trailingPE"), 1)})

def _med(g):
    v = [x["upside_pct"] for x in cons_rows if x["group"] == g and x["upside_pct"] is not None]
    return r(float(np.median(v)), 1) if v else None


cons_summary = {"median_upside": {"image": _med("image"), "video": _med("video")},
                "mean_upside": {g: r(float(np.mean([x["upside_pct"] for x in cons_rows if x["group"] == g and x["upside_pct"] is not None])), 1) for g in ("image", "video")}}
stage3 = {"generated": meta["fetched_at_utc"], "names": NAMES | BENCH, "image": IMAGE, "video": VIDEO,
          "groups": GROUPS, "group_entries": group_entries, "macro_vars": MACRO_VARS, "macro_titles": macro_meta,
          "monthly": monthly, "corr_month": corr_month, "roll": roll, "z1": z1q,
          "cashflow": cf, "consensus": {"snapshot_utc": cons["snapshot_utc"], "rows": cons_rows, "summary": cons_summary},
          "macro_last": {k: macro[k].last_valid_index().strftime("%Y-%m-%d") for k in macro.columns}}
(SITE / "stage3.json").write_text(json.dumps(stage3, ensure_ascii=False))

# ============================================================ 2단계(정적 데이터 묶음)
st = DATA / "static"
stage2 = {"companies": json.loads((st / "companies.json").read_text()), "edges": json.loads((st / "edges.json").read_text())}
(SITE / "stage2.json").write_text(json.dumps(stage2, ensure_ascii=False))

(SITE / "meta.json").write_text(json.dumps({"fetched_at_utc": meta["fetched_at_utc"],
                                             "price_last": prices.index[-1].strftime("%Y-%m-%d"),
                                             "price_first": prices.dropna(how="all").index[0].strftime("%Y-%m-%d")}, ensure_ascii=False))
print("ok", {p.name: p.stat().st_size for p in SITE.glob("*.json")})
