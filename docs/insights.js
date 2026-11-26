/**
 * Ecosystem Insights visualization panel & Side-by-Side Tool Comparison drawer.
 */

import { computeHistoryTrendSummary, formatCompactNumber, getStatusLabel } from "./catalog-logic.js";

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function renderBarList(title, items, maxVal) {
  const card = el("div", "insight-card");
  card.append(el("h3", "insight-title", title));
  const list = el("div", "bar-list");
  for (const item of items) {
    const row = el("div", "bar-row");
    const head = el("div", "bar-row-head");
    head.append(el("span", "", item.label), el("strong", "", String(item.value)));
    const track = el("div", "bar-track");
    const fill = el("div", "bar-fill");
    const pct = maxVal > 0 ? Math.max(6, Math.round((item.value / maxVal) * 100)) : 0;
    fill.style.width = `${pct}%`;
    track.append(fill);
    row.append(head, track);
    list.append(row);
  }
  card.append(list);
  return card;
}

export function renderInsightsPanel(mountEl, bundle, lang) {
  if (!mountEl || !bundle) return;
  const wasOpen = mountEl.querySelector(".insights-details")?.open ?? false;
  mountEl.hidden = false;
  mountEl.textContent = "";

  const details = el("details", "insights-details");
  details.open = wasOpen;
  const summary = el(
    "summary",
    "insights-summary",
    lang === "zh" ? "📊 生态洞察与技术分布（点击展开）" : "📊 Ecosystem Insights & Distribution (Expand)"
  );
  details.append(summary);

  const grid = el("div", "insights-grid");

  // 1. Category counts
  const catCounts = {};
  for (const tool of bundle.tools) {
    catCounts[tool.category] = (catCounts[tool.category] || 0) + 1;
  }
  const catItems = bundle.categories.map((c) => ({
    label: `${c.icon} ${lang === "zh" ? c.name_zh : c.name_en}`,
    value: catCounts[c.id] || 0,
  }));
  const maxCat = Math.max(1, ...catItems.map((i) => i.value));
  grid.append(renderBarList(lang === "zh" ? "分类分布" : "By Category", catItems, maxCat));

  // 2. Top languages
  const langs = (bundle.summary.by_language || []).slice(0, 6).map((x) => ({
    label: x.name,
    value: x.count,
  }));
  const maxLang = Math.max(1, ...langs.map((i) => i.value));
  grid.append(renderBarList(lang === "zh" ? "主力开发语言" : "Primary Languages", langs, maxLang));

  // 3. Health score buckets
  const buckets =
    lang === "zh"
      ? [
          { label: "90-100 (卓越)", value: 0 },
          { label: "75-89 (良好)", value: 0 },
          { label: "50-74 (一般)", value: 0 },
          { label: "<50 (待复查)", value: 0 },
        ]
      : [
          { label: "90-100 (Elite)", value: 0 },
          { label: "75-89 (Strong)", value: 0 },
          { label: "50-74 (Moderate)", value: 0 },
          { label: "<50 (Needs Review)", value: 0 },
        ];
  for (const tool of bundle.tools) {
    const sc = tool.telemetry?.health_score;
    if (typeof sc !== "number") continue;
    if (sc >= 90) buckets[0].value++;
    else if (sc >= 75) buckets[1].value++;
    else if (sc >= 50) buckets[2].value++;
    else buckets[3].value++;
  }
  const maxB = Math.max(1, ...buckets.map((b) => b.value));
  grid.append(renderBarList(lang === "zh" ? "健康度评分分布" : "Health Score Distribution", buckets, maxB));

  // 4. 90-Day Ecosystem Trend SVG Sparkline (if >= 2 history entries)
  const trend = computeHistoryTrendSummary(bundle.history);
  if (trend.points.length >= 2) {
    const trendCard = el("div", "insight-card");
    trendCard.append(el("h3", "insight-title", lang === "zh" ? "生态增长趋势" : "90-Day Ecosystem Trend"));
    const wrap = el("div", "trend-chart");

    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("class", "trend-svg");
    svg.setAttribute("viewBox", "0 0 240 64");
    svg.setAttribute("role", "img");
    svg.setAttribute(
      "aria-label",
      lang === "zh" ? "生态合计 Stars 历史增长折线图" : "Combined GitHub stars historical trend chart"
    );

    const baseline = document.createElementNS(ns, "line");
    baseline.setAttribute("x1", "0");
    baseline.setAttribute("y1", "56");
    baseline.setAttribute("x2", "240");
    baseline.setAttribute("y2", "56");
    baseline.setAttribute("stroke", "currentColor");
    baseline.setAttribute("stroke-opacity", "0.18");
    baseline.setAttribute("stroke-width", "1");
    svg.append(baseline);

    const polyline = document.createElementNS(ns, "polyline");
    polyline.setAttribute("fill", "none");
    polyline.setAttribute("stroke", "var(--accent)");
    polyline.setAttribute("stroke-width", "2.5");
    polyline.setAttribute("stroke-linecap", "round");
    polyline.setAttribute("stroke-linejoin", "round");
    polyline.setAttribute("points", trend.starPolyline);
    svg.append(polyline);

    const pts = trend.starPolyline.split(" ");
    const lastPt = pts[pts.length - 1]?.split(",");
    if (lastPt && lastPt.length === 2) {
      const dot = document.createElementNS(ns, "circle");
      dot.setAttribute("cx", lastPt[0]);
      dot.setAttribute("cy", lastPt[1]);
      dot.setAttribute("r", "3.5");
      dot.setAttribute("fill", "var(--accent-strong)");
      svg.append(dot);
    }

    const starSign = trend.starDelta >= 0 ? "+" : "-";
    const toolSign = trend.toolDelta >= 0 ? "+" : "-";
    const starText = `${starSign}${formatCompactNumber(Math.abs(trend.starDelta))} ★`;
    const toolText = `${toolSign}${Math.abs(trend.toolDelta)} ${lang === "zh" ? "工具" : "tools"}`;

    const metaTop = el("div", "trend-meta");
    const deltaEl = el("span", `trend-delta${trend.starDelta < 0 ? " is-negative" : ""}`, `${starText} · ${toolText}`);
    metaTop.append(
      el("span", "", `${trend.earliestDate} → ${trend.latestDate}`),
      deltaEl
    );

    const metaRange = el("div", "trend-meta");
    metaRange.append(
      el("span", "", `${formatCompactNumber(trend.minStars)} → ${formatCompactNumber(trend.maxStars)} ★`),
      el("span", "", `${trend.points.length} ${lang === "zh" ? "次巡检记录" : "audits"}`)
    );

    wrap.append(svg, metaTop, metaRange);
    trendCard.append(wrap);
    grid.append(trendCard);
  }

  details.append(grid);
  mountEl.append(details);
}

export function renderCompareTray(barEl, dialogEl, bodyEl, state, onRemove, onClear) {
  if (!barEl || !state.bundle) return;
  const selected = state.compareIds
    .map((id) => state.bundle.tools.find((t) => t.id === id))
    .filter(Boolean);

  if (selected.length === 0) {
    barEl.hidden = true;
    barEl.textContent = "";
    return;
  }

  barEl.hidden = false;
  barEl.textContent = "";
  const inner = el("div", "container compare-bar-inner");
  const chips = el("div", "compare-chips");
  chips.append(
    el("span", "compare-label", state.lang === "zh" ? `已选对比 (${selected.length}/3):` : `Compare (${selected.length}/3):`)
  );

  for (const tool of selected) {
    const chip = el("span", "compare-chip");
    chip.append(document.createTextNode(tool.name));
    const rm = el("button", "chip-remove", "×");
    rm.type = "button";
    rm.setAttribute("aria-label", `Remove ${tool.name} from comparison`);
    rm.addEventListener("click", () => onRemove(tool.id));
    chip.append(rm);
    chips.append(chip);
  }

  const actions = el("div", "compare-actions");
  const clearBtn = el("button", "btn btn-ghost btn-sm", state.lang === "zh" ? "清空" : "Clear");
  clearBtn.type = "button";
  clearBtn.addEventListener("click", onClear);

  const openBtn = el(
    "button",
    "btn btn-primary btn-sm",
    state.lang === "zh" ? `横向对比 (${selected.length})` : `Compare Now (${selected.length})`
  );
  openBtn.type = "button";
  openBtn.disabled = selected.length < 2;
  openBtn.addEventListener("click", () => {
    renderComparisonTable(bodyEl, selected, state.lang);
    if (!dialogEl.open) dialogEl.showModal();
  });

  actions.append(clearBtn, openBtn);
  inner.append(chips, actions);
  barEl.append(inner);
}

export function renderComparisonTable(bodyEl, tools, lang) {
  bodyEl.textContent = "";
  const wrap = el("div", "table-scroll");
  const table = el("table", "compare-table");
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  headRow.append(el("th", "", lang === "zh" ? "维度" : "Metric"));
  for (const tool of tools) {
    const th = document.createElement("th");
    const link = el("a", "", tool.name);
    link.href = tool.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    th.append(link);
    headRow.append(th);
  }
  thead.append(headRow);

  const tbody = document.createElement("tbody");
  const rows = [
    [lang === "zh" ? "仓库" : "Repository", (t) => t.repo],
    [lang === "zh" ? "GitHub Stars" : "GitHub Stars", (t) => `★ ${formatCompactNumber(t.telemetry?.stars || 0)}`],
    [lang === "zh" ? "健康评分" : "Health Score", (t) => (t.telemetry?.health_score != null ? `${t.telemetry.health_score}/100` : "—")],
    [lang === "zh" ? "状态" : "Status", (t) => getStatusLabel(t.telemetry?.status, lang)],
    [lang === "zh" ? "主语言" : "Language", (t) => t.telemetry?.language || "—"],
    [lang === "zh" ? "开源协议" : "License", (t) => t.telemetry?.license || "—"],
    [lang === "zh" ? "最新版本" : "Latest Release", (t) => t.telemetry?.latest_release || "—"],
    [
      lang === "zh" ? "最近更新" : "Last Push",
      (t) =>
        t.telemetry?.days_inactive != null
          ? lang === "zh"
            ? `${t.telemetry.days_inactive} 天前`
            : `${t.telemetry.days_inactive}d ago`
          : "—",
    ],
    [lang === "zh" ? "支持平台" : "Platforms", (t) => (t.platforms || []).join(", ")],
    [lang === "zh" ? "标签" : "Tags", (t) => (t.tags || []).join(", ")],
    [
      lang === "zh" ? "专有性依据" : "Exclusivity Rationale",
      (t) => (lang === "zh" ? t.exclusivity_reason_zh : t.exclusivity_reason_en),
    ],
  ];

  for (const [label, getter] of rows) {
    const tr = document.createElement("tr");
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = label;
    tr.append(th);
    for (const tool of tools) {
      tr.append(el("td", "", getter(tool)));
    }
    tbody.append(tr);
  }

  table.append(thead, tbody);
  wrap.append(table);
  bodyEl.append(wrap);
}
