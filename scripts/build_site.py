#!/usr/bin/env python3
"""
Static Site Bundle, RSS Feed & SEO Artifact Builder for awesome-antigravity-tools.

Merges `data/tools.json`, `data/health_snapshot.json`, and `data/health_history.json`
into `docs/catalog-bundle.json`, and generates `docs/feed.xml`, `docs/sitemap.xml`,
`docs/robots.txt`, and `docs/.nojekyll` for GitHub Pages deployment.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_SNAPSHOT = REPO_ROOT / "data" / "health_snapshot.json"
DEFAULT_HISTORY = REPO_ROOT / "data" / "health_history.json"
DEFAULT_DOCS_DIR = REPO_ROOT / "docs"
DEFAULT_LOGO = REPO_ROOT / "assets" / "logo.svg"
SITE_URL = "https://wllzhang.github.io/awesome-antigravity-tools/"


def load_json_opt(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_catalog_bundle(
    catalog: dict[str, Any],
    snapshot: dict[str, Any] | None,
    history: dict[str, Any] | None,
) -> dict[str, Any]:
    health_map: dict[str, dict[str, Any]] = {}
    if snapshot:
        for r in snapshot.get("repositories", []):
            if "full_name" in r:
                health_map[r["full_name"].lower()] = r

    enriched_tools: list[dict[str, Any]] = []
    lang_counter: Counter[str] = Counter()
    plat_counter: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()
    status_counter: Counter[str] = Counter()

    for tool in catalog.get("tools", []):
        h = health_map.get(tool["repo"].lower(), {})
        status = h.get("status", "UNAUDITED")
        language = h.get("language") or "Unspecified"
        entry = {
            **tool,
            "telemetry": {
                "status": status,
                "health_score": h.get("health_score"),
                "stars": int(h.get("stars", 0)),
                "forks": int(h.get("forks", 0)),
                "open_issues": int(h.get("open_issues", 0)),
                "language": h.get("language"),
                "license": h.get("license"),
                "latest_release": h.get("latest_release"),
                "pushed_at": h.get("pushed_at"),
                "days_inactive": h.get("days_inactive"),
            },
        }
        enriched_tools.append(entry)
        lang_counter[language] += 1
        status_counter[status] += 1
        for p in tool.get("platforms", []):
            plat_counter[p] += 1
        for t in tool.get("tags", []):
            tag_counter[t] += 1

    scores = [
        t["telemetry"]["health_score"]
        for t in enriched_tools
        if isinstance(t["telemetry"]["health_score"], (int, float))
    ]
    total_stars = sum(t["telemetry"]["stars"] for t in enriched_tools)
    total_forks = sum(t["telemetry"]["forks"] for t in enriched_tools)
    healthy = status_counter.get("HEALTHY", 0)
    total = len(enriched_tools)

    generated_at = (
        snapshot.get("generated_at")
        if snapshot and snapshot.get("generated_at")
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    return {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "repository": catalog["repository"],
        "site_url": SITE_URL,
        "summary": {
            "total_tools": total,
            "total_categories": len(catalog.get("categories", [])),
            "healthy_tools": healthy,
            "health_ratio_pct": round(healthy / total * 100.0, 1) if total else 0.0,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "average_health_score": round(sum(scores) / len(scores), 1) if scores else None,
            "by_status": dict(status_counter),
            "by_language": [{"name": k, "count": v} for k, v in lang_counter.most_common()],
            "by_platform": [{"name": k, "count": v} for k, v in plat_counter.most_common()],
            "top_tags": [{"name": k, "count": v} for k, v in tag_counter.most_common(15)],
        },
        "categories": catalog.get("categories", []),
        "tools": enriched_tools,
        "history": (history.get("entries", []) if history else []),
    }


def build_rss_feed(bundle: dict[str, Any]) -> str:
    repo = bundle["repository"]
    gen_at = bundle["generated_at"]
    cat_map = {c["id"]: c["name_en"] for c in bundle["categories"]}
    sorted_tools = sorted(
        bundle["tools"],
        key=lambda t: (t.get("added_at", ""), t["telemetry"]["stars"]),
        reverse=True,
    )

    items_xml: list[str] = []
    for t in sorted_tools:
        title = escape(f"{t['name']} ({cat_map.get(t['category'], t['category'])})")
        link = escape(t["url"])
        guid = escape(f"{SITE_URL}?tool={t['id']}")
        score_disp = f"{t['telemetry']['health_score']}/100" if t["telemetry"].get("health_score") is not None else "N/A"
        desc = escape(
            f"{t['description_en']} | Exclusivity: {t['exclusivity_reason_en']} | "
            f"Stars: {t['telemetry']['stars']:,} | Health: {score_disp}"
        )
        added = t.get("added_at", "2026-11-18")
        pub_dt = datetime.fromisoformat(f"{added}T00:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
        items_xml.append(
            "    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"true\">{guid}</guid>\n"
            f"      <pubDate>{pub_dt}</pubDate>\n"
            f"      <description>{desc}</description>\n"
            "    </item>"
        )

    last_build = datetime.fromisoformat(gen_at.replace("Z", "+00:00")).strftime("%a, %d %b %Y %H:%M:%S +0000")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Awesome Antigravity Tools</title>\n"
        f"    <link>{escape(SITE_URL)}</link>\n"
        f'    <atom:link href="{escape(SITE_URL + "feed.xml")}" rel="self" type="application/rss+xml" />\n'
        "    <description>Strictly 100% Google Antigravity-exclusive engineering tools, IDE extensions, runtime hotfixes, and ACP gateways.</description>\n"
        "    <language>en-us</language>\n"
        f"    <lastBuildDate>{last_build}</lastBuildDate>\n"
        f"    <docs>https://github.com/{escape(repo)}</docs>\n"
        + "\n".join(items_xml)
        + "\n  </channel>\n</rss>\n"
    )


def build_sitemap(bundle: dict[str, Any]) -> str:
    lastmod = bundle["generated_at"][:10]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{escape(SITE_URL)}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        "    <changefreq>daily</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>\n"
        "</urlset>\n"
    )


def build_robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n"


def build_llms_txt(bundle: dict[str, Any]) -> str:
    summary = bundle["summary"]
    repo_slug = bundle["repository"]
    avg_score_disp = f"{summary['average_health_score']}/100" if summary.get("average_health_score") is not None else "N/A"
    lines = [
        "# Awesome Antigravity Tools",
        "",
        "> Strictly curated, schema-validated directory of 100% Google Antigravity-exclusive engineering tools, IDE extensions, runtime hotfixes, and ACP gateways.",
        "",
        f"- **Canonical Repository**: https://github.com/{repo_slug}",
        f"- **Interactive Explorer**: {SITE_URL}",
        f"- **Machine-Readable Bundle**: {SITE_URL}catalog-bundle.json",
        f"- **RSS Feed**: {SITE_URL}feed.xml",
        f"- **Ecosystem Pulse**: {summary['total_tools']} tools across {summary['total_categories']} categories | {summary['total_stars']:,} combined stars | {summary['healthy_tools']}/{summary['total_tools']} active ({summary['health_ratio_pct']}%) | Avg Health Score: {avg_score_disp}",
        "",
    ]

    by_cat: dict[str, list[dict[str, Any]]] = {c["id"]: [] for c in bundle["categories"]}
    for tool in bundle["tools"]:
        by_cat.setdefault(tool["category"], []).append(tool)

    for cat in bundle["categories"]:
        tools = sorted(by_cat.get(cat["id"], []), key=lambda t: (-t["telemetry"]["stars"], t["name"].lower()))
        if not tools:
            continue
        lines.append(f"## {cat['name_en']} ({len(tools)})")
        lines.append("")
        lines.append(cat["description_en"])
        lines.append("")
        for t in tools:
            tel = t["telemetry"]
            plats = ", ".join(t.get("platforms", []))
            tags = ", ".join(t.get("tags", []))
            score = f"{tel['health_score']}/100" if tel.get("health_score") is not None else "N/A"
            lines.append(
                f"- [{t['name']}]({t['url']}) (`{t['repo']}` | {tel['status']} {score} | ★{tel['stars']:,} | {plats}): "
                f"{t['description_en']} Exclusivity: {t['exclusivity_reason_en']} Tags: {tags}."
            )
            if t.get("install_hint"):
                lines.append(f"  - Install: `{t['install_hint']}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_or_check(path: Path, content: str, check_only: bool) -> bool:
    if check_only:
        if not path.exists():
            print(f"[FAIL] Missing site artifact: {path}", file=sys.stderr)
            return False
        current = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if current != content:
            print(f"[FAIL] Out of sync site artifact: {path} (run `python scripts/build_site.py`)", file=sys.stderr)
            return False
        print(f"[OK] Site artifact in sync: {path}")
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[+] Wrote site artifact: {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build docs/ catalog bundle, RSS feed, and SEO artifacts.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    parser.add_argument("--check", action="store_true", help="Verify generated artifacts are up to date")
    args = parser.parse_args()

    catalog = load_json_opt(args.catalog)
    if catalog is None:
        print(f"[ERROR] Missing catalog: {args.catalog}", file=sys.stderr)
        return 1

    snapshot = load_json_opt(args.snapshot)
    history = load_json_opt(args.history)
    bundle = build_catalog_bundle(catalog, snapshot, history)

    artifacts = {
        args.docs_dir / "catalog-bundle.json": json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
        args.docs_dir / "feed.xml": build_rss_feed(bundle),
        args.docs_dir / "sitemap.xml": build_sitemap(bundle),
        args.docs_dir / "robots.txt": build_robots(),
        args.docs_dir / "llms.txt": build_llms_txt(bundle),
        args.docs_dir / ".nojekyll": "",
    }
    if DEFAULT_LOGO.exists():
        artifacts[args.docs_dir / "logo.svg"] = DEFAULT_LOGO.read_text(encoding="utf-8").replace("\r\n", "\n")

    ok = all(write_or_check(path, content, args.check) for path, content in artifacts.items())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
