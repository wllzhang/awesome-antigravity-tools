/**
 * Pure filtering, sorting, and formatting logic for the Awesome Antigravity Tools Web Explorer.
 * Shared between browser UI (`app.js`) and Node.js automated tests.
 */

export function formatCompactNumber(num) {
  const n = Number(num) || 0;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

export function filterAndSortTools(tools, state) {
  const query = (state.query || "").trim().toLowerCase();
  const tokens = query ? query.split(/\s+/).filter(Boolean) : [];
  const category = state.category || "all";
  const platform = state.platform || "all";
  const tag = (state.tag || "all").trim();
  const tagLower = tag.toLowerCase();
  const featuredOnly = Boolean(state.featuredOnly);
  const status = state.status || "all";
  const sort = state.sort || "stars";

  const filtered = tools.filter((tool) => {
    if (category !== "all" && tool.category !== category) return false;
    if (platform !== "all" && !(tool.platforms || []).includes(platform)) return false;
    if (tagLower && tagLower !== "all") {
      const hasTag = (tool.tags || []).some((tg) => String(tg).toLowerCase() === tagLower);
      if (!hasTag) return false;
    }
    if (featuredOnly && !tool.featured) return false;
    const toolStatus = (tool.telemetry?.status || "UNAUDITED").toUpperCase();
    if (status !== "all" && toolStatus !== status.toUpperCase()) return false;

    if (tokens.length > 0) {
      const haystack = [
        tool.id,
        tool.name,
        tool.repo,
        tool.description_en,
        tool.description_zh,
        tool.exclusivity_reason_en,
        tool.exclusivity_reason_zh,
        ...(tool.tags || []),
        ...(tool.platforms || []),
        tool.telemetry?.language || "",
        tool.telemetry?.license || "",
      ]
        .join(" ")
        .toLowerCase();
      if (!tokens.every((tk) => haystack.includes(tk))) return false;
    }
    return true;
  });

  const sorted = [...filtered];
  if (sort === "score") {
    sorted.sort(
      (a, b) =>
        (b.telemetry?.health_score ?? -1) - (a.telemetry?.health_score ?? -1) ||
        (b.telemetry?.stars ?? 0) - (a.telemetry?.stars ?? 0)
    );
  } else if (sort === "recent") {
    sorted.sort(
      (a, b) =>
        (a.telemetry?.days_inactive ?? 99999) - (b.telemetry?.days_inactive ?? 99999) ||
        (b.telemetry?.stars ?? 0) - (a.telemetry?.stars ?? 0)
    );
  } else if (sort === "name") {
    sorted.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
  } else {
    sorted.sort(
      (a, b) =>
        (b.telemetry?.stars ?? 0) - (a.telemetry?.stars ?? 0) ||
        a.name.toLowerCase().localeCompare(b.name.toLowerCase())
    );
  }
  return sorted;
}

export function getStatusLabel(status, lang) {
  const s = (status || "UNAUDITED").toUpperCase();
  const en = {
    HEALTHY: "Healthy",
    STALE: "Stale (>180d)",
    VERY_STALE: "Very Stale",
    ARCHIVED: "Archived",
    DEAD: "Dead (404)",
    ERROR: "API Error",
    UNAUDITED: "Unaudited",
  };
  const zh = {
    HEALTHY: "活跃健康",
    STALE: "观察 (>180天)",
    VERY_STALE: "停滞 (>365天)",
    ARCHIVED: "已归档",
    DEAD: "已失效",
    ERROR: "接口异常",
    UNAUDITED: "待巡检",
  };
  return (lang === "zh" ? zh[s] : en[s]) || s;
}

export function getScoreTier(score) {
  if (typeof score !== "number") return "neutral";
  if (score >= 85) return "excellent";
  if (score >= 65) return "good";
  if (score >= 40) return "warn";
  return "danger";
}

function normalizeCompareIds(rawList) {
  const seen = new Set();
  const out = [];
  for (const item of rawList || []) {
    const cleaned = String(item || "").trim();
    if (cleaned && !seen.has(cleaned)) {
      seen.add(cleaned);
      out.push(cleaned);
      if (out.length >= 3) break;
    }
  }
  return out;
}

export function serializeStateToParams(state) {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category && state.category !== "all") params.set("cat", state.category);
  if (state.platform && state.platform !== "all") params.set("platform", state.platform);
  if (state.tag && state.tag !== "all") params.set("tag", state.tag);
  if (state.featuredOnly) params.set("featured", "1");
  if (state.status && state.status !== "all") params.set("status", state.status);
  if (state.sort && state.sort !== "stars") params.set("sort", state.sort);
  if (state.lang && state.lang !== "en") params.set("lang", state.lang);
  const cmp = normalizeCompareIds(state.compareIds);
  if (cmp.length > 0) params.set("compare", cmp.join(","));
  if (state.openToolId) params.set("tool", state.openToolId);
  return params;
}

export function parseParamsToState(searchString) {
  const params = new URLSearchParams(searchString || "");
  const rawCmp = params.get("compare") || "";
  const compareIds = normalizeCompareIds(rawCmp ? rawCmp.split(",") : []);
  return {
    query: params.get("q") || "",
    category: params.get("cat") || "all",
    platform: params.get("platform") || "all",
    tag: params.get("tag") || "all",
    featuredOnly: params.get("featured") === "1" || params.get("featured") === "true",
    status: params.get("status") || "all",
    sort: ["stars", "score", "recent", "name"].includes(params.get("sort")) ? params.get("sort") : "stars",
    lang: params.get("lang") === "zh" ? "zh" : "en",
    compareIds,
    openToolId: params.get("tool") || "",
  };
}

export function computeHistoryTrendSummary(history, width = 240, height = 64, padY = 8) {
  const list = Array.isArray(history)
    ? [...history]
        .filter((e) => e && typeof e.date === "string")
        .sort((a, b) => a.date.localeCompare(b.date))
    : [];
  if (list.length === 0) {
    return {
      points: [],
      starDelta: 0,
      toolDelta: 0,
      earliestDate: "",
      latestDate: "",
      starPolyline: "",
      toolPolyline: "",
      minStars: 0,
      maxStars: 0,
      minTools: 0,
      maxTools: 0,
    };
  }

  const starsArr = list.map((e) => Number(e.total_stars) || 0);
  const toolsArr = list.map((e) => Number(e.total) || 0);
  const minStars = Math.min(...starsArr);
  const maxStars = Math.max(...starsArr);
  const minTools = Math.min(...toolsArr);
  const maxTools = Math.max(...toolsArr);
  const usableH = Math.max(1, height - padY * 2);

  const buildPolyline = (vals, minV, maxV) => {
    const n = vals.length;
    return vals
      .map((val, idx) => {
        const x = n === 1 ? width / 2 : (idx / (n - 1)) * width;
        const y = maxV === minV ? height / 2 : padY + (1 - (val - minV) / (maxV - minV)) * usableH;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  };

  return {
    points: list,
    starDelta: starsArr[starsArr.length - 1] - starsArr[0],
    toolDelta: toolsArr[toolsArr.length - 1] - toolsArr[0],
    earliestDate: list[0].date,
    latestDate: list[list.length - 1].date,
    starPolyline: buildPolyline(starsArr, minStars, maxStars),
    toolPolyline: buildPolyline(toolsArr, minTools, maxTools),
    minStars,
    maxStars,
    minTools,
    maxTools,
  };
}
