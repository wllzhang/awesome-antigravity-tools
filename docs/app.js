import {
  filterAndSortTools,
  formatCompactNumber,
  getScoreTier,
  getStatusLabel,
  parseParamsToState,
  serializeStateToParams,
} from "./catalog-logic.js";
import { renderCompareTray, renderComparisonTable, renderInsightsPanel } from "./insights.js";

const I18N = {
  en: {
    title: "Awesome Antigravity Tools",
    subtitle: "100% Google Antigravity-exclusive tools, extensions, runtime hotfixes & ACP gateways.",
    githubBtn: "GitHub ↗",
    statTools: "Curated Tools",
    statStars: "Combined Stars",
    statHealth: "Active Ratio",
    statScore: "Avg Health Score",
    allCategories: "All",
    allPlatforms: "All Platforms",
    allLanguages: "All Languages",
    allStatuses: "All Statuses",
    statusHealthy: "Healthy & Active",
    statusStale: "Stale (>180d)",
    sortStars: "Most Stars",
    sortScore: "Health Score",
    sortRecent: "Recently Updated",
    sortName: "Alphabetical (A-Z)",
    searchLabel: "Search tools",
    platformLabel: "Filter by platform",
    languageLabel: "Filter by programming language",
    statusLabel: "Filter by health status",
    sortLabel: "Sort tools",
    searchPlaceholder: "Search tools, tags, languages, ACP, quota... (Press /)",
    featuredOnly: "Featured Only",
    featuredBadge: "★ Featured",
    popularTags: "Tags:",
    resetFilters: "Reset filters",
    emptyMessage: "No Antigravity-exclusive tools matched your current filters.",
    details: "Details",
    compare: "Compare",
    comparing: "Selected ✓",
    openRepo: "Open on GitHub ↗",
    copyLink: "Copy Share Link",
    copyCompareLink: "Copy Comparison Link",
    copied: "Copied ✓",
    exclusivityHeading: "Why 100% Antigravity-Exclusive",
    installHeading: "Quick Install / Usage",
    copyCmd: "Copy",
    copyInstall: "Install",
    compareHeading: "Side-by-Side Tool Comparison",
    detailStatus: "Status",
    detailScore: "Health Score",
    detailStars: "Stars",
    detailLang: "Language",
    detailLicense: "License",
    detailRelease: "Latest Release",
    detailPush: "Last Push",
    detailAdded: "Added",
    footerNote: "Backed by single-source-of-truth",
    contribute: "Contribute",
    auditReport: "Health Report",
    langToggle: "中文",
    shortcutsBtn: "?",
    shortcutsHeading: "Keyboard Shortcuts",
    shortcutSearch: "Focus search box",
    shortcutNavigate: "Move focus across tool cards",
    shortcutOpen: "Open focused tool details",
    shortcutLang: "Switch English / 中文",
    shortcutEsc: "Clear search or close dialog",
    shortcutHelp: "Toggle this shortcuts help",
  },
  zh: {
    title: "Awesome Antigravity Tools",
    subtitle: "纯粹且极致：100% 专为 Google Antigravity 打造的扩展、底层修复与 ACP 网关。",
    githubBtn: "GitHub ↗",
    statTools: "收录专有工具",
    statStars: "生态合计 Stars",
    statHealth: "健康活跃率",
    statScore: "平均健康分",
    allCategories: "全部",
    allPlatforms: "全部平台",
    allLanguages: "全部语言",
    allStatuses: "全部状态",
    statusHealthy: "活跃健康",
    statusStale: "观察 (>180天)",
    sortStars: "按 Star 排序",
    sortScore: "按健康分排序",
    sortRecent: "按最近更新",
    sortName: "按名称 A-Z",
    searchLabel: "搜索工具",
    platformLabel: "按平台筛选",
    languageLabel: "按编程语言筛选",
    statusLabel: "按健康状态筛选",
    sortLabel: "工具排序",
    searchPlaceholder: "搜索工具名、标签、语言、ACP、配额... (按 / 聚焦)",
    featuredOnly: "仅看精选",
    featuredBadge: "★ 精选",
    popularTags: "热门标签:",
    resetFilters: "重置筛选",
    emptyMessage: "当前筛选条件下未找到匹配的 Antigravity 专有工具。",
    details: "查看详情",
    compare: "对比",
    comparing: "已选 ✓",
    openRepo: "访问 GitHub ↗",
    copyLink: "复制分享链接",
    copyCompareLink: "复制对比链接",
    copied: "已复制 ✓",
    exclusivityHeading: "为什么 100% 专属于 Antigravity",
    installHeading: "快速安装 / 使用提示",
    copyCmd: "复制",
    copyInstall: "安装",
    compareHeading: "工具横向对比",
    detailStatus: "健康状态",
    detailScore: "健康评分",
    detailStars: "Stars",
    detailLang: "主语言",
    detailLicense: "开源协议",
    detailRelease: "最新版本",
    detailPush: "最近推送",
    detailAdded: "收录日期",
    footerNote: "由单一数据源驱动",
    contribute: "参与贡献",
    auditReport: "巡检报告",
    langToggle: "EN",
    shortcutsBtn: "?",
    shortcutsHeading: "键盘快捷键",
    shortcutSearch: "聚焦搜索框",
    shortcutNavigate: "切换工具卡片焦点",
    shortcutOpen: "打开当前焦点工具详情",
    shortcutLang: "切换中英文界面",
    shortcutEsc: "清空搜索或关闭弹窗",
    shortcutHelp: "打开/关闭快捷键帮助",
  },
};

const state = {
  ...parseParamsToState(window.location.search),
  bundle: null,
  focusedIndex: -1,
};

const els = {
  searchInput: document.getElementById("searchInput"),
  platformFilter: document.getElementById("platformFilter"),
  languageFilter: document.getElementById("languageFilter"),
  statusFilter: document.getElementById("statusFilter"),
  sortSelect: document.getElementById("sortSelect"),
  categoryPills: document.getElementById("categoryPills"),
  tagFilterBar: document.getElementById("tagFilterBar"),
  resultsCount: document.getElementById("resultsCount"),
  featuredToggleBtn: document.getElementById("featuredToggleBtn"),
  resetFiltersBtn: document.getElementById("resetFiltersBtn"),
  emptyResetBtn: document.getElementById("emptyResetBtn"),
  toolsGrid: document.getElementById("toolsGrid"),
  emptyState: document.getElementById("emptyState"),
  langToggle: document.getElementById("langToggle"),
  themeToggle: document.getElementById("themeToggle"),
  shortcutsBtn: document.getElementById("shortcutsBtn"),
  toolDialog: document.getElementById("toolDialog"),
  dialogTitle: document.getElementById("dialogTitle"),
  dialogRepo: document.getElementById("dialogRepo"),
  dialogBody: document.getElementById("dialogBody"),
  dialogGithubLink: document.getElementById("dialogGithubLink"),
  dialogCloseBtn: document.getElementById("dialogCloseBtn"),
  dialogCopyUrlBtn: document.getElementById("dialogCopyUrlBtn"),
  compareBar: document.getElementById("compareBar"),
  compareDialog: document.getElementById("compareDialog"),
  compareBody: document.getElementById("compareBody"),
  compareCloseBtn: document.getElementById("compareCloseBtn"),
  compareCopyUrlBtn: document.getElementById("compareCopyUrlBtn"),
  shortcutsDialog: document.getElementById("shortcutsDialog"),
  shortcutsCloseBtn: document.getElementById("shortcutsCloseBtn"),
  insightsMount: document.getElementById("insightsMount"),
  statTotalTools: document.getElementById("statTotalTools"),
  statTotalStars: document.getElementById("statTotalStars"),
  statActiveRatio: document.getElementById("statActiveRatio"),
  statAvgScore: document.getElementById("statAvgScore"),
  lastUpdatedText: document.getElementById("lastUpdatedText"),
  footerContributeLink: document.getElementById("footerContributeLink"),
  footerReportLink: document.getElementById("footerReportLink"),
};

function t(key) {
  return (I18N[state.lang] && I18N[state.lang][key]) || I18N.en[key] || key;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

// Theme toggle following modern-web-guidance `dark-mode-toggle`
function initThemeToggle() {
  const meta = document.querySelector('meta[name="color-scheme"]');
  const getSystemDark = () => window.matchMedia("(prefers-color-scheme: dark)").matches;

  function applySchemeFromStorage() {
    try {
      const saved = localStorage.getItem("color-scheme");
      meta.content = saved === "light" || saved === "dark" ? saved : "light dark";
    } catch {
      meta.content = "light dark";
    }
  }

  els.themeToggle.addEventListener("click", () => {
    let saved = null;
    try {
      saved = localStorage.getItem("color-scheme");
    } catch {}
    const sysDark = getSystemDark();
    const currentlyDark = saved ? saved === "dark" : sysDark;
    const target = currentlyDark ? "light" : "dark";
    const matchesSystem = (target === "dark") === sysDark;

    try {
      if (matchesSystem) {
        localStorage.removeItem("color-scheme");
      } else {
        localStorage.setItem("color-scheme", target);
      }
    } catch {}
    meta.content = matchesSystem ? "light dark" : target;
  });

  window.addEventListener("storage", (e) => {
    if (e.key === "color-scheme") applySchemeFromStorage();
  });
}

// Safari fallback for `closedby="any"` following modern-web-guidance `light-dismiss-a-dialog`
function attachDialogLightDismissFallback(dialog) {
  if (!("closedBy" in HTMLDialogElement.prototype)) {
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      const inside =
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width;
      if (!inside) dialog.close();
    });
  }
}

function syncUrl() {
  const params = serializeStateToParams(state);
  const qs = params.toString();
  const nextUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
  window.history.replaceState(null, "", nextUrl);
}

function applyI18n() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  for (const node of document.querySelectorAll("[data-i18n]")) {
    const key = node.getAttribute("data-i18n");
    if (key) node.textContent = t(key);
  }
  els.searchInput.placeholder = t("searchPlaceholder");
  els.langToggle.textContent = t("langToggle");
  if (els.languageFilter) {
    els.languageFilter.setAttribute("aria-label", t("languageLabel"));
  }
  if (els.shortcutsBtn) {
    const scLabel = t("shortcutsHeading");
    els.shortcutsBtn.setAttribute("aria-label", scLabel);
    els.shortcutsBtn.setAttribute("title", scLabel);
  }
  if (els.tagFilterBar) {
    els.tagFilterBar.setAttribute("aria-label", state.lang === "zh" ? "热门标签" : "Popular tags");
  }
  if (els.footerContributeLink) {
    els.footerContributeLink.href =
      state.lang === "zh"
        ? "https://github.com/wllzhang/awesome-antigravity-tools/blob/main/CONTRIBUTING.zh-CN.md"
        : "https://github.com/wllzhang/awesome-antigravity-tools/blob/main/CONTRIBUTING.md";
  }
  if (els.footerReportLink) {
    els.footerReportLink.href =
      state.lang === "zh"
        ? "https://github.com/wllzhang/awesome-antigravity-tools/blob/main/health_report.zh-CN.md"
        : "https://github.com/wllzhang/awesome-antigravity-tools/blob/main/health_report.md";
  }
}

function renderSummary() {
  const s = state.bundle.summary;
  els.statTotalTools.textContent = String(s.total_tools);
  els.statTotalStars.textContent = formatCompactNumber(s.total_stars);
  els.statActiveRatio.textContent = `${s.healthy_tools}/${s.total_tools} (${s.health_ratio_pct}%)`;
  els.statAvgScore.textContent = s.average_health_score !== null ? `${s.average_health_score}/100` : "—";
  els.lastUpdatedText.textContent =
    state.lang === "zh"
      ? `最近巡检：${state.bundle.generated_at.replace("T", " ").replace("Z", " UTC")}`
      : `Last audited: ${state.bundle.generated_at.replace("T", " ").replace("Z", " UTC")}`;
}

function populatePlatformSelect() {
  const platforms = state.bundle.summary.by_platform || [];
  const validNames = new Set(platforms.map((p) => p.name));
  if (state.platform !== "all" && !validNames.has(state.platform)) {
    state.platform = "all";
  }
  while (els.platformFilter.options.length > 1) {
    els.platformFilter.remove(1);
  }
  for (const p of platforms) {
    const opt = document.createElement("option");
    opt.value = p.name;
    opt.textContent = `${p.name} (${p.count})`;
    els.platformFilter.append(opt);
  }
  els.platformFilter.value = state.platform;
}

function populateLanguageSelect() {
  if (!els.languageFilter) return;
  const languages = state.bundle.summary.by_language || [];
  if (state.language && state.language !== "all") {
    const match = languages.find((item) => item.name.toLowerCase() === state.language.toLowerCase());
    state.language = match ? match.name : "all";
  }
  while (els.languageFilter.options.length > 1) {
    els.languageFilter.remove(1);
  }
  for (const langItem of languages) {
    const opt = document.createElement("option");
    opt.value = langItem.name;
    opt.textContent = `${langItem.name} (${langItem.count})`;
    els.languageFilter.append(opt);
  }
  els.languageFilter.value = state.language;
}

function renderTagFilterBar() {
  if (!els.tagFilterBar) return;
  els.tagFilterBar.textContent = "";
  const topTags = (state.bundle.summary.top_tags || []).slice(0, 12);
  const tagList = [...topTags];
  if (
    state.tag &&
    state.tag !== "all" &&
    !tagList.some((item) => item.name.toLowerCase() === state.tag.toLowerCase())
  ) {
    tagList.unshift({ name: state.tag, count: "" });
  }
  if (tagList.length === 0) return;

  els.tagFilterBar.append(el("span", "tag-bar-label", t("popularTags")));
  for (const item of tagList) {
    const isActive = state.tag.toLowerCase() === item.name.toLowerCase();
    const label = item.count ? `${item.name} (${item.count})` : item.name;
    const btn = el("button", "tag tag-btn", label);
    btn.type = "button";
    btn.setAttribute("aria-pressed", String(isActive));
    btn.addEventListener("click", () => {
      state.tag = isActive ? "all" : item.name;
      renderAll();
    });
    els.tagFilterBar.append(btn);
  }
}

function renderCategoryPills() {
  els.categoryPills.textContent = "";
  const counts = {};
  for (const tool of state.bundle.tools) {
    counts[tool.category] = (counts[tool.category] || 0) + 1;
  }

  const allPill = el("button", "pill", `${t("allCategories")} (${state.bundle.tools.length})`);
  allPill.type = "button";
  allPill.role = "tab";
  allPill.setAttribute("aria-selected", String(state.category === "all"));
  allPill.addEventListener("click", () => {
    state.category = "all";
    renderAll();
  });
  els.categoryPills.append(allPill);

  for (const cat of state.bundle.categories) {
    const label = state.lang === "zh" ? cat.name_zh : cat.name_en;
    const pill = el("button", "pill", `${cat.icon} ${label} (${counts[cat.id] || 0})`);
    pill.type = "button";
    pill.role = "tab";
    pill.setAttribute("aria-selected", String(state.category === cat.id));
    pill.addEventListener("click", () => {
      state.category = cat.id;
      renderAll();
    });
    els.categoryPills.append(pill);
  }
}

function openToolDialog(tool) {
  state.openToolId = tool.id;
  syncUrl();
  const tel = tool.telemetry || {};
  els.dialogTitle.textContent = tool.name;
  els.dialogRepo.textContent = tool.repo;
  els.dialogGithubLink.href = tool.url;
  els.dialogBody.textContent = "";

  const desc = el("p", "", state.lang === "zh" ? tool.description_zh : tool.description_en);
  els.dialogBody.append(desc);

  const callout = el("div", "callout-box");
  const strong = el("strong", "", `${t("exclusivityHeading")}: `);
  const reasonText = document.createTextNode(
    state.lang === "zh" ? tool.exclusivity_reason_zh : tool.exclusivity_reason_en
  );
  callout.append(strong, reasonText);
  els.dialogBody.append(callout);

  const grid = el("div", "detail-grid");
  const lastPushVal =
    tel.days_inactive != null
      ? state.lang === "zh"
        ? `${tel.days_inactive} 天前`
        : `${tel.days_inactive}d ago`
      : "—";
  const kvs = [
    [t("detailStatus"), getStatusLabel(tel.status, state.lang)],
    [t("detailScore"), tel.health_score != null ? `${tel.health_score}/100` : "—"],
    [t("detailStars"), (tel.stars || 0).toLocaleString()],
    [t("detailLang"), tel.language || "—"],
    [t("detailLicense"), tel.license || "—"],
    [t("detailRelease"), tel.latest_release || "—"],
    [t("detailPush"), lastPushVal],
    [t("detailAdded"), tool.added_at || "—"],
  ];
  for (const [k, v] of kvs) {
    const box = el("div", "detail-kv");
    box.append(el("span", "", k), el("strong", "", v));
    grid.append(box);
  }
  els.dialogBody.append(grid);

  const tagsWrap = el("div", "tag-row");
  for (const p of tool.platforms || []) tagsWrap.append(el("span", "tag tag-muted", p));
  for (const tg of tool.tags || []) tagsWrap.append(el("span", "tag", tg));
  els.dialogBody.append(tagsWrap);

  if (tool.install_hint) {
    const installWrap = el("div");
    installWrap.append(el("p", "stat-label", t("installHeading")));
    const box = el("div", "install-box");
    const code = el("code", "", tool.install_hint);
    const copyBtn = el("button", "btn btn-ghost btn-sm", t("copyCmd"));
    copyBtn.type = "button";
    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(tool.install_hint);
        copyBtn.textContent = t("copied");
        setTimeout(() => (copyBtn.textContent = t("copyCmd")), 1500);
      } catch {}
    });
    box.append(code, copyBtn);
    installWrap.append(box);
    els.dialogBody.append(installWrap);
  }

  if (!els.toolDialog.open) {
    els.toolDialog.showModal();
  }
}

function renderToolsGrid() {
  state.focusedIndex = -1;
  const visible = filterAndSortTools(state.bundle.tools, state);
  els.toolsGrid.textContent = "";

  const isFiltered =
    Boolean(state.query) ||
    state.category !== "all" ||
    state.platform !== "all" ||
    state.language !== "all" ||
    (Boolean(state.tag) && state.tag !== "all") ||
    Boolean(state.featuredOnly) ||
    state.status !== "all";
  els.resetFiltersBtn.hidden = !isFiltered;
  if (els.featuredToggleBtn) {
    els.featuredToggleBtn.setAttribute("aria-pressed", String(Boolean(state.featuredOnly)));
  }

  els.resultsCount.textContent =
    state.lang === "zh"
      ? `显示 ${visible.length} / ${state.bundle.tools.length} 款专有工具`
      : `Showing ${visible.length} of ${state.bundle.tools.length} exclusive tools`;

  els.emptyState.hidden = visible.length > 0;

  for (const [idx, tool] of visible.entries()) {
    const tel = tool.telemetry || {};
    const shell = el("div", "tool-card-shell");
    const card = el("article", "tool-card");
    card.dataset.toolId = tool.id;
    card.tabIndex = 0;

    const top = el("div", "card-top");
    const titleWrap = el("div", "card-title-wrap");
    const h3 = el("h3", "card-title");
    const link = el("a", "", tool.name);
    link.href = tool.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    h3.append(link);
    titleWrap.append(h3, el("p", "card-repo", tool.repo));

    const metrics = el("div", "card-metrics");
    if (tool.featured) {
      metrics.append(el("span", "badge badge-featured", t("featuredBadge")));
    }
    metrics.append(el("span", "badge badge-star", `★ ${formatCompactNumber(tel.stars || 0)}`));
    const tier = getScoreTier(tel.health_score);
    const scoreText = tel.health_score != null ? `${tel.health_score}` : "—";
    metrics.append(el("span", `badge badge-${tier}`, `${scoreText}/100`));

    top.append(titleWrap, metrics);

    const desc = el("p", "card-desc", state.lang === "zh" ? tool.description_zh : tool.description_en);

    const tagRow = el("div", "tag-row");
    for (const tg of tool.tags || []) {
      const isTagActive = state.tag && state.tag.toLowerCase() === tg.toLowerCase();
      const tagBtn = el("button", "tag tag-btn", tg);
      tagBtn.type = "button";
      tagBtn.setAttribute("aria-pressed", String(Boolean(isTagActive)));
      tagBtn.addEventListener("click", () => {
        state.tag = isTagActive ? "all" : tg;
        renderAll();
      });
      tagRow.append(tagBtn);
    }
    if (tel.language) tagRow.append(el("span", "tag tag-muted", tel.language));

    const footer = el("div", "card-footer");
    const metaText = `${getStatusLabel(tel.status, state.lang)}${tel.license ? ` · ${tel.license}` : ""}`;
    footer.append(el("span", "", metaText));

    const actions = el("div", "card-actions");
    if (tool.install_hint) {
      const installBtn = el("button", "btn btn-ghost btn-sm", t("copyInstall"));
      installBtn.type = "button";
      installBtn.title = tool.install_hint;
      installBtn.setAttribute("aria-label", `${t("copyInstall")}: ${tool.install_hint}`);
      installBtn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(tool.install_hint);
          installBtn.textContent = t("copied");
          setTimeout(() => (installBtn.textContent = t("copyInstall")), 1500);
        } catch {}
      });
      actions.append(installBtn);
    }
    const isCompared = state.compareIds.includes(tool.id);
    const cmpBtn = el("button", "btn btn-ghost btn-sm", isCompared ? t("comparing") : t("compare"));
    cmpBtn.type = "button";
    cmpBtn.setAttribute("aria-pressed", String(isCompared));
    cmpBtn.addEventListener("click", () => toggleCompare(tool.id));

    const detBtn = el("button", "btn btn-primary btn-sm", t("details"));
    detBtn.type = "button";
    detBtn.addEventListener("click", () => openToolDialog(tool));

    actions.append(cmpBtn, detBtn);
    footer.append(actions);

    card.append(top, desc, tagRow, footer);
    shell.append(card);
    els.toolsGrid.append(shell);
  }
}

function syncCompareTray() {
  renderCompareTray(
    els.compareBar,
    els.compareDialog,
    els.compareBody,
    state,
    (id) => toggleCompare(id),
    () => {
      state.compareIds = [];
      syncCompareTray();
      renderToolsGrid();
      syncUrl();
    }
  );
}

function toggleCompare(toolId) {
  if (state.compareIds.includes(toolId)) {
    state.compareIds = state.compareIds.filter((id) => id !== toolId);
  } else if (state.compareIds.length < 3) {
    state.compareIds = [...state.compareIds, toolId];
  }
  syncCompareTray();
  renderToolsGrid();
  syncUrl();
}

function resetFilters() {
  state.query = "";
  state.category = "all";
  state.platform = "all";
  state.language = "all";
  state.tag = "all";
  state.featuredOnly = false;
  state.status = "all";
  state.sort = "stars";
  els.searchInput.value = "";
  els.platformFilter.value = "all";
  if (els.languageFilter) els.languageFilter.value = "all";
  els.statusFilter.value = "all";
  els.sortSelect.value = "stars";
  renderAll();
}

function renderAll() {
  applyI18n();
  renderSummary();
  populatePlatformSelect();
  populateLanguageSelect();
  renderCategoryPills();
  renderTagFilterBar();
  renderInsightsPanel(els.insightsMount, state.bundle, state.lang);
  syncCompareTray();
  renderToolsGrid();
  syncUrl();
  window.dispatchEvent(new CustomEvent("aat:rendered", { detail: { state } }));
}

function bindEvents() {
  els.searchInput.value = state.query;
  els.statusFilter.value = state.status;
  els.sortSelect.value = state.sort;

  els.searchInput.addEventListener("input", () => {
    state.query = els.searchInput.value;
    renderToolsGrid();
    syncUrl();
  });

  els.platformFilter.addEventListener("change", () => {
    state.platform = els.platformFilter.value;
    renderToolsGrid();
    syncUrl();
  });

  if (els.languageFilter) {
    els.languageFilter.addEventListener("change", () => {
      state.language = els.languageFilter.value;
      renderToolsGrid();
      syncUrl();
    });
  }

  els.statusFilter.addEventListener("change", () => {
    state.status = els.statusFilter.value;
    renderToolsGrid();
    syncUrl();
  });

  els.sortSelect.addEventListener("change", () => {
    state.sort = els.sortSelect.value;
    renderToolsGrid();
    syncUrl();
  });

  els.langToggle.addEventListener("click", () => {
    state.lang = state.lang === "en" ? "zh" : "en";
    renderAll();
  });

  els.resetFiltersBtn.addEventListener("click", resetFilters);
  els.emptyResetBtn.addEventListener("click", resetFilters);

  if (els.featuredToggleBtn) {
    els.featuredToggleBtn.addEventListener("click", () => {
      state.featuredOnly = !state.featuredOnly;
      renderAll();
    });
  }

  els.dialogCloseBtn.addEventListener("click", () => els.toolDialog.close());
  els.compareCloseBtn.addEventListener("click", () => els.compareDialog.close());
  if (els.shortcutsBtn && els.shortcutsDialog) {
    els.shortcutsBtn.addEventListener("click", () => {
      if (!els.shortcutsDialog.open) els.shortcutsDialog.showModal();
    });
  }
  if (els.shortcutsCloseBtn && els.shortcutsDialog) {
    els.shortcutsCloseBtn.addEventListener("click", () => els.shortcutsDialog.close());
  }

  if (els.compareCopyUrlBtn) {
    els.compareCopyUrlBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(window.location.href);
        els.compareCopyUrlBtn.textContent = t("copied");
        setTimeout(() => (els.compareCopyUrlBtn.textContent = t("copyCompareLink")), 1500);
      } catch {}
    });
  }

  els.toolDialog.addEventListener("close", () => {
    state.openToolId = "";
    syncUrl();
  });

  els.dialogCopyUrlBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      els.dialogCopyUrlBtn.textContent = t("copied");
      setTimeout(() => (els.dialogCopyUrlBtn.textContent = t("copyLink")), 1500);
    } catch {}
  });

  attachDialogLightDismissFallback(els.toolDialog);
  attachDialogLightDismissFallback(els.compareDialog);
  if (els.shortcutsDialog) attachDialogLightDismissFallback(els.shortcutsDialog);

  // Keyboard-first navigation shortcuts
  document.addEventListener("keydown", (event) => {
    if (els.shortcutsDialog?.open) {
      if (event.key === "?") {
        event.preventDefault();
        els.shortcutsDialog.close();
      }
      return;
    }
    if (els.toolDialog.open || els.compareDialog.open) return;
    const activeTag = (document.activeElement?.tagName || "").toUpperCase();
    const isTyping = activeTag === "INPUT" || activeTag === "TEXTAREA" || activeTag === "SELECT";

    if (event.key === "?" && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey) {
      if (els.shortcutsDialog) {
        event.preventDefault();
        els.shortcutsDialog.showModal();
      }
      return;
    }

    if (event.key === "/" && !isTyping && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();
      els.searchInput.focus();
      els.searchInput.select();
      return;
    }

    if (event.key === "Escape" && document.activeElement === els.searchInput && state.query) {
      state.query = "";
      els.searchInput.value = "";
      renderToolsGrid();
      syncUrl();
      return;
    }

    if (isTyping || event.ctrlKey || event.metaKey || event.altKey) return;

    if (event.key === "l" || event.key === "L") {
      state.lang = state.lang === "en" ? "zh" : "en";
      renderAll();
      return;
    }

    const cards = Array.from(els.toolsGrid.querySelectorAll(".tool-card"));
    if (!cards.length) return;

    if (event.key === "j" || event.key === "k") {
      event.preventDefault();
      const delta = event.key === "j" ? 1 : -1;
      state.focusedIndex =
        state.focusedIndex < 0
          ? 0
          : (state.focusedIndex + delta + cards.length) % cards.length;
      for (const [i, card] of cards.entries()) {
        card.classList.toggle("is-focused", i === state.focusedIndex);
      }
      const target = cards[state.focusedIndex];
      target.focus({ preventScroll: false });
      target.scrollIntoView({ block: "nearest", behavior: "smooth" });
      return;
    }

    if (event.key === "Enter" && document.activeElement?.classList.contains("tool-card")) {
      const tid = document.activeElement.dataset.toolId;
      const tool = state.bundle?.tools.find((item) => item.id === tid);
      if (tool) openToolDialog(tool);
    }
  });
}

async function boot() {
  initThemeToggle();
  bindEvents();
  try {
    const resp = await fetch("./catalog-bundle.json", { cache: "no-store" });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    state.bundle = await resp.json();
    const validIds = new Set(state.bundle.tools.map((tool) => tool.id));
    state.compareIds = (state.compareIds || []).filter((id) => validIds.has(id)).slice(0, 3);
    window.__AAT_STATE__ = state;
    renderAll();

    if (state.openToolId) {
      const target = state.bundle.tools.find((item) => item.id === state.openToolId);
      if (target) {
        openToolDialog(target);
      } else {
        state.openToolId = "";
        syncUrl();
      }
    } else if (state.compareIds.length >= 2) {
      const selected = state.compareIds
        .map((id) => state.bundle.tools.find((item) => item.id === id))
        .filter(Boolean);
      if (selected.length >= 2) {
        renderComparisonTable(els.compareBody, selected, state.lang);
        if (!els.compareDialog.open) els.compareDialog.showModal();
      }
    }
  } catch (err) {
    els.resultsCount.textContent = `Failed to load catalog-bundle.json: ${err.message}`;
  }
}

boot();
