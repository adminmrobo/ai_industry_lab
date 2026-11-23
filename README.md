# AI 산업 연구실 (ai_industry_lab)

Bloomberg의 「How Nvidia and OpenAI Fuel the AI Money Machine」(2025-10) 그림을 기준점으로,
AI 기업에 돈이 몰리는 길을 **주가 → 회사 간 관계망 → 거시환경·현금흐름** 세 겹으로 읽는 대시보드입니다.

**사이트: https://adminmrobo.github.io/ai_industry_lab/**

| 페이지 | 내용 |
|---|---|
| `index.html` | 개요와 읽는 원칙 |
| `stage1.html` | ① 기준시점(2025-10-07) ±3개월, 그림 속 7개 상장사 주가 · 거래 발표 15건의 초과 수익률 · 비상장사 기업가치 계단 |
| `stage2.html` | ② 영상 「50 AI Companies You Should Know」 42개사 + 그림 15개사 = 57개사 사업·특징 표 · 층 간 연결 행렬 · 정적 가치사슬 지도 · 움직이는 관계망 |
| `stage3.html` | ③ 현재 주가·컨센서스 · 개별/기업군 3D 궤적(거시 변수 × 주가) · 롤링 상관 곡면 · 월간 상관 행렬 · 기업 현금흐름 · 연준 Z.1 자금 부족 |

## 데이터 흐름

```
GitHub Actions (평일 22:17 UTC)
  └ scripts/fetch_data.py      Yahoo Finance(주가·컨센서스·현금흐름), FRED(거시·Z.1) → data/*.csv, *.json
  └ scripts/static_data.py     거래 발표일·비상장 기업가치·57개사·관계(출처 포함) → data/static/*.json
  └ scripts/build_site_data.py 페이지용 계산(지수화·초과 수익률·상관·궤적) → data/site/*.json
```

- 거래·관계 데이터를 고치려면 `scripts/static_data.py`를 수정하고 커밋하면 됩니다(워크플로가 다시 계산).
- 컨센서스는 `data/consensus_history/날짜.json`으로 날마다 쌓입니다.
- 차트 라이브러리(Plotly 2.35.2, D3 7.9.0)는 `assets/vendor/`에 들어 있어 외부 CDN이 필요 없습니다.

## 방법 메모

- 초과 수익률: 시장모형(반응일 130~11거래일 전 120일로 α·β 추정, 나스닥100 기준)과 단순 차감을 함께 제공.
- 월간 상관: 수익률 vs 거시 변수 변화, 표본 18개월 미만은 비움, 피셔 z로 5% 유의 표시(*).
- 컨센서스 상승 여력은 중앙값을 기본으로, 평균은 보조로 표시.
- 관계 날짜: 출처에서 일(日)까지 확인한 것만 '확인', 나머지는 '대략'. Bloomberg 그림 화살표를 해석한 관계는 '그림 해석'.

## 원칙

1. 관계의 이력이지 인과가 아니다.
2. 수준보다 변화로 비교한다(상관은 수익률·변화량 기준).
3. 출처가 있는 관계만 그린다.
4. 평가 변동은 현금이 아니다.

함께 보면 좋은 글: [현금흐름 연구실](https://adminmrobo.github.io/cashflow-lab/) · [돈의 경맥](https://adminmrobo.github.io/fof-money-meridian-/)

글 · 안상선 ((주)M-Robo 대표) · 교육·연구용 자료이며 투자 권유가 아닙니다.
