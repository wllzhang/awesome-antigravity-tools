import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  computeHistoryTrendSummary,
  filterAndSortTools,
  formatCompactNumber,
  getScoreTier,
  getStatusLabel,
  parseParamsToState,
  serializeStateToParams,
} from "../docs/catalog-logic.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const bundlePath = path.resolve(__dirname, "..", "docs", "catalog-bundle.json");
const catalogPath = path.resolve(__dirname, "..", "data", "tools.json");
const bundle = JSON.parse(fs.readFileSync(bundlePath, "utf8"));
const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));

test("bundle contains expected categories and enriched tools", () => {
  assert.ok(bundle.categories.length >= 4);
  assert.equal(bundle.tools.length, catalog.tools.length);
  assert.ok(bundle.tools.length >= 15);
  for (const tool of bundle.tools) {
    assert.ok(tool.id && tool.name && tool.url && tool.telemetry);
  }
});

test("filterAndSortTools handles multi-token bilingual search and sorting", () => {
  const quotaTools = filterAndSortTools(bundle.tools, { query: "quota", sort: "stars" });
  assert.ok(quotaTools.length >= 3);
  for (let i = 1; i < quotaTools.length; i++) {
    assert.ok((quotaTools[i - 1].telemetry?.stars ?? 0) >= (quotaTools[i].telemetry?.stars ?? 0));
  }

  const zhSearch = filterAndSortTools(bundle.tools, { query: "硬链接" });
  assert.equal(zhSearch.length, 1);
  assert.equal(zhSearch[0].id, "antigravity-junction-skill-fix");

  const byScore = filterAndSortTools(bundle.tools, { sort: "score" });
  for (let i = 1; i < byScore.length; i++) {
    assert.ok(
      (byScore[i - 1].telemetry?.health_score ?? -1) >= (byScore[i].telemetry?.health_score ?? -1)
    );
  }

  const byName = filterAndSortTools(bundle.tools, { sort: "name" });
  for (let i = 1; i < byName.length; i++) {
    assert.ok(byName[i - 1].name.toLowerCase().localeCompare(byName[i].name.toLowerCase()) <= 0);
  }
});

test("category, platform, tag, featured, and status filters compose accurately", () => {
  const winPatches = filterAndSortTools(bundle.tools, {
    category: "platform-fixes-runtime-patches",
    platform: "Windows",
    status: "HEALTHY",
  });
  assert.ok(winPatches.length >= 3);
  for (const t of winPatches) {
    assert.equal(t.category, "platform-fixes-runtime-patches");
    assert.ok(t.platforms.includes("Windows"));
    assert.equal(t.telemetry.status, "HEALTHY");
  }

  const acpTagged = filterAndSortTools(bundle.tools, { tag: "acp" });
  assert.ok(acpTagged.length >= 4);
  for (const t of acpTagged) {
    assert.ok(t.tags.some((tg) => tg.toLowerCase() === "acp"));
  }

  const featuredTools = filterAndSortTools(bundle.tools, { featuredOnly: true });
  assert.ok(featuredTools.length >= 5);
  assert.ok(featuredTools.length < bundle.tools.length);
  for (const t of featuredTools) {
    assert.equal(Boolean(t.featured), true);
  }
});

test("URL state serialization round-trips cleanly with tag, featured, and compare capping", () => {
  const original = {
    query: "acp rust",
    category: "dedicated-gateways-migration",
    platform: "Linux",
    tag: "Gateway",
    featuredOnly: true,
    status: "HEALTHY",
    sort: "score",
    lang: "zh",
    compareIds: ["liftgate", "agy-gyro"],
    openToolId: "liftgate",
  };
  const qs = serializeStateToParams(original).toString();
  const parsed = parseParamsToState(`?${qs}`);
  assert.deepEqual(parsed, original);

  const capped = parseParamsToState("?compare=a,b,a,c,d&featured=true");
  assert.deepEqual(capped.compareIds, ["a", "b", "c"]);
  assert.equal(capped.featuredOnly, true);
});

test("computeHistoryTrendSummary computes polylines and deltas deterministically", () => {
  const empty = computeHistoryTrendSummary([]);
  assert.equal(empty.points.length, 0);
  assert.equal(empty.starPolyline, "");

  const single = computeHistoryTrendSummary([{ date: "2026-11-26", total: 37, total_stars: 73000 }]);
  assert.equal(single.starDelta, 0);
  assert.equal(single.starPolyline, "120.0,32.0");

  const multi = computeHistoryTrendSummary([
    { date: "2026-11-25", total: 19, total_stars: 61145 },
    { date: "2026-11-17", total: 21, total_stars: 59005 },
    { date: "2026-11-26", total: 37, total_stars: 73088 },
  ]);
  assert.equal(multi.earliestDate, "2026-11-17");
  assert.equal(multi.latestDate, "2026-11-26");
  assert.equal(multi.starDelta, 73088 - 59005);
  assert.equal(multi.toolDelta, 37 - 21);
  assert.equal(multi.starPolyline.split(" ").length, 3);
});

test("formatting and tier helpers behave deterministically", () => {
  assert.equal(formatCompactNumber(999), "999");
  assert.equal(formatCompactNumber(1500), "1.5k");
  assert.equal(formatCompactNumber(1_250_000), "1.3M");
  assert.equal(getStatusLabel("HEALTHY", "en"), "Healthy");
  assert.equal(getStatusLabel("HEALTHY", "zh"), "活跃健康");
  assert.equal(getScoreTier(95), "excellent");
  assert.equal(getScoreTier(72), "good");
  assert.equal(getScoreTier(45), "warn");
  assert.equal(getScoreTier(10), "danger");
});
