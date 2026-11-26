#!/usr/bin/env python3
"""
Deterministic bilingual README generator for awesome-antigravity-tools.

Reads the canonical catalog (`data/tools.json`) and optional health snapshot
(`data/health_snapshot.json`) to generate `README.md` and `README.zh-CN.md`
with guaranteed EN/ZH parity, alphabetical ordering, and accurate badges.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_SNAPSHOT = REPO_ROOT / "data" / "health_snapshot.json"


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def github_anchor(heading: str) -> str:
    """Replicate GitHub's exact heading anchor slugification (including U+FE0F marks & CJK)."""
    slug = heading.strip().lower()
    allowed_categories = {"Lu", "Ll", "Lt", "Lm", "Lo", "Nd", "Nl", "No", "Mn", "Mc", "Pc"}
    cleaned = [
        ch for ch in slug if ch in (" ", "-") or unicodedata.category(ch) in allowed_categories
    ]
    return "".join(cleaned).replace(" ", "-")


def format_number(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def compute_health_summary(
    catalog: dict[str, Any], snapshot: dict[str, Any] | None
) -> dict[str, Any]:
    total_tools = len(catalog.get("tools", []))
    if not snapshot:
        return {
            "total": total_tools,
            "healthy": total_tools,
            "ratio_pct": 100.0 if total_tools else 0.0,
            "total_stars": 0,
            "avg_score": None,
            "has_snapshot": False,
            "by_repo": {},
        }

    repos_list = snapshot.get("repositories", [])
    by_repo = {r["full_name"].lower(): r for r in repos_list if "full_name" in r}
    catalog_slugs = {t["repo"].lower() for t in catalog.get("tools", [])}
    matched = [by_repo[s] for s in catalog_slugs if s in by_repo]

    healthy = sum(1 for r in matched if r.get("status") == "HEALTHY")
    total_audited = len(matched) if matched else total_tools
    ratio_pct = (healthy / total_audited * 100.0) if total_audited else 0.0
    total_stars = sum(int(r.get("stars", 0)) for r in matched)
    scores = [r["health_score"] for r in matched if isinstance(r.get("health_score"), (int, float))]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    return {
        "total": total_tools,
        "audited": total_audited,
        "healthy": healthy,
        "ratio_pct": ratio_pct,
        "total_stars": total_stars,
        "avg_score": avg_score,
        "has_snapshot": bool(matched),
        "generated_at": snapshot.get("generated_at", ""),
        "by_repo": by_repo,
    }


def badge_color_for_ratio(ratio_pct: float) -> str:
    if ratio_pct >= 90.0:
        return "brightgreen"
    if ratio_pct >= 75.0:
        return "yellowgreen"
    if ratio_pct >= 50.0:
        return "yellow"
    return "orange"


def render_tool_line(tool: dict[str, Any], lang: str, health_map: dict[str, Any]) -> str:
    desc = tool["description_en"] if lang == "en" else tool["description_zh"]
    tags_str = " ".join(f"`{tag}`" for tag in tool["tags"])
    prefix = ""
    repo_info = health_map.get(tool["repo"].lower())
    if repo_info and repo_info.get("status") == "ARCHIVED":
        prefix = "`[Archived]` "
    return f"- [{tool['name']}]({tool['url']}) - {prefix}{desc} {tags_str}"


def group_tools_by_category(catalog: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {c["id"]: [] for c in catalog["categories"]}
    for tool in catalog["tools"]:
        grouped.setdefault(tool["category"], []).append(tool)
    for cat_id in grouped:
        grouped[cat_id].sort(key=lambda t: t["name"].lower())
    return grouped


def render_readme_en(catalog: dict[str, Any], snapshot: dict[str, Any] | None) -> str:
    repo = catalog["repository"]
    summary = compute_health_summary(catalog, snapshot)
    grouped = group_tools_by_category(catalog)
    health_map = summary["by_repo"]

    ratio_color = badge_color_for_ratio(summary["ratio_pct"])
    if summary["has_snapshot"]:
        health_msg = quote(f"{summary['healthy']}/{summary['audited']} Active ({summary['ratio_pct']:.0f}%)")
    else:
        health_msg = quote(f"{summary['total']} Curated")
    count_msg = quote(f"{summary['total']} Tools")

    lines: list[str] = [
        "<!-- AUTO-GENERATED FROM data/tools.json BY scripts/generate_docs.py — DO NOT EDIT DIRECTLY -->",
        "",
        "# Awesome Antigravity Tools [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)",
        "[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)",
        f"[![Curated Tools](https://img.shields.io/badge/Curated-{count_msg}-4285F4.svg)](#contents)",
        f"[![Daily Health Audit](https://github.com/{repo}/actions/workflows/health-check.yml/badge.svg)](https://github.com/{repo}/actions/workflows/health-check.yml)",
        f"[![Repository Health](https://img.shields.io/badge/Health%20Audit-{health_msg}-{ratio_color})](health_report.md)",
        "[![Antigravity](https://img.shields.io/badge/Google-Antigravity-4285F4.svg?logo=google)](https://antigravity.google)",
        "",
        "> A strictly curated, schema-validated directory of **100% native, dedicated tools, IDE extensions, runtime hotfixes, and engineering gateways** built exclusively for Google Antigravity.",
        "",
        f"[🌐 Interactive Web Explorer](https://wllzhang.github.io/awesome-antigravity-tools/) · [📊 Comparison Matrix](COMPARISON.md) · [🤖 LLMs.txt](https://wllzhang.github.io/awesome-antigravity-tools/llms.txt) · [中文文档 (Chinese)](README.zh-CN.md) · [Contributing Guidelines](CONTRIBUTING.md) · [Daily Health Report](health_report.md) · [Submit a Tool](https://github.com/{repo}/issues/new/choose)",
        "",
        "---",
        "",
        "## 🎯 Our Manifesto: Strictly Antigravity-Exclusive",
        "",
        'Most "awesome" lists in the AI agent space are flooded with two types of noise:',
        "1. **Generic Markdown prompt dumps** (`SKILL.md`) that work identically across Claude Code, Cursor, and Codex.",
        '2. **Generic multi-agent tools** that were designed for other platforms and merely slapped "Antigravity" onto their tags.',
        "",
        "**This repository rejects all generic padding.** Every single project curated here is **100% dedicated to Google Antigravity**:",
        "- Built specifically for the Antigravity IDE, CLI (`agy`), or `agy acp` protocol.",
        "- Directly fixes critical Antigravity bugs, OS runtime limitations, or telemetry blind spots.",
        "- Verified daily by our automated health audit (`scripts/health-check.py`) and backed by a single-source-of-truth JSON catalog (`data/tools.json`).",
        "",
    ]

    if summary["has_snapshot"]:
        stars_disp = format_number(summary["total_stars"])
        avg_disp = f"`{summary['avg_score']}/100`" if summary["avg_score"] is not None else "N/A"
        lines.extend(
            [
                f"> **Ecosystem Pulse**: `{summary['total']}` curated tools across `{len(catalog['categories'])}` categories · `{stars_disp}` combined GitHub stars · `{summary['healthy']}/{summary['audited']}` active (`{summary['ratio_pct']:.1f}%`) · Avg Health Score: {avg_disp} ([Full Audit](health_report.md))",
                "",
            ]
        )

    lines.extend(["---", "", "## Contents", ""])
    for cat in catalog["categories"]:
        heading = f"{cat['icon']} {cat['name_en']}"
        anchor = github_anchor(heading)
        count = len(grouped.get(cat["id"], []))
        lines.append(f"- [{cat['name_en']} ({count})](#{anchor})")
    lines.extend(
        [
            f"- [Badge](#{github_anchor('🏷️ Badge')})",
            f"- [Contributing](#{github_anchor('🤝 Contributing')})",
            "",
            "---",
            "",
        ]
    )

    for cat in catalog["categories"]:
        tools = grouped.get(cat["id"], [])
        if not tools:
            continue
        lines.append(f"## {cat['icon']} {cat['name_en']}")
        lines.append("")
        lines.append(cat["description_en"])
        lines.append("")
        for tool in tools:
            lines.append(render_tool_line(tool, "en", health_map))
        lines.extend(["", "---", ""])

    lines.extend(
        [
            "## 🏷️ Badge",
            "",
            "If your tool is featured in this list, add this badge to your README:",
            "",
            f"[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/{repo})",
            "",
            "```markdown",
            f"[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/{repo})",
            "```",
            "",
            "---",
            "",
            "## 🤝 Contributing",
            "",
            "Contributions are welcome! All entries are managed in [`data/tools.json`](data/tools.json) and rendered deterministically into both English and Chinese READMEs via `python scripts/generate_docs.py`.",
            "",
            "> **Tip**: This repository also ships as a native Antigravity plugin ([`plugin.json`](plugin.json) + `antigravity-tools-advisor` skill) and CLI (`python scripts/aat_cli.py recommend \"<intent>\"`, `doctor`, `search <query>`).",
            "",
            "Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request or issue.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_zh(catalog: dict[str, Any], snapshot: dict[str, Any] | None) -> str:
    repo = catalog["repository"]
    summary = compute_health_summary(catalog, snapshot)
    grouped = group_tools_by_category(catalog)
    health_map = summary["by_repo"]

    ratio_color = badge_color_for_ratio(summary["ratio_pct"])
    if summary["has_snapshot"]:
        health_msg = quote(f"{summary['healthy']}/{summary['audited']} 活跃 ({summary['ratio_pct']:.0f}%)")
    else:
        health_msg = quote(f"已收录 {summary['total']} 项")
    count_msg = quote(f"{summary['total']} 个工具")

    lines: list[str] = [
        "<!-- 由 scripts/generate_docs.py 基于 data/tools.json 自动生成 — 请勿直接手动编辑 -->",
        "",
        "# Awesome Antigravity Tools (Antigravity 专有工程工具精选榜) [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)",
        "[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.zh-CN.md)",
        f"[![收录工具数](https://img.shields.io/badge/精选收录-{count_msg}-4285F4.svg)](#目录)",
        f"[![每日健康巡检](https://github.com/{repo}/actions/workflows/health-check.yml/badge.svg)](https://github.com/{repo}/actions/workflows/health-check.yml)",
        f"[![巡检状态](https://img.shields.io/badge/巡检状态-{health_msg}-{ratio_color})](health_report.zh-CN.md)",
        "[![Antigravity](https://img.shields.io/badge/Google-Antigravity-4285F4.svg?logo=google)](https://antigravity.google)",
        "",
        "> 纯粹且极致：由 Schema 严格校验的精选目录，只收录 **100% 专为 Google Antigravity 设计研发** 的原生 IDE 扩展、底层系统补丁、运行时热修补与专用工程网关。",
        "",
        f"[🌐 交互式网页目录](https://wllzhang.github.io/awesome-antigravity-tools/?lang=zh) · [📊 横向对比矩阵](COMPARISON.md) · [🤖 LLMs.txt](https://wllzhang.github.io/awesome-antigravity-tools/llms.txt) · [English Documentation](README.md) · [贡献指南](CONTRIBUTING.zh-CN.md) · [每日健康与清退报告](health_report.zh-CN.md) · [提交新工具](https://github.com/{repo}/issues/new/choose)",
        "",
        "---",
        "",
        "## 🎯 我们的纯粹性原则：严拒泛用充数，只收专有原生",
        "",
        "当前 AI 编程领域的绝大多数 Awesome 列表充斥着两大臃肿噪音：",
        "1. **纯 Markdown 提示词堆砌**（`SKILL.md`）：在 Claude Code、Cursor、Codex 间无差别通用，毫无工程壁垒；",
        "2. **跨平台泛用工具贴牌**：原本为 Claude Code 或通用 LLM 开发，仅在 README 里贴一个“Antigravity”关键词引流。",
        "",
        "**本项目坚决拒绝一切泛用充数。** 列表中收录的每一个项目，**其核心使命 100% 专为 Google Antigravity 而生**：",
        "- 专为 Antigravity IDE、官方 CLI (`agy`) 或 `agy acp` 底层协议深度研发；",
        "- 正面攻克 Antigravity 运行时的特定缺陷、系统级死锁或配额盲区；",
        "- 由统一数据源 `data/tools.json` 驱动，每日自动执行健康度与活性巡检（`scripts/health-check.py`）。",
        "",
    ]

    if summary["has_snapshot"]:
        stars_disp = format_number(summary["total_stars"])
        avg_disp = f"`{summary['avg_score']}/100`" if summary["avg_score"] is not None else "N/A"
        lines.extend(
            [
                f"> **生态脉搏**：共收录 `{summary['total']}` 款专有工具（`{len(catalog['categories'])}` 个分类）· 合计 `{stars_disp}` Stars · `{summary['healthy']}/{summary['audited']}` 活跃（`{summary['ratio_pct']:.1f}%`）· 平均健康分：{avg_disp}（[完整巡检报告](health_report.zh-CN.md)）",
                "",
            ]
        )

    lines.extend(["---", "", "## 目录", ""])
    for cat in catalog["categories"]:
        heading = f"{cat['icon']} {cat['name_zh']}"
        anchor = github_anchor(heading)
        count = len(grouped.get(cat["id"], []))
        lines.append(f"- [{cat['icon']} {cat['name_zh']} ({count})](#{anchor})")
    lines.extend(
        [
            f"- [🏷️ 项目徽章 (Badge)](#{github_anchor('🏷️ 项目徽章 (Badge)')})",
            f"- [🤝 参与贡献](#{github_anchor('🤝 参与贡献')})",
            "",
            "---",
            "",
        ]
    )

    for cat in catalog["categories"]:
        tools = grouped.get(cat["id"], [])
        if not tools:
            continue
        lines.append(f"## {cat['icon']} {cat['name_zh']}")
        lines.append("")
        lines.append(cat["description_zh"])
        lines.append("")
        for tool in tools:
            lines.append(render_tool_line(tool, "zh", health_map))
        lines.extend(["", "---", ""])

    lines.extend(
        [
            "## 🏷️ 项目徽章 (Badge)",
            "",
            "如果您的工具已被收录到本榜单，欢迎在您的 README 中展示收录徽章：",
            "",
            f"[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/{repo})",
            "",
            "```markdown",
            f"[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/{repo})",
            "```",
            "",
            "---",
            "",
            "## 🤝 参与贡献",
            "",
            "欢迎提交您的专有工具！所有收录条目统一维护于 [`data/tools.json`](data/tools.json)，通过 `python scripts/generate_docs.py` 自动同步生成中英文文档。",
            "",
            "> **提示**：本仓库本身亦遵循 Antigravity 原生插件规范（[`plugin.json`](plugin.json) + `antigravity-tools-advisor` 技能），同时内置零依赖 CLI（`python scripts/aat_cli.py recommend \"<意图>\"`、`doctor`、`search <关键词>`）。",
            "",
            "在提交前请阅读我们的 [贡献指南](CONTRIBUTING.zh-CN.md) 与 [行为准则](CODE_OF_CONDUCT.md)。",
            "",
        ]
    )
    return "\n".join(lines)


def write_or_check(path: Path, content: str, check_only: bool) -> bool:
    if check_only:
        if not path.exists():
            print(f"[FAIL] Missing generated file: {path}", file=sys.stderr)
            return False
        current = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if current != content:
            print(f"[FAIL] Out of sync: {path} (run `python scripts/generate_docs.py`)", file=sys.stderr)
            return False
        print(f"[OK] In sync: {path}")
        return True

    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[+] Generated {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate README.md and README.zh-CN.md from data/tools.json."
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="Path to tools.json")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT, help="Optional path to health_snapshot.json")
    parser.add_argument("--out-en", type=Path, default=REPO_ROOT / "README.md", help="Output path for English README")
    parser.add_argument("--out-zh", type=Path, default=REPO_ROOT / "README.zh-CN.md", help="Output path for Chinese README")
    parser.add_argument("--check", action="store_true", help="Verify READMEs match generated output without writing")
    args = parser.parse_args()

    catalog = load_json(args.catalog)
    if catalog is None:
        print(f"[ERROR] Catalog not found: {args.catalog}", file=sys.stderr)
        return 1

    snapshot = load_json(args.snapshot)
    en_content = render_readme_en(catalog, snapshot)
    zh_content = render_readme_zh(catalog, snapshot)

    ok_en = write_or_check(args.out_en, en_content, args.check)
    ok_zh = write_or_check(args.out_zh, zh_content, args.check)
    return 0 if (ok_en and ok_zh) else 1


if __name__ == "__main__":
    raise SystemExit(main())
