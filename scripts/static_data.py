"""손으로 정리한 정적 데이터(출처 포함)를 data/static/*.json으로 내보낸다.

- events: 1단계 주가 차트에 꽂을 거래 발표일
- private_valuations: 비상장사 기업가치(투자 라운드·인수 기준)
- companies: 그림(Bloomberg) 15개사 + 영상(50 AI Companies) 중 그림과 겹치지 않는 42개사
- edges: 회사 간 관계(투자·공급·서비스·인수·지배구조)

원칙: 출처 URL이 있는 관계만 넣는다. 그림에 그려진 관계는 출처를 'Bloomberg 그림(2025-10)'으로 둔다.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "static"
OUT.mkdir(parents=True, exist_ok=True)

BLOOMBERG = "https://www.bloomberg.com/news/features/2025-10-07/openai-s-nvidia-amd-deals-boost-1-trillion-ai-boom-with-circular-deals"

# ---------------------------------------------------------------- 거래 발표일
# react: 주가가 반응한 첫 거래일(장 마감 뒤 발표면 다음 거래일)
EVENTS = [
    dict(date="2025-09-08", react="2025-09-09", tickers=["NBIS", "MSFT"], kind="services",
         title="Nebius–Microsoft GPU 인프라 계약 174억 달러(최대 194억)",
         note="장 마감 뒤 발표, 다음 날 반응", src="https://www.nasdaq.com/articles/nebius-shares-soar-us-174-billion-microsoft-ai-deal"),
    dict(date="2025-09-09", react="2025-09-10", tickers=["ORCL"], kind="services",
         title="Oracle 1분기 실적: 잔여이행의무(RPO·계약했지만 아직 매출로 잡히지 않은 금액) 4,550억 달러, 359% 증가",
         note="장 마감 뒤 발표", src="https://www.oracle.com/ae/news/announcement/q1fy26-earnings-release-2025-09-09/"),
    dict(date="2025-09-09", react="2025-09-09", tickers=["NVDA"], kind="vc",
         title="Mistral 시리즈 C 17억 유로(ASML 주도, Nvidia 참여)",
         note="", src="https://tech.eu/2025/09/09/mistral-bags-1-7bn-funding-round-as-asml-takes-significant-stake/"),
    dict(date="2025-09-15", react="2025-09-15", tickers=["CRWV", "NVDA"], kind="services",
         title="Nvidia, CoreWeave 미사용 용량 63억 달러 구매 보증(2032년 4월까지)",
         note="9월 9일 체결, 9월 15일 8-K 공시(반응일 = 공시일)", src="https://www.sec.gov/Archives/edgar/data/1769628/000176962825000047/crwv-20250909.htm"),
    dict(date="2025-09-16", react="2025-09-16", tickers=["NVDA", "INTC"], kind="vc",
         title="Figure AI 시리즈 C, 기업가치 390억 달러(Nvidia·Intel Capital 참여)",
         note="", src="https://figure.ai/news/series-c"),
    dict(date="2025-09-18", react="2025-09-18", tickers=["NVDA", "INTC"], kind="investment",
         title="Nvidia, Intel 보통주 50억 달러 매입·공동 개발 발표",
         note="", src="https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-and-Intel-to-Develop-AI-Infrastructure-and-Personal-Computing-Products/"),
    dict(date="2025-09-22", react="2025-09-22", tickers=["NVDA", "ORCL", "MSFT"], kind="investment",
         title="Nvidia–OpenAI 의향서(LOI·정식 계약 전 합의): 최대 1,000억 달러 투자·10GW 배치",
         note="의향서였고, 2026년 2월 300억 달러 지분 투자로 바뀌었다는 보도가 있음", src="https://investor.nvidia.com/news/press-release-details/2025/OpenAI-and-NVIDIA-Announce-Strategic-Partnership-to-Deploy-10-Gigawatts-of-NVIDIA-Systems/"),
    dict(date="2025-10-02", react="2025-10-02", tickers=[], kind="investment",
         title="OpenAI 직원 지분 매각, 기업가치 5,000억 달러",
         note="상장사 반응 대상 아님(비상장 기업가치 기준점)", src="https://www.bloomberg.com/news/articles/2025-10-02/openai-completes-share-sale-at-record-500-billion-valuation"),
    dict(date="2025-10-06", react="2025-10-06", tickers=["AMD"], kind="hardware",
         title="AMD–OpenAI 6GW GPU 공급 + OpenAI에 AMD 주식 최대 1억6천만 주 워런트(정해진 값에 주식을 살 권리)",
         note="", src="https://ir.amd.com/news-events/press-releases/detail/1260/amd-and-openai-announce-strategic-partnership-to-deploy-6-gigawatts-of-amd-gpus"),
    dict(date="2025-10-07", react="2025-10-07", tickers=[], kind="base",
         title="기준시점: Bloomberg 그림 공개",
         note="이 날 종가를 100으로 둔다", src=BLOOMBERG),
    dict(date="2025-11-13", react="2025-11-13", tickers=["NVDA", "GOOGL"], kind="vc",
         title="Anysphere(Cursor) 23억 달러 조달, 기업가치 293억 달러(Nvidia·Google 참여)",
         note="", src="https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/"),
    dict(date="2025-11-18", react="2025-11-18", tickers=["MSFT", "NVDA"], kind="investment",
         title="Microsoft·Nvidia, Anthropic에 최대 50억·100억 달러 투자 / Anthropic, Azure 300억 달러 구매",
         note="", src="https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships"),
    dict(date="2025-12-03", react="2025-12-04", tickers=["SNOW"], kind="services",
         title="Snowflake–Anthropic 2억 달러 다년 계약",
         note="실적 발표 직후 공개", src="https://snowflake.com/en/news/press-releases/snowflake-and-anthropic-announce-200-million-partnership-to-bring-agentic-ai-to-global-enterprises/"),
    dict(date="2025-12-10", react="2025-12-11", tickers=["ORCL"], kind="services",
         title="Oracle 2분기 실적: 설비투자 확대(연간 약 500억 달러 전망), 주가 11% 하락",
         note="장 마감 뒤 발표", src="https://fortune.com/2025/12/11/oracle-earnings-stock-falls-11-percent-why-investors-disappointed-data-centers-cloud/"),
    dict(date="2025-12-24", react="2025-12-26", tickers=["NVDA"], kind="hardware",
         title="Nvidia–Groq 추론 기술 비독점 라이선스(약 200억 달러 보도)",
         note="크리스마스 이브 단축장, 다음 거래일 기준", src="https://techcrunch.com/2025/12/24/nvidia-acquires-ai-chip-challenger-groq-for-20b-report-says/"),
    dict(date="2026-01-06", react="2026-01-07", tickers=["NVDA"], kind="vc",
         title="xAI 시리즈 E 200억 달러(Nvidia 참여)",
         note="미국 장 마감 뒤 발표, 다음 거래일 기준", src="https://x.ai/news/series-e"),
]

# 기준시점 이후(2026-01-08~) 발표: 원인을 단정하지 않고 날짜만 나란히 둔다
EVENTS += [
    dict(date="2026-01-14", react="2026-01-15", tickers=[], kind="services", recent=True,
         title="OpenAI–Cerebras 750MW 컴퓨팅 계약(100억 달러 이상 보도)", note="상장사 반응 대상 아님",
         src="https://techcrunch.com/2026/01/14/openai-signs-deal-reportedly-worth-10-billion-for-compute-from-cerebras/"),
    dict(date="2026-02-01", react="2026-02-02", tickers=["ORCL"], kind="services", recent=True,
         title="Oracle, 2026년 최대 500억 달러 부채·주식 조달 계획 발표", note="일요일 밤 발표, 월요일 반응",
         src="https://fortune.com/2026/02/02/why-did-oracle-stock-fall-openai-exposure-nvidia-microsoft/"),
    dict(date="2026-02-02", react="2026-02-02", tickers=["SNOW"], kind="services", recent=True,
         title="Snowflake–OpenAI 2억 달러 다년 계약", note="",
         src="https://investors.snowflake.com/news/news-details/2026/Snowflake-and-OpenAI-Forge-200-Million-Partnership-to-Bring-Enterprise-Ready-AI-to-the-Worlds-Most-Trusted-Data-Platform/default.aspx"),
    dict(date="2026-02-02", react="2026-02-03", tickers=[], kind="acquisition", recent=True,
         title="SpaceX, xAI 인수(xAI 2,500억 달러 평가 보도)", note="상장사 반응 대상 아님",
         src="https://news.bloomberglaw.com/tech-and-telecom-law/elon-musks-spacex-said-to-combine-with-xai-ahead-of-mega-ipo"),
    dict(date="2026-02-27", react="2026-02-27", tickers=["NVDA"], kind="investment", recent=True,
         title="OpenAI 1,100억 달러 조달 발표(Nvidia 300억·Amazon 500억 달러 참여 보도)", note="2025-09 의향서 대신 지분 투자",
         src="https://builtin.com/articles/openai-raises-110b-730b-valuation-20260227"),
    dict(date="2026-04-24", react="2026-04-24", tickers=["GOOGL"], kind="investment", recent=True,
         title="Alphabet, Anthropic에 최대 400억 달러 투자(100억 달러 우선)", note="",
         src="https://www.thestar.com.my/tech/tech-news/2026/04/25/google-plans-to-invest-up-to-40-billion-in-anthropic-bloomberg-news-reports"),
    dict(date="2026-04-28", react="2026-04-28", tickers=["ORCL", "CRWV", "NVDA", "AMD"], kind="services", recent=True,
         title="WSJ 보도: OpenAI가 내부 사용자·매출 목표에 못 미침", note="보도일 기준",
         src="https://www.brecorder.com/news/amp/40418678"),
    dict(date="2026-06-16", react="2026-06-16", tickers=[], kind="acquisition", recent=True,
         title="SpaceX, Cursor(Anysphere) 600억 달러 주식 인수 합의(3분기 종결 예정)", note="상장사 반응 대상 아님(SPCX 미수집)",
         src="https://techcrunch.com/2026/06/16/spacex-to-acquire-cursor-for-60b-in-stock-days-after-blockbuster-ipo/"),
    dict(date="2026-11-12", react="2026-11-12", tickers=["NVDA"], kind="governance", recent=True,
         title="Nvidia CEO 교체 발표(젠슨 황 사임, 콜레트 크레스 임시 CEO) — 8-K", note="장 시작 전 발표",
         src="https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000082/nvidiaannouncesceotransiti.htm"),
    dict(date="2026-11-17", react="2026-11-18", tickers=["NVDA"], kind="earnings", recent=True,
         title="Nvidia 3분기(FY27) 실적: 매출 1,158억 달러(+103%) — 8-K", note="장 마감 뒤 발표",
         src="https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000088/q3fy27pr.htm"),
    dict(date="2026-11-19", react="2026-11-19", tickers=["MSFT", "NVDA", "GOOGL"], kind="ipo", recent=True,
         title="Anthropic 나스닥 상장(ANT, 공모가 83달러)", note="투자사 반응 비교용",
         src="https://www.aljazeera.com/economy/2026/11/19/anthropic-starts-trading-in-the-us-after-blockbuster-ipo"),
    dict(date="2026-11-20", react="2026-11-20", tickers=["NVDA"], kind="report", recent=True,
         title="로이터 보도: SEC가 Nvidia 회계를 들여다보는 중", note="보도 기준, SEC는 논평 거부",
         src="https://www.fool.com/investing/2026/11/20/nvidia-stock-plunge-wipes-out-nearly-usd500-billion-in-one-day-as-sec-reportedly-probes-its-accounting/"),
]

# ---------------------------------------------------------------- 비상장 기업가치(십억 달러)
PRIVATE = {
    "OpenAI": [
        ("2024-10-02", 157, "투자 라운드 66억 달러", "https://fortune.com/2024/10/02/openai-officially-raises-6-6-billion-funding-deal-157-billion-valuation-sam-altman-thrive-capital/"),
        ("2025-03-31", 300, "SoftBank 주도 400억 달러 라운드", "https://www.foxbusiness.com/markets/openai-becomes-worlds-most-valuable-private-company-500b-valuation-report"),
        ("2025-10-02", 500, "직원 지분 매각(세컨더리)", "https://www.bloomberg.com/news/articles/2025-10-02/openai-completes-share-sale-at-record-500-billion-valuation"),
        ("2026-03-31", 852, "1,220억 달러 라운드", "https://openai.com/en-US/index/accelerating-the-next-phase-ai/"),
    ],
    "xAI": [
        ("2024-12-23", 45, "시리즈 C 60억 달러(보도 기준 기업가치)", "https://techcrunch.com/2025/03/29/elon-musk-says-xai-acquired-x/"),
        ("2025-03-28", 80, "X 인수 시 xAI 단독 가치(X는 330억 달러)", "https://techcrunch.com/2025/03/28/elon-musk-says-xai-acquired-x"),
        ("2025-11-15", 230, "WSJ 보도 기업가치(2025년 11월, 일자 대략)", "https://finance.yahoo.com/news/musks-spacex-merge-xai-combined-212210116.html"),
        ("2026-02-02", 250, "SpaceX에 인수(보도 기준)", "https://news.bloomberglaw.com/tech-and-telecom-law/elon-musks-spacex-said-to-combine-with-xai-ahead-of-mega-ipo"),
    ],
    "Figure AI": [
        ("2024-02-29", 2.6, "시리즈 B 6.75억 달러(2024년 2월)", "https://finance.yahoo.com/news/figure-valued-39-billion-latest-131115237.html"),
        ("2025-09-16", 39, "시리즈 C 10억 달러 이상", "https://figure.ai/news/series-c"),
    ],
    "Anysphere(Cursor)": [
        ("2025-06-01", 9.9, "시리즈 C 9억 달러(6월, 일자 대략)", "https://finance.yahoo.com/news/anysphere-secures-900m-funding-083823106.html"),
        ("2025-11-13", 29.3, "시리즈 D 23억 달러", "https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/"),
        ("2026-06-16", 60, "SpaceX 인수 합의가(주식 교환)", "https://techcrunch.com/2026/06/16/spacex-to-acquire-cursor-for-60b-in-stock-days-after-blockbuster-ipo/"),
    ],
    "Mistral AI": [
        ("2024-06-01", 6.0, "6.4억 달러 라운드(2024년 6월, 일자 대략)", "https://siliconangle.com/2025/09/09/mistral-ai-raises-2b-led-chip-equipment-maker-asml-14b-valuation/"),
        ("2025-09-09", 13.7, "시리즈 C 17억 유로(117억 유로)", "https://mistral.ai/fr/news/mistral-ai-raises-1-7-b-to-accelerate-technological-progress-with-ai"),
    ],
}

# ---------------------------------------------------------------- 기업(57개)
# layer: bigtech, chip, cloud, model, app, robot, infra
# group: image(그림만), both(그림+영상), video(영상만)
C = []


def co(cid, name, layer, group, ticker, country, business, feature, parent=None, fsrc=None):
    # business: 각 사 공식 소개 요약 / feature: 사실 문장만, 근거가 필요한 문장은 fsrc에 출처
    C.append(dict(id=cid, name=name, layer=layer, group=group, ticker=ticker, country=country,
                  business=business, feature=feature, parent=parent, fsrc=fsrc))


# 그림(Bloomberg) 15개사 ─ 이 가운데 8개사는 영상에도 나온다
co("openai", "OpenAI", "model", "both", None, "미국", "ChatGPT와 GPT 계열 모델 개발·판매", "Bloomberg 그림에서 Nvidia와 함께 가장 많은 선이 이어진 회사. 2026-03 1,220억 달러 조달", fsrc="https://openai.com/en-US/index/accelerating-the-next-phase-ai/")
co("microsoft", "Microsoft", "bigtech", "image", "MSFT", "미국", "Azure 클라우드·오피스·윈도우", "OpenAI 최대 투자자이자 클라우드 공급자. 네오클라우드(CoreWeave·Nebius)에서 용량을 사 온다")
co("nvidia", "NVIDIA", "chip", "both", "NVDA", "미국", "AI 학습·추론용 GPU와 시스템", "칩을 공급하면서 OpenAI·xAI·CoreWeave 등 고객사에도 투자(관계망 참고). 2026-11-12 CEO 사임 공시", fsrc="https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000082/nvidiaannouncesceotransiti.htm")
co("amd", "AMD", "chip", "both", "AMD", "미국", "GPU(Instinct)·CPU", "OpenAI에 GPU를 공급하고 자사 주식 워런트를 대가로 줌")
co("intel", "Intel", "chip", "both", "INTC", "미국", "CPU·파운드리", "Nvidia가 50억 달러 지분 투자. 미국 정부도 지분 보유")
co("oracle", "Oracle", "cloud", "image", "ORCL", "미국", "데이터베이스·OCI 클라우드", "OpenAI와 3,000억 달러 클라우드 계약(그림). 2026-02 최대 500억 달러 부채·주식 조달 계획 발표", fsrc="https://fortune.com/2026/02/02/why-did-oracle-stock-fall-openai-exposure-nvidia-microsoft/")
co("coreweave", "CoreWeave", "cloud", "image", "CRWV", "미국", "GPU 전문 클라우드(네오클라우드)", "Nvidia가 주주이자 용량 구매 보증자. 2025년 3월 상장")
co("nebius", "Nebius", "cloud", "image", "NBIS", "네덜란드", "GPU 전문 클라우드", "Microsoft와 최대 194억 달러 계약. Yandex에서 분리")
co("nscale", "Nscale", "cloud", "image", None, "영국", "유럽 AI 데이터센터·GPU 클라우드", "Nvidia가 투자, OpenAI가 서비스 고객")
co("xai", "xAI", "model", "both", None, "미국", "Grok 모델", "2026-02 SpaceX에 인수. SpaceX는 2026-06-12 나스닥 상장(SPCX)", parent="SpaceX(SPCX)", fsrc="https://www.npr.org/2026/06/12/nx-s1-5855004/nx-s1-9808791")
co("mistral", "Mistral AI", "model", "both", None, "프랑스", "개방형 가중치 언어모델", "유럽 대표 모델 회사. ASML이 최대주주, Nvidia도 투자")
co("figure", "Figure AI", "robot", "both", None, "미국", "범용 휴머노이드 로봇", "Nvidia·Intel·Qualcomm 등 칩 회사가 함께 투자")
co("harvey", "Harvey", "app", "both", None, "미국", "법률 전문 AI", "OpenAI 스타트업 펀드 투자처")
co("anysphere", "Anysphere(Cursor)", "app", "image", None, "미국", "AI 코드 편집기 Cursor", "Nvidia·Google이 2025-11 투자 참여. 2026-06 SpaceX가 600억 달러 주식 인수 합의(3분기 종결 예정)", parent="SpaceX(인수 합의)", fsrc="https://techcrunch.com/2026/06/16/spacex-to-acquire-cursor-for-60b-in-stock-days-after-blockbuster-ipo/")
co("ambience", "Ambience Healthcare", "app", "image", None, "미국", "의료 기록 자동화 AI", "OpenAI 스타트업 펀드 투자처")

# 영상(50 AI Companies) 중 그림에 없는 42개사
# 1) 프런티어 모델
co("anthropic", "Anthropic", "model", "video", "ANT", "미국", "Claude 모델", "2025-11 Microsoft·Nvidia, 2026-04 Amazon·Alphabet 투자 발표. 2026-11-19 나스닥 상장(ANT, 주가 이력이 짧아 주가 분석에서는 제외)", fsrc="https://www.aljazeera.com/economy/2026/11/19/anthropic-starts-trading-in-the-us-after-blockbuster-ipo")
co("deepmind", "Google DeepMind", "model", "video", "GOOGL", "영국·미국", "Gemini 모델·연구", "Alphabet 자회사", parent="Alphabet")
co("metaai", "Meta AI", "model", "video", "META", "미국", "Llama 모델·연구", "Meta 내부 조직", parent="Meta")
co("cohere", "Cohere", "model", "video", None, "캐나다", "기업용 언어모델", "Nvidia가 여러 라운드에 투자")
co("ai21", "AI21 Labs", "model", "video", None, "이스라엘", "언어모델·기업용 AI", "")
co("alephalpha", "Aleph Alpha", "model", "video", None, "독일", "주권형·기업용 AI", "")
co("deepseek", "DeepSeek", "model", "video", None, "중국", "추론·개방형 가중치 모델", "이번 관계망에서 출처로 확인된 직접 거래 없음")
# 2) 칩·컴퓨팅
co("cerebras", "Cerebras", "chip", "video", None, "미국", "웨이퍼 크기 AI 칩", "OpenAI와 100억 달러 이상 컴퓨팅 계약(2026-01)")
co("groq", "Groq", "chip", "video", None, "미국", "추론 전용 칩(LPU)", "Nvidia가 기술 라이선스·핵심 인력 영입(2025-12)")
co("tenstorrent", "Tenstorrent", "chip", "video", None, "캐나다·미국", "RISC-V 기반 AI 프로세서", "")
co("qualcomm", "Qualcomm", "chip", "video", "QCOM", "미국", "모바일·기기 내 AI 칩", "Figure AI에 투자")
co("sambanova", "SambaNova Systems", "chip", "video", None, "미국", "AI 전용 칩·시스템", "")
co("graphcore", "Graphcore", "chip", "video", None, "영국", "IPU(지능 처리 장치)", "SoftBank 자회사", parent="SoftBank")
co("dmatrix", "d-Matrix", "chip", "video", None, "미국", "추론용 칩", "")
# 3) 응용 서비스
co("perplexity", "Perplexity AI", "app", "video", None, "미국", "AI 검색", "Nvidia가 2023년부터 계속 투자")
co("runway", "Runway", "app", "video", None, "미국", "AI 영상 생성", "Nvidia·Google 투자")
co("synthesia", "Synthesia", "app", "video", None, "영국", "AI 아바타 영상", "")
co("elevenlabs", "ElevenLabs", "app", "video", None, "미국·영국", "AI 음성 생성", "")
co("midjourney", "Midjourney", "app", "video", None, "미국", "AI 이미지 생성", "")
co("characterai", "Character.AI", "app", "video", None, "미국", "대화형 AI 캐릭터", "")
co("glean", "Glean", "app", "video", None, "미국", "기업용 AI 검색", "")
co("gamma", "Gamma", "app", "video", None, "미국", "AI 발표자료·문서", "")
co("lovable", "Lovable", "app", "video", None, "스웨덴", "AI 소프트웨어 제작", "")
# 4) 로봇·자율주행
co("bostondynamics", "Boston Dynamics", "robot", "video", None, "미국", "고성능 로봇", "현대자동차그룹 소유", parent="현대자동차그룹")
co("physicalintelligence", "Physical Intelligence", "robot", "video", None, "미국", "범용 로봇 지능", "")
co("agility", "Agility Robotics", "robot", "video", None, "미국", "작업용 휴머노이드", "")
co("skydio", "Skydio", "robot", "video", None, "미국", "자율 드론", "")
co("waymo", "Waymo", "robot", "video", "GOOGL", "미국", "자율주행", "Alphabet 자회사", parent="Alphabet")
co("tesla", "Tesla", "robot", "video", "TSLA", "미국", "전기차·자율주행·휴머노이드", "")
co("onex", "1X Technologies", "robot", "video", None, "노르웨이·미국", "휴머노이드 로봇", "")
co("sanctuary", "Sanctuary AI", "robot", "video", None, "캐나다", "범용 휴머노이드", "")
co("apptronik", "Apptronik", "robot", "video", None, "미국", "휴머노이드 로봇", "")
# 5) 인프라·특화
co("huggingface", "Hugging Face", "infra", "video", None, "미국·프랑스", "개방형 AI 생태계·모델 허브", "Nvidia 투자")
co("scaleai", "Scale AI", "infra", "video", None, "미국", "AI 학습 데이터·평가", "Meta가 49% 지분 투자(2025-06)")
co("databricks", "Databricks", "infra", "video", None, "미국", "데이터·AI 플랫폼", "Nvidia 투자")
co("snowflake", "Snowflake", "infra", "video", "SNOW", "미국", "클라우드 데이터 플랫폼", "Anthropic과 2억 달러 계약(2025-12)")
co("wandb", "Weights & Biases", "infra", "video", None, "미국", "머신러닝 실험 관리 도구", "CoreWeave가 인수(2025-05)", parent="CoreWeave")
co("langchain", "LangChain", "infra", "video", None, "미국", "AI 응용 개발 프레임워크", "")
co("pinecone", "Pinecone", "infra", "video", None, "미국", "벡터 데이터베이스", "")
co("qdrant", "Qdrant", "infra", "video", None, "독일", "벡터 검색·데이터베이스", "")
co("runpod", "RunPod", "infra", "video", None, "미국", "클라우드 GPU", "")
co("together", "Together AI", "infra", "video", None, "미국", "AI 모델 호스팅·인프라", "Nvidia 투자")

# ---------------------------------------------------------------- 관계(엣지)
# kind: investment(지분 투자), vc(벤처 투자), hardware(칩·하드웨어 구매), services(클라우드·서비스 구매),
#       acquisition(인수·라이선스), ownership(자회사), partnership(제휴·판매 계약)
# 방향: 돈이 나가는 쪽(from) → 받는 쪽(to). 투자는 투자자→피투자사, 구매는 구매자→판매자.
E = []


def ed(a, b, kind, label, date, src, fig=False, approx=False, interp=False):
    # date_approx: 출처에서 일(日)까지 확인하지 못한 날짜(시간 슬라이더용 대략값)
    # interp: Bloomberg 그림의 화살표를 해석한 관계(성격·방향 확인 필요)
    E.append(dict(source=a, target=b, kind=kind, label=label, date=date, src=src, in_figure=fig,
                  date_approx=(src == BLOOMBERG) or approx, interp=interp))


# Bloomberg 그림에 그려진 관계(2025-10 기준)
ed("nvidia", "openai", "investment", "최대 1,000억 달러 투자 의향서(LOI)", "2025-09-22", "https://investor.nvidia.com/news/press-release-details/2025/OpenAI-and-NVIDIA-Announce-Strategic-Partnership-to-Deploy-10-Gigawatts-of-NVIDIA-Systems/", True)
ed("nvidia", "openai", "investment", "300억 달러 지분 투자(1,100억 달러 라운드)", "2026-02-27", "https://builtin.com/articles/openai-raises-110b-730b-valuation-20260227")
ed("openai", "nvidia", "hardware", "Nvidia 시스템 10GW 배치", "2025-09-22", BLOOMBERG, True)
ed("openai", "amd", "hardware", "AMD GPU 6GW", "2025-10-06", "https://ir.amd.com/news-events/press-releases/detail/1260/amd-and-openai-announce-strategic-partnership-to-deploy-6-gigawatts-of-amd-gpus", True)
ed("amd", "openai", "investment", "주식 최대 1억6천만 주 워런트(주식을 살 권리)", "2025-10-06", "https://ir.amd.com/news-events/press-releases/detail/1260/amd-and-openai-announce-strategic-partnership-to-deploy-6-gigawatts-of-amd-gpus", True)
ed("openai", "oracle", "services", "3,000억 달러 클라우드 계약", "2025-09-10", BLOOMBERG, True)
ed("oracle", "nvidia", "hardware", "Nvidia 칩 수백억 달러 구매", "2025-09-10", BLOOMBERG, True)
ed("microsoft", "openai", "investment", "OpenAI 투자", "2019-07-22", BLOOMBERG, True)
ed("openai", "microsoft", "services", "Azure 사용", "2019-07-22", BLOOMBERG, True)
ed("microsoft", "nvidia", "hardware", "GPU 구매", "2023-01-01", BLOOMBERG, True)
ed("microsoft", "coreweave", "services", "GPU 용량 임차", "2023-06-01", BLOOMBERG, True)
ed("microsoft", "nebius", "services", "GPU 인프라 174억 달러", "2025-09-08", "https://www.nasdaq.com/articles/nebius-shares-soar-us-174-billion-microsoft-ai-deal", True)
ed("openai", "coreweave", "services", "컴퓨팅 계약 최대 119억 달러", "2025-03-10", "https://investors.coreweave.com/news/news-details/2025/CoreWeave-Announces-Agreement-with-OpenAI-to-Deliver-AI-Infrastructure", True)
ed("openai", "coreweave", "investment", "CoreWeave 주식 3.5억 달러 취득", "2025-03-10", "https://investors.coreweave.com/news/news-details/2025/CoreWeave-Announces-Agreement-with-OpenAI-to-Deliver-AI-Infrastructure", True)
ed("coreweave", "nvidia", "hardware", "Nvidia 시스템 구매", "2023-01-01", BLOOMBERG, True)
ed("nvidia", "coreweave", "services", "미사용 용량 63억 달러 구매 보증(8-K)", "2025-09-09", "https://www.sec.gov/Archives/edgar/data/1769628/000176962825000047/crwv-20250909.htm", True)
ed("nvidia", "coreweave", "investment", "지분 보유(8-K에 주주로 기재)", "2023-04-10", "https://www.sec.gov/Archives/edgar/data/1769628/000176962825000047/crwv-20250909.htm", True, approx=True)
ed("nvidia", "nebius", "investment", "7억 달러 사모 배정 참여", "2024-12-02", "https://nebius.com/newsroom/nebius-announces-oversubscribed-strategic-equity-financing-of-usd-700-million-to-accelerate-roll-out-of-full-stack-ai-infrastructure", True)
ed("nvidia", "intel", "investment", "보통주 50억 달러", "2025-09-18", "https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-and-Intel-to-Develop-AI-Infrastructure-and-Personal-Computing-Products/", True)
ed("intel", "coreweave", "hardware", "그림 표기: 하드웨어·소프트웨어 거래(성격 확인 필요)", "2025-10-01", BLOOMBERG, True, interp=True)
ed("nvidia", "xai", "vc", "시리즈 C 60억 달러 참여", "2024-12-23", "https://x.ai/news/series-c", True)
ed("amd", "xai", "vc", "시리즈 C 60억 달러 참여", "2024-12-23", "https://x.ai/news/series-c")
ed("nvidia", "xai", "vc", "시리즈 E 200억 달러 참여", "2026-01-06", "https://x.ai/news/series-e")
ed("xai", "nvidia", "hardware", "GPU 구매", "2024-06-01", BLOOMBERG, True)
ed("nvidia", "mistral", "vc", "시리즈 C 참여", "2025-09-09", "https://tech.eu/2025/09/09/mistral-bags-1-7bn-funding-round-as-asml-takes-significant-stake/", True)
ed("mistral", "nvidia", "hardware", "GPU 구매(Mistral Compute)", "2025-06-11", BLOOMBERG, True)
ed("nvidia", "figure", "vc", "시리즈 C 참여", "2025-09-16", "https://siliconangle.com/?p=711441", True)
ed("figure", "nvidia", "hardware", "학습 인프라용 GPU", "2025-09-16", "https://siliconangle.com/2025/09/16/humanoid-robot-startup-figure-raises-1b-39b-valuation/", True)
ed("nvidia", "nscale", "investment", "SAFE(나중에 지분으로 바뀌는 투자 약정) 4.33억 달러 라운드 참여", "2025-10-01", "https://www.bloomberg.com/news/articles/2025-10-01/nscale-raises-433-million-days-after-closing-1-1-billion-round", True)
ed("openai", "nscale", "services", "유럽 데이터센터 용량", "2025-09-16", BLOOMBERG, True)
ed("amd", "nscale", "hardware", "그림 표기: 하드웨어 거래(방향·성격 확인 필요)", "2025-10-01", BLOOMBERG, True, interp=True)
for s in ("harvey", "anysphere", "ambience"):
    ed("openai", s, "vc", "OpenAI 스타트업 펀드 투자", "2024-01-01", BLOOMBERG, True)
    ed(s, "openai", "services", "OpenAI 모델 사용", "2024-01-01", BLOOMBERG, True)

# 그림 밖 관계(영상 기업과 연결) ─ 모두 출처 있음
ed("microsoft", "anthropic", "investment", "최대 50억 달러", "2025-11-18", "https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships")
ed("nvidia", "anthropic", "investment", "최대 100억 달러", "2025-11-18", "https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships")
ed("anthropic", "microsoft", "services", "Azure 300억 달러 구매", "2025-11-18", "https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships")
ed("deepmind", "anthropic", "investment", "Google, 최대 400억 달러 투자(100억 달러 우선, 300억 달러는 성과 조건)", "2026-04-24", "https://www.thestar.com.my/tech/tech-news/2026/04/25/google-plans-to-invest-up-to-40-billion-in-anthropic-bloomberg-news-reports")
ed("anthropic", "deepmind", "services", "Google 맞춤형 칩(TPU)·클라우드 사용", "2026-04-24", "https://www.wam.ae/en/article/176tjwp-google-invest-40-billion-rival-anthropic")
ed("snowflake", "anthropic", "partnership", "2억 달러 다년 계약", "2025-12-03", "https://snowflake.com/en/news/press-releases/snowflake-and-anthropic-announce-200-million-partnership-to-bring-agentic-ai-to-global-enterprises/")
ed("snowflake", "openai", "partnership", "2억 달러 다년 계약", "2026-02-02", "https://investors.snowflake.com/news/news-details/2026/Snowflake-and-OpenAI-Forge-200-Million-Partnership-to-Bring-Enterprise-Ready-AI-to-the-Worlds-Most-Trusted-Data-Platform/default.aspx")
ed("nvidia", "anysphere", "vc", "시리즈 D 참여", "2025-11-13", "https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/")
ed("deepmind", "anysphere", "vc", "Google, 시리즈 D 참여(모델 공급사)", "2025-11-13", "https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/")
ed("openai", "cerebras", "services", "750MW 컴퓨팅, 100억 달러 이상", "2026-01-14", "https://techcrunch.com/2026/01/14/openai-signs-deal-reportedly-worth-10-billion-for-compute-from-cerebras/")
ed("nvidia", "groq", "acquisition", "추론 기술 라이선스·인력 영입(약 200억 달러 보도)", "2025-12-24", "https://techcrunch.com/2025/12/24/nvidia-acquires-ai-chip-challenger-groq-for-20b-report-says/")
ed("metaai", "scaleai", "investment", "Meta, 143억 달러로 49% 지분", "2025-06-12", "https://fortune.com/2025/06/13/meta-scale-ai-alexandr-wang-superintelligence-team/")
ed("coreweave", "wandb", "acquisition", "인수 완료", "2025-05-05", "https://coreweave.com/blog/coreweave-completes-acquisition-of-weights-biases")
ed("intel", "figure", "vc", "Intel Capital, 시리즈 C 참여", "2025-09-16", "https://www.intelcapital.com/?p=11952")
ed("qualcomm", "figure", "vc", "Qualcomm Ventures, 시리즈 C 참여", "2025-09-16", "https://siliconangle.com/?p=711441")
ed("microsoft", "figure", "vc", "시리즈 B 참여", "2024-02-29", "https://finance.yahoo.com/news/figure-valued-39-billion-latest-131115237.html", approx=True)
ed("nvidia", "perplexity", "vc", "2023년 11월부터 여러 라운드 참여", "2023-11-01", "https://techcrunch.com/2025/06/19/nvidias-ai-empire-a-look-at-its-top-startup-investments/", approx=True)
ed("nvidia", "cohere", "vc", "2023년부터 여러 라운드 참여", "2023-06-01", "https://techcrunch.com/2025/10/12/nvidias-ai-empire-a-look-at-its-top-startup-investments", approx=True)
ed("nvidia", "together", "vc", "시리즈 B 참여", "2024-02-01", "https://techcrunch.com/2026/01/02/nvidias-ai-empire-a-look-at-its-top-startup-investments/", approx=True)
ed("nvidia", "runway", "vc", "시리즈 C 확장 참여", "2023-06-01", "https://emeatribune.com/nvidias-ai-empire-a-look-at-its-top-startup-investments", approx=True)
ed("deepmind", "runway", "vc", "Google, 시리즈 C 확장 참여", "2023-06-01", "https://emeatribune.com/nvidias-ai-empire-a-look-at-its-top-startup-investments", approx=True)
ed("nvidia", "huggingface", "vc", "시리즈 D 2.35억 달러 참여", "2023-08-24", "https://techcrunch.com/2023/08/24/hugging-face-raises-235m-from-investors-including-salesforce-and-nvidia")
for _inv in ("deepmind", "amd", "intel", "qualcomm"):
    ed(_inv, "huggingface", "vc", "시리즈 D 2.35억 달러 참여" + (" (Google)" if _inv == "deepmind" else ""), "2023-08-24", "https://techcrunch.com/2023/08/24/hugging-face-raises-235m-from-investors-including-salesforce-and-nvidia")
ed("nvidia", "databricks", "vc", "시리즈 I 참여(전략 투자자)", "2023-09-14", "https://www.databricks.com/de/company/newsroom/press-releases/databricks-raises-series-i-investment-43b-valuation")
ed("nvidia", "scaleai", "vc", "시리즈 F 10억 달러 참여(기존 투자자)", "2024-05-21", "https://www.nbcnews.com/news/rcna153327")
for _inv, _t in (("amd", "AMD Ventures"), ("intel", "Intel Capital"), ("metaai", "Meta")):
    ed(_inv, "scaleai", "vc", f"{_t}, 시리즈 F 참여", "2024-05-21", "https://www.intelcapital.com/?p=10893")
ed("nvidia", "physicalintelligence", "vc", "투자자 명단 포함(라운드 시점 확인 필요)", "2025-11-20", "https://www.revenuememo.com/p/who-owns-physical-intelligence", approx=True)
ed("deepmind", "physicalintelligence", "vc", "Alphabet CapitalG, 6억 달러 라운드 주도", "2025-11-20", "https://dataconomy.com/2025/11/21/bezos-backed-physical-intelligence-raises-600m-at-5-6b-valuation/")
ed("nvidia", "skydio", "vc", "시리즈 E 2.3억 달러 참여(기존 투자자)", "2023-02-27", "https://www.therobotreport.com/skydio-flying-high-with-230m-series-e-funding-round/")
ed("nvidia", "elevenlabs", "vc", "첫 투자(2025년 9월, CEO 공개)", "2025-09-25", "https://www.musicbusinessworldwide.com/ai-audio-startup-elevenlabs-a-rival-to-suno-just-secured-strategic-investment-from-the-worlds-most-valuable-company-nvidia/", approx=True)
ed("deepmind", "waymo", "ownership", "같은 모회사(Alphabet)", "2016-12-13", "https://abc.xyz/", approx=True)

PRIMARY = ("sec.gov", "investor.", "investors.", "ir.amd.com", "openai.com", "anthropic.com", "nvidia.com", "coreweave.com", "x.ai",
           "mistral.ai", "figure.ai", "snowflake.com", "nebius.com", "intelcapital.com", "databricks.com", "skydio.com", "elevenlabs.io",
           "oracle.com", "blogs.microsoft.com", "abc.xyz")
SECONDARY = ("applescoop", "benzinga.com/markets/tech/26/07", "dealroom.co", "emeatribune", "mexc.com", "sacra.com", "multiples.vc",
             "vlsi.kr", "dailysift", "fierce-network.com/cloud/fierce-networks-encyclopedia", "revenuememo", "useluminix", "247wallst")


def tier(url: str) -> str:
    if url == BLOOMBERG:
        return "그림"
    if any(k in url for k in PRIMARY):
        return "1차"
    if any(k in url for k in SECONDARY):
        return "보조"
    return "언론"


for _e in E:
    _e["tier"] = tier(_e["src"])
for _e in EVENTS:
    _e["tier"] = tier(_e["src"])
    _e.setdefault("recent", False)
for _c in C:
    _c["ftier"] = tier(_c["fsrc"]) if _c.get("fsrc") else None

json_dump = lambda name, obj: (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1))
json_dump("events.json", EVENTS)
json_dump("private_valuations.json", {k: [dict(date=d, value_bn=v, note=n, src=s, tier=tier(s)) for d, v, n, s in rows] for k, rows in PRIVATE.items()})
json_dump("companies.json", C)
json_dump("edges.json", E)
ids = {c["id"] for c in C}
bad = [e for e in E if e["source"] not in ids or e["target"] not in ids]
assert not bad, bad
print(len(C), "companies;", len(E), "edges;", len(EVENTS), "events")
from collections import Counter
print("edge tiers", Counter(e["tier"] for e in E), "| approx", sum(e["date_approx"] for e in E))
print("event tiers", Counter(e["tier"] for e in EVENTS))
print("groups", {g: sum(c["group"] == g for c in C) for g in ("image", "both", "video")})
