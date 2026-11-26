#!/usr/bin/env python3
"""
Interactive Zero-Dependency CLI (`aat`) for awesome-antigravity-tools.

Usage:
  python scripts/aat_cli.py list [--category ...] [--platform ...] [--sort stars]
  python scripts/aat_cli.py search <query> [--lang en|zh] [--json]
  python scripts/aat_cli.py recommend <intent> [--platform ...] [--limit 5]
  python scripts/aat_cli.py compare <tool1> <tool2> [tool3] [tool4] [--markdown]
  python scripts/aat_cli.py info <id-or-name>
  python scripts/aat_cli.py stats [--json]
  python scripts/aat_cli.py add --repo owner/name --category ... [fields...]
  python scripts/aat_cli.py verify [--check-sync]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_SNAPSHOT = REPO_ROOT / "data" / "health_snapshot.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_catalog_and_health(
    catalog_path: Path = DEFAULT_CATALOG, snapshot_path: Path = DEFAULT_SNAPSHOT
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    health_map: dict[str, dict[str, Any]] = {}
    if snapshot_path.exists():
        snap = json.loads(snapshot_path.read_text(encoding="utf-8"))
        for r in snap.get("repositories", []):
            if "full_name" in r:
                health_map[r["full_name"].lower()] = r
    return catalog, health_map


def enrich_tool(tool: dict[str, Any], health_map: dict[str, dict[str, Any]], cat_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    h = health_map.get(tool["repo"].lower(), {})
    cat = cat_map.get(tool["category"], {})
    return {
        **tool,
        "category_en": cat.get("name_en", tool["category"]),
        "category_zh": cat.get("name_zh", tool["category"]),
        "stars": int(h.get("stars", 0)),
        "forks": int(h.get("forks", 0)),
        "health_score": h.get("health_score"),
        "status": h.get("status", "UNAUDITED"),
        "language": h.get("language"),
        "license": h.get("license"),
        "latest_release": h.get("latest_release"),
        "days_inactive": h.get("days_inactive"),
    }


def filter_and_sort_tools(
    tools: list[dict[str, Any]],
    *,
    query: str = "",
    category: str = "",
    platform: str = "",
    tag: str = "",
    status: str = "",
    min_stars: int = 0,
    sort_by: str = "stars",
) -> list[dict[str, Any]]:
    q = query.strip().lower()
    cat_f = category.strip().lower()
    plat_f = platform.strip().lower()
    tag_f = tag.strip().lower()
    stat_f = status.strip().upper()

    matched: list[dict[str, Any]] = []
    for t in tools:
        if cat_f and t["category"].lower() != cat_f and cat_f not in t["category_en"].lower():
            continue
        if plat_f and not any(plat_f in p.lower() for p in t.get("platforms", [])):
            continue
        if tag_f and not any(tag_f == tg.lower() for tg in t.get("tags", [])):
            continue
        if stat_f and t.get("status", "").upper() != stat_f:
            continue
        if t.get("stars", 0) < min_stars:
            continue
        if q:
            haystack = " ".join(
                [
                    t.get("id", ""),
                    t.get("name", ""),
                    t.get("repo", ""),
                    t.get("description_en", ""),
                    t.get("description_zh", ""),
                    t.get("exclusivity_reason_en", ""),
                    t.get("exclusivity_reason_zh", ""),
                    " ".join(t.get("tags", [])),
                    " ".join(t.get("platforms", [])),
                    str(t.get("language") or ""),
                ]
            ).lower()
            if not all(token in haystack for token in q.split()):
                continue
        matched.append(t)

    if sort_by == "name":
        matched.sort(key=lambda x: x["name"].lower())
    elif sort_by == "score":
        matched.sort(key=lambda x: ((x.get("health_score") or -1), x.get("stars", 0)), reverse=True)
    elif sort_by == "recent":
        matched.sort(key=lambda x: (x.get("days_inactive") if x.get("days_inactive") is not None else 99999))
    else:
        matched.sort(key=lambda x: (x.get("stars", 0), x["name"].lower()), reverse=True)
    return matched


def print_tools_table(tools: list[dict[str, Any]], lang: str = "en") -> None:
    if not tools:
        print("No matching tools found.")
        return
    print(f"Found {len(tools)} Antigravity-exclusive tool(s):\n")
    for idx, t in enumerate(tools, 1):
        desc = t["description_zh"] if lang == "zh" else t["description_en"]
        score_s = f"{t['health_score']}/100" if t.get("health_score") is not None else "N/A"
        tags_s = ", ".join(t["tags"])
        print(f"{idx:>2}. {t['name']}  ({t['repo']})  ★{t['stars']:,} | {t['status']} ({score_s})")
        print(f"    {desc}")
        print(f"    Category: {t['category_zh'] if lang == 'zh' else t['category_en']} | Tags: [{tags_s}]")
        print(f"    URL: {t['url']}\n")


def cmd_list_or_search(args: argparse.Namespace, query: str = "") -> int:
    catalog, health_map = load_catalog_and_health(args.catalog, args.snapshot)
    cat_map = {c["id"]: c for c in catalog.get("categories", [])}
    enriched = [enrich_tool(t, health_map, cat_map) for t in catalog.get("tools", [])]
    filtered = filter_and_sort_tools(
        enriched,
        query=query,
        category=getattr(args, "category", "") or "",
        platform=getattr(args, "platform", "") or "",
        tag=getattr(args, "tag", "") or "",
        status=getattr(args, "status", "") or "",
        min_stars=getattr(args, "min_stars", 0) or 0,
        sort_by=getattr(args, "sort", "stars") or "stars",
    )
    if args.json:
        print(json.dumps(filtered, indent=2, ensure_ascii=False))
    else:
        print_tools_table(filtered, lang=args.lang)
    return 0


def find_tool(
    catalog: dict[str, Any],
    health_map: dict[str, dict[str, Any]],
    cat_map: dict[str, dict[str, Any]],
    identifier: str,
) -> dict[str, Any] | None:
    target = identifier.strip().lower()
    for t in catalog.get("tools", []):
        if target in (t["id"].lower(), t["name"].lower(), t["repo"].lower()):
            return enrich_tool(t, health_map, cat_map)
    return None


INTENT_SYNONYMS: dict[str, tuple[str, ...]] = {
    "quota": ("quota", "配额", "额度", "hud", "cockpit", "usage", "用量", "limit"),
    "配额": ("quota", "配额", "额度", "hud", "cockpit", "usage", "用量"),
    "额度": ("quota", "配额", "额度", "hud", "cockpit", "usage", "用量"),
    "proxy": ("proxy", "代理", "tun", "socks5", "http", "retry", "重试", "enterprise gateway"),
    "代理": ("proxy", "代理", "tun", "socks5", "http", "retry", "重试"),
    "tun": ("tun", "proxy", "代理", "dll"),
    "chinese": ("chinese", "汉化", "中文", "localization", "zh-cn", "语言包"),
    "汉化": ("chinese", "汉化", "中文", "localization", "zh-cn", "asar", "语言包"),
    "中文": ("chinese", "汉化", "中文", "localization", "zh-cn", "asar"),
    "localization": ("localization", "汉化", "中文", "chinese", "rtl", "排版"),
    "acp": ("acp", "gateway", "网关", "adapter", "适配器", "stdio", "agy acp"),
    "gateway": ("gateway", "网关", "acp", "openai", "anthropic", "gemini", "api"),
    "网关": ("gateway", "网关", "acp", "openai", "anthropic", "gemini", "api"),
    "symlink": ("symlink", "junction", "硬链接", "符号链接", "ntfs", "mklink", "reparse"),
    "junction": ("junction", "symlink", "硬链接", "符号链接", "ntfs", "mklink", "reparse"),
    "硬链接": ("junction", "symlink", "硬链接", "符号链接", "ntfs", "mklink"),
    "符号链接": ("junction", "symlink", "硬链接", "符号链接", "ntfs", "mklink"),
    "statusline": ("statusline", "hud", "状态栏", "powerline", "terminal"),
    "hud": ("hud", "statusline", "状态栏", "capsule", "胶囊", "cockpit", "telemetry"),
    "状态栏": ("statusline", "hud", "状态栏", "powerline"),
    "account": ("account", "accounts", "账号", "switch", "切换", "multi-account", "多账号", "多开", "sandbox"),
    "账号": ("account", "accounts", "账号", "switch", "切换", "multi-account", "多账号", "多开", "sandbox"),
    "多账号": ("multi-account", "账号", "account", "switch", "切换", "多开", "sandbox"),
    "多开": ("multi-account", "sandbox", "多开", "并行", "account", "账号"),
    "cache": ("cache", "缓存", "token", "加速", "kv", "fts5", "context", "上下文"),
    "缓存": ("cache", "缓存", "token", "加速", "kv", "fts5", "context", "上下文"),
    "加速": ("accelerator", "加速", "fast", "cache", "缓存", "token"),
    "mobile": ("mobile", "手机", "远程", "wecom", "pwa", "remote", "企微"),
    "手机": ("mobile", "手机", "远程", "wecom", "pwa", "remote", "企微"),
    "远程": ("remote", "远程", "mobile", "手机", "wecom", "pwa", "websocket"),
    "wecom": ("wecom", "企微", "企业微信", "remote"),
    "defender": ("defender", "agy.exe", "202", "backend", "timeout"),
    "context": ("context", "上下文", "token", "用量", "usage", "vial"),
    "上下文": ("context", "上下文", "token", "用量", "usage"),
    "theme": ("theme", "主题", "ui", "optical", "webgl2", "ux", "光学"),
    "主题": ("theme", "主题", "ui", "optical", "webgl2", "ux", "光学"),
    "flow": ("flow", "google-flow", "veo", "nano banana", "omni"),
    "robotics": ("robotics", "机器人", "mujoco", "deepmind"),
}


def _extract_intent_tokens(intent: str) -> tuple[list[str], set[str]]:
    intent_l = intent.strip().lower()
    raw_tokens = re.findall(r"[a-z0-9_.-]+|[\u4e00-\u9fff]+", intent_l)
    primary: list[str] = []
    seen_p: set[str] = set()

    def add_primary(tok: str) -> None:
        if tok and tok not in seen_p:
            seen_p.add(tok)
            primary.append(tok)

    for tok in raw_tokens:
        add_primary(tok)
        if re.search(r"[\u4e00-\u9fff]", tok) and len(tok) > 2:
            matched_sub = [k for k in INTENT_SYNONYMS if len(k) >= 2 and k in tok]
            for sub in matched_sub:
                add_primary(sub)
            if not matched_sub:
                for i in range(len(tok) - 1):
                    add_primary(tok[i : i + 2])

    expanded: set[str] = set()
    for tok in list(primary):
        for key, syns in INTENT_SYNONYMS.items():
            if tok == key or (len(key) >= 2 and key in tok):
                expanded.update(syns)
    return primary, expanded


def recommend_tools(
    tools: list[dict[str, Any]],
    intent: str,
    *,
    platform: str = "",
    limit: int = 5,
) -> list[dict[str, Any]]:
    intent_l = intent.strip().lower()
    if not intent_l:
        return []
    plat_f = platform.strip().lower()
    primary_tokens, expanded_tokens = _extract_intent_tokens(intent_l)
    synonym_only = expanded_tokens - set(primary_tokens)

    scored: list[dict[str, Any]] = []
    for t in tools:
        plats_l = [p.lower() for p in t.get("platforms", [])]
        if plat_f and not any(plat_f in p for p in plats_l):
            continue

        tid = t.get("id", "").lower()
        tname = t.get("name", "").lower()
        tags_l = [tg.lower() for tg in t.get("tags", [])]
        text_l = " ".join(
            [
                t.get("repo", ""),
                t.get("description_en", ""),
                t.get("description_zh", ""),
                t.get("exclusivity_reason_en", ""),
                t.get("exclusivity_reason_zh", ""),
                str(t.get("language") or ""),
            ]
        ).lower()

        relevance = 0.0
        reasons: list[str] = []

        if intent_l in (tid, tname):
            relevance += 45.0
            reasons.append("exact-name")

        for tok in primary_tokens:
            if tok in tid or tok in tname:
                relevance += 35.0
                reasons.append(f"name:{tok}")
            if any(tok == tg or tok in tg for tg in tags_l):
                relevance += 18.0
                reasons.append(f"tag:{tok}")
            if any(tok in p for p in plats_l):
                relevance += 10.0
                reasons.append(f"platform:{tok}")
            if tok in text_l:
                relevance += 12.0
                reasons.append(f"desc:{tok}")

        for syn in sorted(synonym_only):
            if syn in tid or syn in tname:
                relevance += 14.0
                reasons.append(f"syn-name:{syn}")
            if any(syn == tg or syn in tg for tg in tags_l):
                relevance += 10.0
                reasons.append(f"syn-tag:{syn}")
            if syn in text_l:
                relevance += 6.0
                reasons.append(f"syn-desc:{syn}")

        if relevance <= 0.0:
            continue

        status = str(t.get("status") or "UNAUDITED").upper()
        if status in ("ARCHIVED", "DEAD"):
            relevance -= 40.0
            reasons.append(f"penalty:{status.lower()}")
        elif status in ("STALE", "VERY_STALE"):
            relevance -= 15.0
            reasons.append(f"penalty:{status.lower()}")

        if t.get("featured"):
            relevance += 6.0
            reasons.append("featured")

        hs = t.get("health_score")
        if isinstance(hs, (int, float)):
            relevance += hs * 0.15

        stars = int(t.get("stars", 0))
        relevance += min(6.0, math.log10(stars + 1) * 1.2)

        dedup_reasons = list(dict.fromkeys(reasons))
        scored.append(
            {
                **t,
                "match_score": round(relevance, 1),
                "match_reasons": dedup_reasons,
            }
        )

    scored.sort(key=lambda x: (x["match_score"], x.get("stars", 0), x["name"].lower()), reverse=True)
    return scored[: max(1, limit)]


def render_comparison_markdown(tools: list[dict[str, Any]], lang: str = "en") -> str:
    header_label = "维度" if lang == "zh" else "Metric"
    headers = [header_label, *[f"[{t['name']}]({t['url']})" for t in tools]]
    aligns = [":---", *([":---"] * len(tools))]
    rows = [
        ("仓库" if lang == "zh" else "Repository", lambda t: f"`{t['repo']}`"),
        ("分类" if lang == "zh" else "Category", lambda t: t["category_zh"] if lang == "zh" else t["category_en"]),
        ("健康状态" if lang == "zh" else "Status", lambda t: f"`{t['status']}`"),
        ("健康分" if lang == "zh" else "Health Score", lambda t: f"{t['health_score']}/100" if t.get("health_score") is not None else "-"),
        ("Stars", lambda t: f"★{t.get('stars', 0):,}"),
        ("主语言" if lang == "zh" else "Language", lambda t: t.get("language") or "-"),
        ("开源协议" if lang == "zh" else "License", lambda t: t.get("license") or "-"),
        ("最新版本" if lang == "zh" else "Latest Release", lambda t: f"`{t['latest_release']}`" if t.get("latest_release") else "-"),
        ("最近推送" if lang == "zh" else "Last Push", lambda t: f"{t['days_inactive']}d ago" if t.get("days_inactive") is not None else "-"),
        ("平台" if lang == "zh" else "Platforms", lambda t: ", ".join(t.get("platforms", []))),
        ("标签" if lang == "zh" else "Tags", lambda t: ", ".join(t.get("tags", []))),
        ("专有性依据" if lang == "zh" else "Exclusivity", lambda t: (t["exclusivity_reason_zh"] if lang == "zh" else t["exclusivity_reason_en"]).replace("|", "\\|")),
        ("安装提示" if lang == "zh" else "Install Hint", lambda t: (t.get("install_hint") or "-").replace("|", "\\|")),
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(aligns) + " |",
    ]
    for label, getter in rows:
        vals = [getter(t) for t in tools]
        lines.append("| " + " | ".join([f"**{label}**", *vals]) + " |")
    return "\n".join(lines) + "\n"


def cmd_recommend(args: argparse.Namespace) -> int:
    catalog, health_map = load_catalog_and_health(args.catalog, args.snapshot)
    cat_map = {c["id"]: c for c in catalog.get("categories", [])}
    enriched = [enrich_tool(t, health_map, cat_map) for t in catalog.get("tools", [])]
    recs = recommend_tools(enriched, args.intent, platform=args.platform, limit=args.limit)
    if args.json:
        print(json.dumps(recs, indent=2, ensure_ascii=False))
        return 0
    if not recs:
        print("No matching Antigravity-exclusive tools found for that intent.")
        return 0
    print(f"Top {len(recs)} recommended Antigravity-exclusive tool(s) for '{args.intent}':\n")
    for idx, t in enumerate(recs, 1):
        desc = t["description_zh"] if args.lang == "zh" else t["description_en"]
        score_s = f"{t['health_score']}/100" if t.get("health_score") is not None else "N/A"
        print(f"{idx:>2}. {t['name']}  ({t['repo']})  ★{t['stars']:,} | {t['status']} ({score_s}) | Match: {t['match_score']}")
        print(f"    {desc}")
        print(f"    Signals: {', '.join(t['match_reasons'][:5])} | URL: {t['url']}")
        if t.get("install_hint"):
            print(f"    Install: {t['install_hint']}")
        print()
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    if not (2 <= len(args.tools) <= 4):
        print("[ERROR] `compare` requires between 2 and 4 tool identifiers.", file=sys.stderr)
        return 1
    catalog, health_map = load_catalog_and_health(args.catalog, args.snapshot)
    cat_map = {c["id"]: c for c in catalog.get("categories", [])}

    resolved: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for ident in args.tools:
        found = find_tool(catalog, health_map, cat_map, ident)
        if not found:
            print(f"[ERROR] Tool not found: {ident}", file=sys.stderr)
            return 1
        if found["id"] in seen_ids:
            print(f"[ERROR] Duplicate tool specified for comparison: {found['id']}", file=sys.stderr)
            return 1
        seen_ids.add(found["id"])
        resolved.append(found)

    if args.json:
        print(json.dumps({"tools": resolved}, indent=2, ensure_ascii=False))
        return 0
    if args.markdown:
        sys.stdout.write(render_comparison_markdown(resolved, lang=args.lang))
        return 0

    rows = [
        ("Repository", lambda t: t["repo"]),
        ("Category", lambda t: t["category_zh"] if args.lang == "zh" else t["category_en"]),
        ("Status", lambda t: f"{t['status']} ({t['health_score']}/100)" if t.get("health_score") is not None else t["status"]),
        ("Stars", lambda t: f"★{t.get('stars', 0):,}"),
        ("Language", lambda t: t.get("language") or "-"),
        ("License", lambda t: t.get("license") or "-"),
        ("Release", lambda t: t.get("latest_release") or "-"),
        ("Platforms", lambda t: ", ".join(t.get("platforms", []))),
        ("Tags", lambda t: ", ".join(t.get("tags", []))),
        ("Install", lambda t: t.get("install_hint") or "-"),
    ]
    col_w = 28
    print(" | ".join(["Metric".ljust(14), *[t["name"][:col_w].ljust(col_w) for t in resolved]]))
    print("-+-".join(["-" * 14, *["-" * col_w for _ in resolved]]))
    for label, getter in rows:
        cells = [str(getter(t))[:col_w].ljust(col_w) for t in resolved]
        print(" | ".join([label.ljust(14), *cells]))
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    catalog, health_map = load_catalog_and_health(args.catalog, args.snapshot)
    cat_map = {c["id"]: c for c in catalog.get("categories", [])}
    found = find_tool(catalog, health_map, cat_map, args.tool)
    if not found:
        print(f"[ERROR] Tool not found: {args.tool}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(found, indent=2, ensure_ascii=False))
        return 0

    print(f"=== {found['name']} ({found['repo']}) ===")
    print(f"ID:            {found['id']}")
    print(f"URL:           {found['url']}")
    print(f"Category:      {found['category_en']} / {found['category_zh']}")
    print(f"Status:        {found['status']} | Health Score: {found['health_score']}/100")
    print(f"Stats:         ★{found['stars']:,} | Forks: {found['forks']:,} | Language: {found['language'] or '-'} | License: {found['license'] or '-'}")
    print(f"Latest Rel:    {found['latest_release'] or '-'} | Last Push: {found['days_inactive']}d ago")
    print(f"Platforms:     {', '.join(found['platforms'])}")
    print(f"Tags:          {', '.join(found['tags'])}")
    print(f"Description:   {found['description_en']}")
    print(f"中文说明:       {found['description_zh']}")
    print(f"Exclusivity:   {found['exclusivity_reason_en']}")
    if found.get("install_hint"):
        print(f"Install Hint:  {found['install_hint']}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    catalog, health_map = load_catalog_and_health(args.catalog, args.snapshot)
    cat_map = {c["id"]: c for c in catalog.get("categories", [])}
    enriched = [enrich_tool(t, health_map, cat_map) for t in catalog.get("tools", [])]

    by_cat = Counter(t["category"] for t in enriched)
    by_lang = Counter(t["language"] or "Unspecified" for t in enriched)
    by_plat = Counter(p for t in enriched for p in t["platforms"])
    by_status = Counter(t["status"] for t in enriched)
    total_stars = sum(t["stars"] for t in enriched)
    scores = [t["health_score"] for t in enriched if isinstance(t["health_score"], (int, float))]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    payload = {
        "total_tools": len(enriched),
        "total_categories": len(catalog["categories"]),
        "total_stars": total_stars,
        "average_health_score": avg_score,
        "by_category": dict(by_cat),
        "by_status": dict(by_status),
        "by_language": dict(by_lang.most_common()),
        "by_platform": dict(by_plat.most_common()),
        "top_starred": [
            {"id": t["id"], "name": t["name"], "stars": t["stars"]}
            for t in sorted(enriched, key=lambda x: x["stars"], reverse=True)[:5]
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("=== Awesome Antigravity Tools — Ecosystem Stats ===")
    print(f"Total Tools:        {payload['total_tools']} across {payload['total_categories']} categories")
    print(f"Combined Stars:     {payload['total_stars']:,}")
    print(f"Average Health:     {payload['average_health_score']}/100")
    print(f"Status Breakdown:   {dict(by_status)}")
    print("\nBy Category:")
    for c in catalog["categories"]:
        print(f"  - {c['name_en']}: {by_cat.get(c['id'], 0)}")
    print("\nTop Languages:")
    for lang, cnt in by_lang.most_common(6):
        print(f"  - {lang}: {cnt}")
    print("\nTop Starred:")
    for item in payload["top_starred"]:
        print(f"  - {item['name']}: ★{item['stars']:,}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    import generate_docs
    import validate_catalog

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    repo = args.repo.strip().removeprefix("https://github.com/").strip("/")
    if "/" not in repo:
        print(f"[ERROR] Invalid repo slug: {repo}", file=sys.stderr)
        return 1

    name = args.name.strip() if args.name else repo.split("/", 1)[1]
    tid = args.id.strip() if args.id else re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    entry: dict[str, Any] = {
        "id": tid,
        "name": name,
        "repo": repo,
        "url": f"https://github.com/{repo}",
        "category": args.category,
        "description_en": args.desc_en.strip(),
        "description_zh": args.desc_zh.strip(),
        "exclusivity_reason_en": args.reason_en.strip(),
        "exclusivity_reason_zh": args.reason_zh.strip(),
        "platforms": [p.strip() for p in args.platforms.split(",") if p.strip()],
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "added_at": args.added_at or date.today().isoformat(),
    }
    if args.install_hint:
        entry["install_hint"] = args.install_hint.strip()
    if args.featured:
        entry["featured"] = True

    catalog["tools"].append(entry)
    catalog = validate_catalog.sort_catalog_tools(catalog)
    errors, warnings = validate_catalog.validate_catalog_data(catalog)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    for w in warnings:
        print(f"[WARN] {w}")

    args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"[+] Added '{name}' ({repo}) to {args.catalog}")

    if args.sync_docs:
        return sync_all_derived_artifacts(args.catalog, args.snapshot)
    return 0


def sync_all_derived_artifacts(catalog_path: Path, snapshot_path: Path) -> int:
    import build_site
    import export_catalog
    import generate_badges
    import generate_docs
    import validate_catalog

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog = validate_catalog.sort_catalog_tools(catalog)
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    if catalog_path.resolve() == DEFAULT_CATALOG.resolve():
        validate_catalog.sync_issue_template_categories(catalog)

    snapshot = generate_docs.load_json(snapshot_path)

    # 1. Badges
    badges = generate_badges.build_badges(catalog, snapshot)
    badges_dir = REPO_ROOT / "data" / "badges"
    badges_dir.mkdir(parents=True, exist_ok=True)
    for fname, payload in badges.items():
        (badges_dir / fname).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )

    # 2. Bilingual READMEs
    generate_docs.write_or_check(
        REPO_ROOT / "README.md", generate_docs.render_readme_en(catalog, snapshot), check_only=False
    )
    generate_docs.write_or_check(
        REPO_ROOT / "README.zh-CN.md", generate_docs.render_readme_zh(catalog, snapshot), check_only=False
    )

    # 3. Exports (COMPARISON.md, CSV, JSON-LD) & 4. Site Bundle + Feeds
    old_argv = sys.argv
    try:
        sys.argv = ["export_catalog.py", "--catalog", str(catalog_path), "--snapshot", str(snapshot_path)]
        rc_exp = export_catalog.main()
        sys.argv = ["build_site.py", "--catalog", str(catalog_path), "--snapshot", str(snapshot_path)]
        rc_site = build_site.main()
    finally:
        sys.argv = old_argv

    return 0 if (rc_exp == 0 and rc_site == 0) else 1


def cmd_verify(args: argparse.Namespace) -> int:
    import build_site
    import export_catalog
    import generate_badges
    import validate_catalog

    argv = ["--catalog", str(args.catalog)]
    if args.check_sync:
        argv.append("--check-sync")
    if args.strict_warnings:
        argv.append("--strict-warnings")
    old_argv = sys.argv
    try:
        sys.argv = ["validate_catalog.py", *argv]
        rc_val = validate_catalog.main()
        if rc_val != 0 or not args.check_sync:
            return rc_val
        if args.catalog.resolve() == DEFAULT_CATALOG.resolve():
            sys.argv = ["generate_badges.py", "--check"]
            rc_badges = generate_badges.main()
            sys.argv = ["build_site.py", "--check"]
            rc_site = build_site.main()
            sys.argv = ["export_catalog.py", "--check"]
            rc_exp = export_catalog.main()
            return 0 if (rc_badges == 0 and rc_site == 0 and rc_exp == 0) else 1
        return 0
    finally:
        sys.argv = old_argv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aat",
        description="CLI explorer and maintainer utility for awesome-antigravity-tools.",
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="Path to data/tools.json")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT, help="Path to data/health_snapshot.json")

    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List and filter curated tools")
    p_list.add_argument("-c", "--category", default="")
    p_list.add_argument("-p", "--platform", default="")
    p_list.add_argument("-t", "--tag", default="")
    p_list.add_argument("-s", "--status", default="")
    p_list.add_argument("--min-stars", type=int, default=0)
    p_list.add_argument("--sort", choices=["stars", "score", "name", "recent"], default="stars")
    p_list.add_argument("--lang", choices=["en", "zh"], default="en")
    p_list.add_argument("--json", action="store_true")

    p_search = sub.add_parser("search", help="Search curated tools by keyword")
    p_search.add_argument("query", help="Search keywords")
    p_search.add_argument("-c", "--category", default="")
    p_search.add_argument("-p", "--platform", default="")
    p_search.add_argument("--sort", choices=["stars", "score", "name", "recent"], default="stars")
    p_search.add_argument("--lang", choices=["en", "zh"], default="en")
    p_search.add_argument("--json", action="store_true")

    p_rec = sub.add_parser("recommend", help="Recommend tools by natural-language intent (EN/ZH)")
    p_rec.add_argument("intent", help="Goal, bug symptom, or capability query")
    p_rec.add_argument("-p", "--platform", default="")
    p_rec.add_argument("-n", "--limit", type=int, default=5)
    p_rec.add_argument("--lang", choices=["en", "zh"], default="en")
    p_rec.add_argument("--json", action="store_true")

    p_cmp = sub.add_parser("compare", help="Compare 2 to 4 tools side by side")
    p_cmp.add_argument("tools", nargs="+", help="Tool ids, names, or owner/repo slugs")
    p_cmp.add_argument("--markdown", action="store_true", help="Output as GitHub-flavored Markdown table")
    p_cmp.add_argument("--lang", choices=["en", "zh"], default="en")
    p_cmp.add_argument("--json", action="store_true")

    p_info = sub.add_parser("info", help="Show detailed metadata and live telemetry for one tool")
    p_info.add_argument("tool", help="Tool id, name, or owner/repo")
    p_info.add_argument("--json", action="store_true")

    p_stats = sub.add_parser("stats", help="Display ecosystem aggregate statistics")
    p_stats.add_argument("--json", action="store_true")

    p_add = sub.add_parser("add", help="Add a validated Antigravity-exclusive tool to data/tools.json")
    p_add.add_argument("--repo", required=True, help="GitHub owner/repo or URL")
    p_add.add_argument("--name", default="", help="Display name (defaults to repo name)")
    p_add.add_argument("--id", default="", help="Slug id (defaults to slugified name)")
    p_add.add_argument("--category", required=True, help="Category ID from data/tools.json")
    p_add.add_argument("--desc-en", required=True, help="English one-line description ending with period")
    p_add.add_argument("--desc-zh", required=True, help="Chinese one-line description ending with 。")
    p_add.add_argument("--reason-en", required=True, help="English Antigravity exclusivity justification")
    p_add.add_argument("--reason-zh", required=True, help="Chinese Antigravity exclusivity justification")
    p_add.add_argument("--platforms", required=True, help="Comma-separated platforms (e.g. Windows,VS Code)")
    p_add.add_argument("--tags", required=True, help="Comma-separated tags (1-5)")
    p_add.add_argument("--install-hint", default="")
    p_add.add_argument("--added-at", default="")
    p_add.add_argument("--featured", action="store_true")
    p_add.add_argument("--sync-docs", action="store_true", help="Regenerate READMEs, badges, exports, and web bundle")

    sub.add_parser("sync", help="Canonicalize catalog order and regenerate all derived docs, badges, exports, and site bundle")

    p_verify = sub.add_parser("verify", help="Validate catalog schema and optional full artifact sync")
    p_verify.add_argument("--check-sync", action="store_true")
    p_verify.add_argument("--strict-warnings", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "list":
        return cmd_list_or_search(args)
    if args.command == "search":
        return cmd_list_or_search(args, query=args.query)
    if args.command == "recommend":
        return cmd_recommend(args)
    if args.command == "compare":
        return cmd_compare(args)
    if args.command == "info":
        return cmd_info(args)
    if args.command == "stats":
        return cmd_stats(args)
    if args.command == "add":
        return cmd_add(args)
    if args.command == "sync":
        return sync_all_derived_artifacts(args.catalog, args.snapshot)
    if args.command == "verify":
        return cmd_verify(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
