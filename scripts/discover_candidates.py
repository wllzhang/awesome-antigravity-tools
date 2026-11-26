#!/usr/bin/env python3
"""
Automated Candidate Discovery & Exclusivity Screening Radar for awesome-antigravity-tools.

Searches GitHub for emerging Antigravity-native repositories, filters out
already-cataloged projects, generic prompt dumps, and multi-agent rebrands,
and ranks candidates by an Antigravity Exclusivity & Engineering Signal Score.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_EXCLUSIONS = REPO_ROOT / "data" / "exclusions.json"

DEFAULT_QUERIES = [
    "antigravity in:name archived:false fork:false",
    "agy in:name archived:false fork:false",
    '"google antigravity" in:description archived:false fork:false',
    "antigravity acp in:name,description archived:false fork:false",
    "agy acp in:name,description archived:false fork:false",
]

CODE_LANGUAGES = {
    "Rust",
    "Go",
    "TypeScript",
    "JavaScript",
    "Python",
    "C++",
    "C",
    "C#",
    "PowerShell",
    "Swift",
    "Kotlin",
    "Java",
    "Shell",
    "Zig",
}

NATIVE_ENGINEERING_RE = re.compile(
    r"\b(agy|acp|quota|cockpit|language server|plugin\.json|vsix|extension|patch|fix|bridge|proxy|sdk|gateway|cli|hud|tauri|electron|sidecar|asar|statusline|mcp|context)\b",
    re.IGNORECASE,
)

OTHER_AGENTS = [
    "claude code",
    "codex",
    "cursor",
    "windsurf",
    "copilot",
    "opencode",
    "kiro",
    "cline",
    "gemini cli",
    "deepseek harness",
    "openclaw",
]

PROMPT_DUMP_RE = re.compile(
    r"(awesome-|prompt\s*(pack|collection|library|dump)|skill\s*pack|agent\s*skills|cheatsheet|system\s*prompts)",
    re.IGNORECASE,
)

REGION_BYPASS_RE = re.compile(
    r"(bypass.*region|region.?lock|sanctions|без\s+vpn|обход\s+ошибки|регион-блок)",
    re.IGNORECASE,
)

TOS_PROXY_RE = re.compile(
    r"(oauth.*rate\s*limit|free.*claude|claude.*proxy|reverse.*oauth|impersonat)",
    re.IGNORECASE,
)


def get_token(use_gh_cli: bool = False) -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if token or not use_gh_cli:
        return token
    try:
        proc = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5, check=False)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return ""


def search_github_repos(query: str, per_page: int = 25, token: str = "") -> list[dict[str, Any]]:
    encoded = urllib.parse.quote(query, safe="")
    url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page={per_page}"
    headers = {
        "User-Agent": "Awesome-Antigravity-Discovery/1.0",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return payload.get("items", [])
    except urllib.error.HTTPError as e:
        print(f"[WARN] Search query failed ({e.code}): {query}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[WARN] Search error ({e}): {query}", file=sys.stderr)
        return []


def score_candidate(repo_obj: dict[str, Any]) -> tuple[int, list[str]]:
    """Compute 0-100 Antigravity exclusivity & engineering signal score with reasons."""
    name = (repo_obj.get("name") or "").lower()
    desc = repo_obj.get("description") or ""
    desc_l = desc.lower()
    lang = repo_obj.get("language") or ""
    stars = int(repo_obj.get("stargazers_count", 0))
    lic_obj = repo_obj.get("license")
    lic = lic_obj.get("spdx_id") if isinstance(lic_obj, dict) else None

    score = 0
    reasons: list[str] = []

    if "antigravity" in name or re.search(r"(^|[-_])agy($|[-_])", name):
        score += 35
        reasons.append("dedicated-name")
    elif "antigravity" in desc_l:
        score += 15
        reasons.append("mentions-antigravity")

    if lang in CODE_LANGUAGES:
        score += 20
        reasons.append(f"code:{lang}")

    if NATIVE_ENGINEERING_RE.search(f"{name} {desc}"):
        score += 15
        reasons.append("engineering-keywords")

    if lic and lic not in ("NONE", "NOASSERTION"):
        score += 15
        reasons.append(f"license:{lic}")

    if stars >= 500:
        score += 15
    elif stars >= 50:
        score += 11
    elif stars >= 10:
        score += 7
    elif stars >= 3:
        score += 4

    other_hits = sum(1 for agent in OTHER_AGENTS if agent in desc_l)
    if other_hits >= 3:
        score -= 40
        reasons.append(f"penalty:multi-agent({other_hits})")
    elif other_hits == 2:
        score -= 15
        reasons.append("penalty:cross-agent(2)")

    if PROMPT_DUMP_RE.search(f"{name} {desc}"):
        score -= 35
        reasons.append("penalty:prompt-or-list")

    if REGION_BYPASS_RE.search(f"{name} {desc}"):
        score -= 45
        reasons.append("penalty:region-bypass")

    if TOS_PROXY_RE.search(f"{name} {desc}"):
        score -= 50
        reasons.append("penalty:tos-proxy-risk")

    if not desc.strip():
        score -= 15
        reasons.append("penalty:no-description")

    return max(0, min(100, score)), reasons


def load_existing_slugs(catalog_path: Path) -> set[str]:
    if not catalog_path.exists():
        return set()
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    slugs = {t["repo"].lower() for t in data.get("tools", []) if "repo" in t}
    if data.get("repository"):
        slugs.add(data["repository"].lower())
    return slugs


def load_excluded_slugs(exclusions_path: Path = DEFAULT_EXCLUSIONS) -> set[str]:
    if not exclusions_path.exists():
        return set()
    data = json.loads(exclusions_path.read_text(encoding="utf-8"))
    return {
        str(item["repo"]).lower()
        for item in data.get("exclusions", [])
        if isinstance(item, dict) and item.get("repo")
    }


def _escape_double_quoted_sh(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("$", "\\$")
        .replace("`", "\\`")
    )


def render_markdown_table(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "No new high-signal Antigravity-exclusive candidates matched the current thresholds.\n"
    lines = [
        "# Antigravity-Exclusive Candidate Discovery Radar",
        "",
        "| Score | Repository | Stars | Language | License | Last Push | Signals | Description |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- |",
    ]
    for c in candidates:
        desc = re.sub(r"\s+", " ", c["description"] or "").strip().replace("|", "\\|")[:120]
        signals = ", ".join(c["signals"])
        lines.append(
            f"| **{c['score']}** | [{c['full_name']}]({c['url']}) | {c['stars']:,} | "
            f"{c['language'] or '-'} | {c['license'] or '-'} | {c['pushed_at']} | `{signals}` | {desc} |"
        )
    return "\n".join(lines) + "\n"


def render_aat_commands(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "# No candidates matched the current thresholds.\n"
    blocks: list[str] = []
    for c in candidates:
        raw_desc = re.sub(r"\s+", " ", c.get("description") or "").strip().rstrip(".")
        desc_en = (raw_desc or "Antigravity-exclusive engineering tool") + "."
        lang_tag = re.sub(r"\s+", " ", str(c.get("language") or "CLI")).strip()
        repo_safe = _escape_double_quoted_sh(c["full_name"])
        desc_safe = _escape_double_quoted_sh(desc_en)
        tag_safe = _escape_double_quoted_sh(lang_tag)
        blocks.append(
            "\n".join(
                [
                    f"# {c['full_name']} (score={c['score']}, stars={c['stars']}, pushed={c['pushed_at']})",
                    "python scripts/aat_cli.py add \\",
                    f"  --repo \"{repo_safe}\" \\",
                    "  --category \"ide-extensions-cockpits\" \\",
                    f"  --desc-en \"{desc_safe}\" \\",
                    "  --desc-zh \"专为 Google Antigravity 打造的工程工具。\" \\",
                    "  --reason-en \"Built exclusively for Google Antigravity runtime workflows.\" \\",
                    "  --reason-zh \"专为 Google Antigravity 运行时工作流构建。\" \\",
                    "  --platforms \"Cross-Platform\" \\",
                    f"  --tags \"{tag_safe},Antigravity\" \\",
                    "  --sync-docs",
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def filter_and_rank_candidates(
    items: list[dict[str, Any]],
    existing_slugs: set[str],
    *,
    min_stars: int = 5,
    min_score: int = 55,
    max_days_inactive: int = 180,
    sort_by: str = "score",
    limit: int = 20,
    now_dt: datetime | None = None,
) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    now = now_dt or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    existing_l = {s.lower() for s in existing_slugs}
    dedup: dict[str, dict[str, Any]] = {}
    for item in items:
        full_name = item.get("full_name", "")
        if not full_name:
            continue
        key = full_name.lower()
        if key in existing_l or key in dedup:
            continue
        if item.get("archived") or item.get("fork") or item.get("disabled"):
            continue
        stars = int(item.get("stargazers_count", 0))
        if stars < min_stars:
            continue

        pushed_raw = item.get("pushed_at") or ""
        days_inactive: int | None = None
        if pushed_raw:
            try:
                pushed_dt = datetime.fromisoformat(pushed_raw.replace("Z", "+00:00"))
                if pushed_dt.tzinfo is None:
                    pushed_dt = pushed_dt.replace(tzinfo=timezone.utc)
                days_inactive = max(0, (now - pushed_dt).days)
            except ValueError:
                days_inactive = None

        if max_days_inactive > 0 and days_inactive is not None and days_inactive > max_days_inactive:
            continue

        score, signals = score_candidate(item)
        if score < min_score:
            continue
        lic_obj = item.get("license")
        dedup[key] = {
            "full_name": full_name,
            "url": item.get("html_url", f"https://github.com/{full_name}"),
            "stars": stars,
            "language": item.get("language"),
            "license": lic_obj.get("spdx_id") if isinstance(lic_obj, dict) else None,
            "pushed_at": pushed_raw[:10],
            "days_inactive": days_inactive,
            "description": (item.get("description") or "").strip(),
            "score": score,
            "signals": signals,
        }

    values = list(dedup.values())
    if sort_by == "stars":
        values.sort(key=lambda x: (x["stars"], x["score"]), reverse=True)
    elif sort_by == "recent":
        values.sort(
            key=lambda x: (
                x["days_inactive"] if x["days_inactive"] is not None else 99999,
                -x["score"],
                -x["stars"],
            )
        )
    else:
        values.sort(key=lambda x: (x["score"], x["stars"]), reverse=True)
    return values[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover emerging Antigravity-exclusive tools on GitHub.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--exclusions", type=Path, default=DEFAULT_EXCLUSIONS)
    parser.add_argument("--include-excluded", action="store_true", help="Do not filter out repos listed in data/exclusions.json")
    parser.add_argument("--min-stars", type=int, default=5)
    parser.add_argument("--min-score", type=int, default=55)
    parser.add_argument("--max-days-inactive", type=int, default=180, help="Exclude repos inactive >N days (0 disables)")
    parser.add_argument("--sort", choices=["score", "stars", "recent"], default="score")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--format", choices=["md", "json", "aat-cmd"], default="md")
    parser.add_argument("--out", type=Path, default=None, help="Optional output file path")
    parser.add_argument("--use-gh-cli", action="store_true")
    args = parser.parse_args()

    token = get_token(use_gh_cli=args.use_gh_cli)
    existing = load_existing_slugs(args.catalog)
    if not args.include_excluded:
        existing |= load_excluded_slugs(args.exclusions)

    raw_items: list[dict[str, Any]] = []
    for query in DEFAULT_QUERIES:
        raw_items.extend(search_github_repos(query, per_page=25, token=token))

    ranked = filter_and_rank_candidates(
        raw_items,
        existing,
        min_stars=args.min_stars,
        min_score=args.min_score,
        max_days_inactive=args.max_days_inactive,
        sort_by=args.sort,
        limit=args.limit,
    )
    if args.format == "json":
        output = json.dumps(ranked, indent=2, ensure_ascii=False) + "\n"
    elif args.format == "aat-cmd":
        output = render_aat_commands(ranked)
    else:
        output = render_markdown_table(ranked)

    if args.out:
        args.out.write_text(output, encoding="utf-8", newline="\n")
        print(f"[+] Wrote {len(ranked)} candidates to {args.out}")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
