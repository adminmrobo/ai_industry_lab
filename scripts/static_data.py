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
         title="Oracle 1분기 실적: 잔여이행의무(RPO) 4,550억 달러, 359% 증가",
         note="장 마감 뒤 발표", src="https://www.oracle.com/ae/news/announcement/q1fy26-earnings-release-2025-09-09/"),
    dict(date="2025-09-09", react="2025-09-09", tickers=["NVDA"], kind="vc",
         title="Mistral 시리즈 C 17억 유로(ASML 주도, Nvidia 참여)",
         note="", src="https://tech.eu/2025/09/09/mistral-bags-1-7bn-funding-round-as-asml-takes-significant-stake/"),
    dict(date="2025-09-15", react="2025-09-15", tickers=["CRWV", "NVDA"], kind="services",
         title="Nvidia, CoreWeave 미사용 용량 63억 달러 구매 보증(2032년 4월까지)",
         note="공시 시점 기준(9월 중순)", src="https://applescoop.org/story/ai-circular-money-nvidia-openai-deals-explained"),
    dict(date="2025-09-16", react="2025-09-16", tickers=["NVDA", "INTC"], kind="vc",
         title="Figure AI 시리즈 C, 기업가치 390억 달러(Nvidia·Intel Capital 참여)",
         note="", src="https://figure.ai/news/series-c"),
    dict(date="2025-09-18", react="2025-09-18", tickers=["NVDA", "INTC"], kind="investment",
         title="Nvidia, Intel 보통주 50억 달러 매입·공동 개발 발표",
         note="", src="https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-and-Intel-to-Develop-AI-Infrastructure-and-Personal-Computing-Products/"),
    dict(date="2025-09-22", react="2025-09-22", tickers=["NVDA", "ORCL", "MSFT"], kind="investment",
         title="Nvidia–OpenAI 의향서: 최대 1,000억 달러 투자·10GW 배치",
         note="정식 계약은 체결되지 않았다는 후속 보도가 있음", src="https://dailysift.briefvane.com/2026/09/circular-ai-deals-explained.html"),
    dict(date="2025-10-02", react="2025-10-02", tickers=[], kind="investment",
         title="OpenAI 직원 지분 매각, 기업가치 5,000억 달러",
         note="상장사 반응 대상 아님(비상장 기업가치 기준점)", src="https://www.bloomberg.com/news/articles/2025-10-02/openai-completes-share-sale-at-record-500-billion-valuation"),
    dict(date="2025-10-06", react="2025-10-06", tickers=["AMD"], kind="hardware",
         title="AMD–OpenAI 6GW GPU 공급 + OpenAI에 AMD 주식 최대 1억6천만 주 워런트",
         note="", src="https://www.vlsi.kr/en/ai-circular-investment-loop-en/"),
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
         note="발표 시각 불명확, 다음 거래일 기준", src="https://multiples.vc/private-comps/xai"),
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
        ("2025-03-28", 113, "X와 합병 당시", "https://www.mexc.com/news/509538"),
        ("2026-01-06", 230, "시리즈 E 200억 달러", "https://sacra.com/c/xai/"),
        ("2026-02-02", 250, "SpaceX에 주식 교환 방식으로 인수", "https://sacra.com/c/xai/"),
    ],
    "Figure AI": [
        ("2024-02-29", 2.6, "시리즈 B 6.75억 달러", "https://finance.yahoo.com/news/figure-valued-39-billion-latest-131115237.html"),
        ("2025-09-16", 39, "시리즈 C 10억 달러 이상", "https://figure.ai/news/series-c"),
    ],
    "Anysphere(Cursor)": [
        ("2025-06-05", 9.9, "시리즈 C 9억 달러", "https://finance.yahoo.com/news/anysphere-secures-900m-funding-083823106.html"),
        ("2025-11-13", 29.3, "시리즈 D 23억 달러", "https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/"),
        ("2026-07-15", 50, "후속 라운드(7월 발표)", "https://dealroom.co/news/138472-cursor-hits-50b-valuation-in-quick-re-raise/"),
    ],
    "Mistral AI": [
        ("2024-06-11", 6.0, "6.4억 달러 라운드", "https://siliconangle.com/2025/09/09/mistral-ai-raises-2b-led-chip-equipment-maker-asml-14b-valuation/"),
        ("2025-09-09", 13.7, "시리즈 C 17억 유로(117억 유로)", "https://mistral.ai/fr/news/mistral-ai-raises-1-7-b-to-accelerate-technological-progress-with-ai"),
    ],
}

# ---------------------------------------------------------------- 기업(57개)
# layer: bigtech, chip, cloud, model, app, robot, infra
# group: image(그림만), both(그림+영상), video(영상만)
C = []


def co(cid, name, layer, group, ticker, country, business, feature, parent=None):
    C.append(dict(id=cid, name=name, layer=layer, group=group, ticker=ticker, country=country,
                  business=business, feature=feature, parent=parent))


# 그림(Bloomberg) 15개사 ─ 이 가운데 8개사는 영상에도 나온다
co("openai", "OpenAI", "model", "both", None, "미국", "ChatGPT와 GPT 계열 모델 개발·판매", "그림의 중심. 칩·클라우드 회사와 대규모 장기 계약을 맺고, 스타트업에는 투자도 한다")
co("microsoft", "Microsoft", "bigtech", "image", "MSFT", "미국", "Azure 클라우드·오피스·윈도우", "OpenAI 최대 투자자이자 클라우드 공급자. 네오클라우드(CoreWeave·Nebius)에서 용량을 사 온다")
co("nvidia", "NVIDIA", "chip", "both", "NVDA", "미국", "AI 학습·추론용 GPU와 시스템", "칩을 파는 쪽이면서 고객사에 투자하는 쪽. 순환 거래 논쟁의 한가운데")
co("amd", "AMD", "chip", "both", "AMD", "미국", "GPU(Instinct)·CPU", "OpenAI에 GPU를 공급하고 자사 주식 워런트를 대가로 줌")
co("intel", "Intel", "chip", "both", "INTC", "미국", "CPU·파운드리", "Nvidia가 50억 달러 지분 투자. 미국 정부도 지분 보유")
co("oracle", "Oracle", "cloud", "image", "ORCL", "미국", "데이터베이스·OCI 클라우드", "OpenAI와 3,000억 달러 클라우드 계약. 설비투자를 빚으로 메우는 구조가 쟁점")
co("coreweave", "CoreWeave", "cloud", "image", "CRWV", "미국", "GPU 전문 클라우드(네오클라우드)", "Nvidia가 주주이자 용량 구매 보증자. 2025년 3월 상장")
co("nebius", "Nebius", "cloud", "image", "NBIS", "네덜란드", "GPU 전문 클라우드", "Microsoft와 최대 194억 달러 계약. Yandex에서 분리")
co("nscale", "Nscale", "cloud", "image", None, "영국", "유럽 AI 데이터센터·GPU 클라우드", "Nvidia가 투자, OpenAI가 서비스 고객")
co("xai", "xAI", "model", "both", None, "미국", "Grok 모델", "2026년 2월 SpaceX에 인수", parent="SpaceX")
co("mistral", "Mistral AI", "model", "both", None, "프랑스", "개방형 가중치 언어모델", "유럽 대표 모델 회사. ASML이 최대주주, Nvidia도 투자")
co("figure", "Figure AI", "robot", "both", None, "미국", "범용 휴머노이드 로봇", "Nvidia·Intel·Qualcomm 등 칩 회사가 함께 투자")
co("harvey", "Harvey", "app", "both", None, "미국", "법률 전문 AI", "OpenAI 스타트업 펀드 투자처")
co("anysphere", "Anysphere(Cursor)", "app", "image", None, "미국", "AI 코드 편집기 Cursor", "Nvidia·Google이 2025년 11월 투자 참여")
co("ambience", "Ambience Healthcare", "app", "image", None, "미국", "의료 기록 자동화 AI", "OpenAI 스타트업 펀드 투자처")

# 영상(50 AI Companies) 중 그림에 없는 42개사
# 1) 프런티어 모델
co("anthropic", "Anthropic", "model", "video", None, "미국", "Claude 모델", "Google·Amazon·Microsoft·Nvidia가 모두 투자. 그림이 나온 뒤 순환 고리에 합류")
co("deepmind", "Google DeepMind", "model", "video", "GOOGL", "영국·미국", "Gemini 모델·연구", "Alphabet 자회사", parent="Alphabet")
co("metaai", "Meta AI", "model", "video", "META", "미국", "Llama 모델·연구", "Meta 내부 조직", parent="Meta")
co("cohere", "Cohere", "model", "video", None, "캐나다", "기업용 언어모델", "Nvidia가 여러 라운드에 투자")
co("ai21", "AI21 Labs", "model", "video", None, "이스라엘", "언어모델·기업용 AI", "")
co("alephalpha", "Aleph Alpha", "model", "video", None, "독일", "주권형·기업용 AI", "")
co("deepseek", "DeepSeek", "model", "video", None, "중국", "추론·개방형 가중치 모델", "미국 자본 고리와 직접 연결이 거의 없음")
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


def ed(a, b, kind, label, date, src, fig=False):
    # 그림 출처만 있는 관계의 날짜는 시간 슬라이더용 대략값이다
    E.append(dict(source=a, target=b, kind=kind, label=label, date=date, src=src, in_figure=fig,
                  date_approx=(src == BLOOMBERG)))


# Bloomberg 그림에 그려진 관계(2025-10 기준)
ed("nvidia", "openai", "investment", "최대 1,000억 달러 투자 의향", "2025-09-22", BLOOMBERG, True)
ed("openai", "nvidia", "hardware", "Nvidia 시스템 10GW 배치", "2025-09-22", BLOOMBERG, True)
ed("openai", "amd", "hardware", "AMD GPU 6GW", "2025-10-06", BLOOMBERG, True)
ed("amd", "openai", "investment", "주식 최대 1억6천만 주 워런트", "2025-10-06", BLOOMBERG, True)
ed("openai", "oracle", "services", "3,000억 달러 클라우드 계약", "2025-09-10", BLOOMBERG, True)
ed("oracle", "nvidia", "hardware", "Nvidia 칩 수백억 달러 구매", "2025-09-10", BLOOMBERG, True)
ed("microsoft", "openai", "investment", "OpenAI 투자", "2019-07-22", BLOOMBERG, True)
ed("openai", "microsoft", "services", "Azure 사용", "2019-07-22", BLOOMBERG, True)
ed("microsoft", "nvidia", "hardware", "GPU 구매", "2023-01-01", BLOOMBERG, True)
ed("microsoft", "coreweave", "services", "GPU 용량 임차", "2023-06-01", BLOOMBERG, True)
ed("microsoft", "nebius", "services", "GPU 인프라 174억 달러", "2025-09-08", "https://www.nasdaq.com/articles/nebius-shares-soar-us-174-billion-microsoft-ai-deal", True)
ed("openai", "coreweave", "services", "컴퓨팅 계약 119억 달러+", "2025-03-10", "https://www.fierce-network.com/cloud/fierce-networks-encyclopedia-ai-deals", True)
ed("coreweave", "nvidia", "hardware", "Nvidia 시스템 구매", "2023-01-01", BLOOMBERG, True)
ed("nvidia", "coreweave", "services", "미사용 용량 63억 달러 구매 보증", "2025-09-15", "https://applescoop.org/story/ai-circular-money-nvidia-openai-deals-explained", True)
ed("nvidia", "coreweave", "investment", "지분 보유(상장 전부터)", "2023-04-01", "https://applescoop.org/story/ai-circular-money-nvidia-openai-deals-explained", True)
ed("nvidia", "nebius", "investment", "지분 투자", "2024-12-02", BLOOMBERG, True)
ed("nvidia", "intel", "investment", "보통주 50억 달러", "2025-09-18", "https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-and-Intel-to-Develop-AI-Infrastructure-and-Personal-Computing-Products/", True)
ed("intel", "coreweave", "hardware", "그림 표기: 하드웨어·소프트웨어 거래", "2025-10-01", BLOOMBERG, True)
ed("nvidia", "xai", "vc", "xAI 라운드 참여", "2024-12-01", "https://www.benzinga.com/markets/tech/26/07/60713664/nvidia-funds-ai-frenzy-timeline-of-its-circular-financing-deals-so-far", True)
ed("xai", "nvidia", "hardware", "GPU 구매", "2024-06-01", BLOOMBERG, True)
ed("nvidia", "mistral", "vc", "시리즈 C 참여", "2025-09-09", "https://tech.eu/2025/09/09/mistral-bags-1-7bn-funding-round-as-asml-takes-significant-stake/", True)
ed("mistral", "nvidia", "hardware", "GPU 구매(Mistral Compute)", "2025-06-11", BLOOMBERG, True)
ed("nvidia", "figure", "vc", "시리즈 C 참여", "2025-09-16", "https://siliconangle.com/?p=711441", True)
ed("figure", "nvidia", "hardware", "학습 인프라용 GPU", "2025-09-16", "https://siliconangle.com/2025/09/16/humanoid-robot-startup-figure-raises-1b-39b-valuation/", True)
ed("nvidia", "nscale", "investment", "SAFE 4.33억 달러 라운드 참여", "2025-10-01", "https://www.benzinga.com/markets/tech/26/07/60713664/nvidia-funds-ai-frenzy-timeline-of-its-circular-financing-deals-so-far", True)
ed("openai", "nscale", "services", "유럽 데이터센터 용량", "2025-09-16", BLOOMBERG, True)
ed("amd", "nscale", "hardware", "그림 표기: 하드웨어 거래", "2025-10-01", BLOOMBERG, True)
for s in ("harvey", "anysphere", "ambience"):
    ed("openai", s, "vc", "OpenAI 스타트업 펀드 투자", "2024-01-01", BLOOMBERG, True)
    ed(s, "openai", "services", "OpenAI 모델 사용", "2024-01-01", BLOOMBERG, True)

# 그림 밖 관계(영상 기업과 연결) ─ 모두 출처 있음
ed("microsoft", "anthropic", "investment", "최대 50억 달러", "2025-11-18", "https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships")
ed("nvidia", "anthropic", "investment", "최대 100억 달러", "2025-11-18", "https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships")
ed("anthropic", "microsoft", "services", "Azure 300억 달러 구매", "2025-11-18", "https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships")
ed("deepmind", "anthropic", "investment", "Google, 최대 400억 달러 투자 약정(모회사 Alphabet)", "2026-04-24", "https://pq-cybarg.github.io/bubble-map/r-fin-google-amazon-anthropic-meta.html")
ed("anthropic", "deepmind", "services", "Google TPU·클라우드 사용(모회사 Alphabet)", "2026-04-24", "https://pq-cybarg.github.io/bubble-map/r-fin-google-amazon-anthropic-meta.html")
ed("snowflake", "anthropic", "partnership", "2억 달러 다년 계약", "2025-12-03", "https://snowflake.com/en/news/press-releases/snowflake-and-anthropic-announce-200-million-partnership-to-bring-agentic-ai-to-global-enterprises/")
ed("snowflake", "openai", "partnership", "2억 달러 다년 계약", "2026-02-02", "https://techcrunch.com/?p=3088754")
ed("nvidia", "anysphere", "vc", "시리즈 D 참여", "2025-11-13", "https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/")
ed("deepmind", "anysphere", "vc", "Google, 시리즈 D 참여(모델 공급사)", "2025-11-13", "https://www.techcrunch.com/2025/11/13/coding-assistant-cursor-raises-2-3b-5-months-after-its-previous-round/")
ed("openai", "cerebras", "services", "750MW 컴퓨팅, 100억 달러 이상", "2026-01-14", "https://techcrunch.com/2026/01/14/openai-signs-deal-reportedly-worth-10-billion-for-compute-from-cerebras/")
ed("nvidia", "groq", "acquisition", "추론 기술 라이선스·인력 영입(약 200억 달러 보도)", "2025-12-24", "https://techcrunch.com/2025/12/24/nvidia-acquires-ai-chip-challenger-groq-for-20b-report-says/")
ed("metaai", "scaleai", "investment", "Meta, 143억 달러로 49% 지분", "2025-06-12", "https://fortune.com/2025/06/13/meta-scale-ai-alexandr-wang-superintelligence-team/")
ed("coreweave", "wandb", "acquisition", "인수 완료", "2025-05-05", "https://coreweave.com/blog/coreweave-completes-acquisition-of-weights-biases")
ed("intel", "figure", "vc", "Intel Capital, 시리즈 C 참여", "2025-09-16", "https://www.intelcapital.com/?p=11952")
ed("qualcomm", "figure", "vc", "Qualcomm Ventures, 시리즈 C 참여", "2025-09-16", "https://siliconangle.com/?p=711441")
ed("microsoft", "figure", "vc", "시리즈 B 참여", "2024-02-29", "https://finance.yahoo.com/news/figure-valued-39-billion-latest-131115237.html")
ed("nvidia", "perplexity", "vc", "2023년부터 여러 라운드 참여", "2023-11-01", "https://techcrunch.com/2025/06/19/nvidias-ai-empire-a-look-at-its-top-startup-investments/")
ed("nvidia", "cohere", "vc", "2023년부터 여러 라운드 참여", "2023-06-01", "https://techcrunch.com/2025/10/12/nvidias-ai-empire-a-look-at-its-top-startup-investments")
ed("nvidia", "together", "vc", "시리즈 B 참여", "2024-02-01", "https://techcrunch.com/2026/01/02/nvidias-ai-empire-a-look-at-its-top-startup-investments/")
ed("nvidia", "runway", "vc", "시리즈 C 확장 참여", "2023-06-29", "https://emeatribune.com/nvidias-ai-empire-a-look-at-its-top-startup-investments")
ed("deepmind", "runway", "vc", "Google, 시리즈 C 확장 참여", "2023-06-29", "https://emeatribune.com/nvidias-ai-empire-a-look-at-its-top-startup-investments")
ed("nvidia", "huggingface", "vc", "지분 투자", "2023-08-24", "https://blogs.nvidia.com/blog/nvidia-investments/")
ed("nvidia", "databricks", "vc", "지분 투자", "2023-09-14", "https://blogs.nvidia.com/blog/nvidia-investments/")
ed("nvidia", "scaleai", "vc", "지분 투자", "2024-05-21", "https://www.businessinsider.nl/ai-startup-founders-discuss-what-its-like-to-be-a-part-of-nvidias-sprawling-startup-empire/")
ed("nvidia", "physicalintelligence", "vc", "포트폴리오 포함", "2024-11-04", "https://dealroom.co/investors/nvidia/")
ed("nvidia", "skydio", "vc", "포트폴리오 포함", "2024-01-01", "https://dealroom.co/investors/nvidia/")
ed("nvidia", "elevenlabs", "vc", "투자자 그룹에 포함", "2025-01-30", "https://dealroom.co/investors/nvidia/")
ed("deepmind", "waymo", "ownership", "같은 모회사(Alphabet)", "2016-12-13", "https://abc.xyz/")

json_dump = lambda name, obj: (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1))
json_dump("events.json", EVENTS)
json_dump("private_valuations.json", {k: [dict(date=d, value_bn=v, note=n, src=s) for d, v, n, s in rows] for k, rows in PRIVATE.items()})
json_dump("companies.json", C)
json_dump("edges.json", E)
ids = {c["id"] for c in C}
bad = [e for e in E if e["source"] not in ids or e["target"] not in ids]
assert not bad, bad
print(len(C), "companies;", len(E), "edges;", len(EVENTS), "events")
print("groups", {g: sum(c["group"] == g for c in C) for g in ("image", "both", "video")})
