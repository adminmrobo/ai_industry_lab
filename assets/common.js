/* ai_industry_lab 공통 스크립트 */
const PAL = { s1: "#2a78d6", s2: "#eb6834", s3: "#1baf7a", s4: "#eda100", s5: "#e87ba4", s6: "#008300", s7: "#6250d6", s8: "#e34948" };
const INK = { t1: "#0b0b0b", t2: "#52514e", t3: "#7a7974", grid: "#eeede8", line: "#e6e5e0", neutral: "#8a8984" };

// 색은 회사를 따라간다(순위·필터와 무관하게 고정)
const TICKER_COLOR = { NVDA: PAL.s1, MSFT: PAL.s2, AMD: PAL.s3, ORCL: PAL.s4, INTC: PAL.s5, CRWV: PAL.s6, NBIS: PAL.s7 };
// 영상 기업(그림의 순환 고리 바깥)은 회색 계열 + 직접 라벨로 구분
const OUTSIDE_COLOR = "#6b6a65";
const BENCH_COLOR = "#9c9b96";
const colorOf = (t) => TICKER_COLOR[t] || (t && t.startsWith("^") ? BENCH_COLOR : OUTSIDE_COLOR);

const fmt = {
  pct: (v, d = 1) => (v == null ? "–" : (v > 0 ? "+" : "") + v.toFixed(d) + "%"),
  num: (v, d = 0) => (v == null ? "–" : v.toLocaleString("ko-KR", { maximumFractionDigits: d, minimumFractionDigits: d })),
  usd: (v, d = 2) => (v == null ? "–" : "$" + v.toLocaleString("en-US", { maximumFractionDigits: d, minimumFractionDigits: d })),
  // v: 십억 달러 단위 → 한국어 표기(10억 달러 = 1B, 1조 달러 = 1T)
  bn: (v) => (v == null ? "–" : Math.abs(v) >= 1000 ? (v / 1000).toFixed(2) + "조 달러" : (v * 10).toLocaleString("ko-KR", { maximumFractionDigits: 0 }) + "억 달러"),
};
const cls = (v) => (v == null ? "" : v > 0 ? "pos" : v < 0 ? "neg" : "");

async function loadJSON(path) {
  const r = await fetch(path + "?v=" + Date.now().toString().slice(0, -5));
  if (!r.ok) throw new Error(path + " " + r.status);
  return r.json();
}

// Plotly 공통 레이아웃: 얇은 선, 옅은 격자, 한 개의 y축
function baseLayout(extra = {}) {
  return Object.assign({
    font: { family: "Pretendard Variable, Pretendard, sans-serif", size: 13, color: INK.t1 },
    paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
    margin: { l: 56, r: 24, t: 16, b: 44 },
    hovermode: "x unified",
    hoverlabel: { bgcolor: "#fff", bordercolor: INK.line, font: { color: INK.t1, size: 13 } },
    xaxis: { gridcolor: INK.grid, linecolor: INK.line, tickfont: { color: INK.t2 }, zeroline: false },
    yaxis: { gridcolor: INK.grid, linecolor: INK.line, tickfont: { color: INK.t2 }, zeroline: false },
    legend: { orientation: "h", y: -0.18, font: { size: 12, color: INK.t2 } },
  }, extra);
}
const PCONF = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"] };

function setUpdated(el, meta) {
  if (!el || !meta) return;
  const t = new Date(meta.fetched_at_utc);
  const kst = t.toLocaleString("ko-KR", { timeZone: "Asia/Seoul", hour12: false });
  el.textContent = `데이터 갱신: ${kst} (한국 시간) · 주가 마지막 거래일 ${meta.price_last}`;
}

// 표 정렬(헤더 클릭)
function sortableTable(table) {
  table.querySelectorAll("th").forEach((th, i) => {
    th.addEventListener("click", () => {
      const rows = [...table.tBodies[0].rows];
      const asc = th.dataset.asc !== "1";
      table.querySelectorAll("th").forEach((x) => delete x.dataset.asc);
      th.dataset.asc = asc ? "1" : "0";
      rows.sort((a, b) => {
        const x = a.cells[i].dataset.v ?? a.cells[i].textContent, y = b.cells[i].dataset.v ?? b.cells[i].textContent;
        const nx = parseFloat(x), ny = parseFloat(y);
        const c = !isNaN(nx) && !isNaN(ny) ? nx - ny : String(x).localeCompare(String(y), "ko");
        return asc ? c : -c;
      });
      rows.forEach((r) => table.tBodies[0].appendChild(r));
    });
  });
}

function el(tag, attrs = {}, html = "") {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  e.innerHTML = html;
  return e;
}

// 상단 메뉴
function siteHeader(active) {
  const items = [["index.html", "개요"], ["stage1.html", "① 기준시점 ±3개월"], ["stage2.html", "② 50개사·관계망"], ["stage3.html", "③ 거시·현금흐름 3D"]];
  const h = document.querySelector("header.site .in nav");
  if (!h) return;
  h.innerHTML = items.map(([href, t]) => `<a href="${href}" class="${href === active ? "on" : ""}">${t}</a>`).join("");
}

const MOBILE = window.innerWidth < 600;
const REC_KO = { strong_buy: "강력 매수", buy: "매수", hold: "보유", underperform: "비중 축소", sell: "매도", none: "의견 없음" };
const recKo = (k) => REC_KO[k] || k || "–";

// 용어 풀이 상자: [[용어, 풀이], ...]
function glossary(id, items, title = "이 페이지의 용어 풀이") {
  const box = document.getElementById(id);
  if (!box) return;
  box.innerHTML = `<details class="gloss"><summary>${title} (${items.length}개)</summary><dl>${items.map(([t, d]) => `<dt>${t}</dt><dd>${d}</dd>`).join("")}</dl></details>`;
}
// 자동 요약 3줄
function autoSummary(id, lines) {
  const box = document.getElementById(id);
  if (box) box.innerHTML = `<div class="t">이 페이지에서 보이는 것 (데이터로 자동 작성)</div><ol>${lines.map((l) => `<li>${l}</li>`).join("")}</ol>`;
}
function median(a) { const v = a.filter((x) => x != null).sort((x, y) => x - y); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; }
