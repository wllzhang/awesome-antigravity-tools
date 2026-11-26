#!/usr/bin/env python3
"""
GitHub Issue Submission Form Parser & Automated Triage Validator.

Parses markdown bodies produced by `.github/ISSUE_TEMPLATE/submit_tool.yml`,
maps category labels to canonical IDs, checks duplicates and schema rules
against `data/tools.json`, optionally verifies live repository metadata via
GitHub API, and outputs either a ready-to-merge JSON snippet or a GitHub
Issue triage comment.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_EXCLUSIONS = REPO_ROOT / "data" / "exclusions.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

GITHUB_URL_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", re.IGNORECASE)

CATEGORY_ALIASES = {
    "official cli & sdks": "official-cli-sdks",
    "ide extensions & cockpits": "ide-extensions-cockpits",
    "ide extensions & huds": "ide-extensions-cockpits",
    "platform fixes & runtime patches": "platform-fixes-runtime-patches",
    "platform fixes & system utilities": "platform-fixes-runtime-patches",
    "dedicated gateways, acp adapters & migration tooling": "dedicated-gateways-migration",
    "dedicated gateways & migration tooling": "dedicated-gateways-migration",
}

PLATFORM_ALIASES = {
    "windows": "Windows",
    "win": "Windows",
    "win32": "Windows",
    "win64": "Windows",
    "macos": "macOS",
    "mac": "macOS",
    "darwin": "macOS",
    "osx": "macOS",
    "linux": "Linux",
    "cross-platform": "Cross-Platform",
    "cross platform": "Cross-Platform",
    "all": "Cross-Platform",
    "vscode": "VS Code",
    "vs code": "VS Code",
    "visual studio code": "VS Code",
    "antigravity": "Antigravity IDE",
    "antigravity ide": "Antigravity IDE",
    "ide": "Antigravity IDE",
    "mobile": "Mobile",
    "ios": "Mobile",
    "android": "Mobile",
    "web": "Web",
    "pwa": "Web",
}


def parse_issue_form(body: str) -> dict[str, str]:
    """Parse GitHub Issue Form markdown (`### Heading\\n\\nValue`) into a dict."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current_heading is not None:
            val = "\n".join(buffer).strip()
            if val == "_No response_":
                val = ""
            sections[current_heading.lower()] = val

    for line in body.replace("\r\n", "\n").split("\n"):
        if line.startswith("### "):
            flush()
            current_heading = line[4:].strip()
            buffer = []
        else:
            buffer.append(line)
    flush()
    return sections


def extract_github_slug(url_text: str) -> str | None:
    cleaned = re.split(r"[?#]", url_text.strip(), maxsplit=1)[0].rstrip("/")
    match = GITHUB_URL_RE.search(cleaned)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2)
    repo = re.sub(r"\.git$", "", repo, flags=re.IGNORECASE).rstrip(".")
    if not owner or not repo or owner in (".", "..") or repo in (".", ".."):
        return None
    return f"{owner}/{repo}"


def normalize_platforms(raw_platforms: str) -> list[str]:
    import validate_catalog

    allowed_lower = {p.lower(): p for p in validate_catalog.ALLOWED_PLATFORMS}
    normalized: list[str] = []
    seen: set[str] = set()
    for token in re.split(r"[,;\n/|、]+", raw_platforms or ""):
        cleaned = token.strip(" `")
        if not cleaned:
            continue
        key = cleaned.lower()
        canonical = PLATFORM_ALIASES.get(key) or allowed_lower.get(key)
        if canonical and canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)
    return normalized or ["Cross-Platform"]


def resolve_category_id(raw_category: str, catalog: dict[str, Any]) -> str | None:
    cleaned = raw_category.strip().lower()
    valid_ids = {c["id"] for c in catalog.get("categories", [])}
    if cleaned in valid_ids:
        return cleaned
    if cleaned in CATEGORY_ALIASES and CATEGORY_ALIASES[cleaned] in valid_ids:
        return CATEGORY_ALIASES[cleaned]
    for c in catalog.get("categories", []):
        if cleaned == c["name_en"].lower() or cleaned == c["name_zh"].lower():
            return c["id"]
    return None


def load_exclusions_map(exclusions_path: Path = DEFAULT_EXCLUSIONS) -> dict[str, dict[str, Any]]:
    if not exclusions_path.exists():
        return {}
    data = json.loads(exclusions_path.read_text(encoding="utf-8"))
    return {
        str(item["repo"]).lower(): item
        for item in data.get("exclusions", [])
        if isinstance(item, dict) and item.get("repo")
    }


def build_candidate_entry(
    sections: dict[str, str],
    catalog: dict[str, Any],
    *,
    exclusions: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    import validate_catalog

    errors: list[str] = []

    tool_name = sections.get("tool name", "").strip()
    repo_raw = sections.get("repository / project url", "") or sections.get("repository url", "")
    slug = extract_github_slug(repo_raw)
    if not slug:
        errors.append("Repository URL must be a valid public GitHub repository link (`https://github.com/owner/repo`).")
        slug = "owner/repo"

    if not tool_name:
        tool_name = slug.split("/", 1)[1]

    raw_cat = sections.get("category", "")
    cat_id = resolve_category_id(raw_cat, catalog)
    if not cat_id:
        valid_names = [c["name_en"] for c in catalog.get("categories", [])]
        errors.append(f"Unknown category {raw_cat!r}. Expected one of: {', '.join(valid_names)}.")
        cat_id = catalog["categories"][0]["id"]

    desc_en = (
        sections.get("one-line description (english)")
        or sections.get("one-line description")
        or ""
    ).strip()
    desc_zh = sections.get("one-line description (chinese, optional)", "").strip() or f"{tool_name}：专为 Google Antigravity 打造的工程工具。"
    reason_en = (
        sections.get("antigravity exclusivity rationale")
        or sections.get("exclusivity rationale")
        or ""
    ).strip()
    reason_zh = (
        sections.get("antigravity exclusivity rationale (chinese, optional)")
        or sections.get("exclusivity rationale (chinese, optional)")
        or ""
    ).strip() or (f"专为 Google Antigravity 生态构建：{reason_en[:80]}" if reason_en else "")

    raw_platforms = sections.get("platforms", "Cross-Platform")
    platforms = normalize_platforms(raw_platforms)

    raw_tags = sections.get("tags", "CLI")
    tags = [t.strip(" `") for t in re.split(r"[,;\n]+", raw_tags) if t.strip(" `")][:5] or ["Antigravity"]

    install_hint = sections.get("install / quick-start hint (optional)", "").strip()

    existing_repos = {t["repo"].lower() for t in catalog.get("tools", [])}
    if slug.lower() in existing_repos:
        errors.append(f"Duplicate submission: `{slug}` is already listed in `data/tools.json`.")
    if slug.lower() == catalog.get("repository", "").lower():
        errors.append("Submission cannot reference `awesome-antigravity-tools` itself.")
    if exclusions and slug.lower() in exclusions:
        excl = exclusions[slug.lower()]
        errors.append(
            f"Excluded repository (`{excl.get('category', 'excluded')}`): `{slug}` is in `data/exclusions.json` — {excl.get('reason_en', '')}"
        )

    tid = re.sub(r"[^a-z0-9]+", "-", tool_name.lower()).strip("-")
    entry: dict[str, Any] = {
        "id": tid,
        "name": tool_name,
        "repo": slug,
        "url": f"https://github.com/{slug}",
        "category": cat_id,
        "description_en": desc_en,
        "description_zh": desc_zh,
        "exclusivity_reason_en": reason_en,
        "exclusivity_reason_zh": reason_zh,
        "platforms": platforms,
        "tags": tags,
        "added_at": date.today().isoformat(),
    }
    if install_hint:
        entry["install_hint"] = install_hint

    # Run canonical validator on a simulated catalog containing the candidate
    if not errors:
        sim_catalog = {
            **catalog,
            "tools": [*catalog["tools"], entry],
        }
        val_errors, _ = validate_catalog.validate_catalog_data(sim_catalog)
        # Filter only errors relevant to the newly appended index
        new_idx = len(catalog["tools"])
        for err in val_errors:
            if err.startswith(f"tools[{new_idx}]"):
                errors.append(err.split(": ", 1)[-1])

    return entry, errors


def render_triage_comment(
    entry: dict[str, Any], errors: list[str], github_meta: dict[str, Any] | None = None
) -> str:
    passed = not errors
    header = (
        "### ✅ Automated Submission Triage: Ready for Maintainer Review"
        if passed
        else "### ⚠️ Automated Submission Triage: Action Needed"
    )
    lines = ["<!-- aat-submission-triage -->", header, ""]

    if errors:
        lines.append("**Validation Issues Found:**")
        for err in errors:
            lines.append(f"- ❌ {err}")
        lines.append("")

    if github_meta:
        lines.extend(
            [
                "**Live GitHub Verification:**",
                f"- Repository: [{entry['repo']}]({entry['url']})",
                f"- Status: `{github_meta['status']}` · Stars: `{github_meta['stars']:,}` · Language: `{github_meta['language'] or '-'}` · License: `{github_meta['license'] or '-'}`",
                f"- Exclusivity Signal Score: **{github_meta['signal_score']}/100** (`{', '.join(github_meta['signals'])}`)",
                "",
            ]
        )

    if passed:
        lines.extend(
            [
                "**Generated `data/tools.json` Candidate Entry:**",
                "```json",
                json.dumps(entry, indent=2, ensure_ascii=False),
                "```",
                "",
                "> Maintainers can copy this entry into `data/tools.json` and run `python scripts/aat_cli.py sync`.",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and validate a GitHub Issue tool submission.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--exclusions", type=Path, default=DEFAULT_EXCLUSIONS)
    parser.add_argument("--input", type=Path, default=None, help="Path to markdown issue body (reads stdin if omitted)")
    parser.add_argument("--format", choices=["json", "comment"], default="comment")
    parser.add_argument("--verify-github", action="store_true", help="Verify live GitHub repo metadata via API")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    body = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    exclusions = load_exclusions_map(args.exclusions)

    sections = parse_issue_form(body)
    entry, errors = build_candidate_entry(sections, catalog, exclusions=exclusions)
    github_meta = None

    if args.verify_github and entry["repo"] != "owner/repo":
        import discover_candidates
        import importlib.util

        hc_spec = importlib.util.spec_from_file_location("health_check", SCRIPT_DIR / "health-check.py")
        hc_mod = importlib.util.module_from_spec(hc_spec)
        assert hc_spec and hc_spec.loader
        hc_spec.loader.exec_module(hc_mod)

        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
        owner, repo = entry["repo"].split("/", 1)
        code, data = hc_mod.query_github_repo(owner, repo, token=token, retries=2)
        if code == 200:
            if data.get("archived"):
                errors.append("Repository is archived on GitHub.")
            sig_score, signals = discover_candidates.score_candidate(data)
            lic_obj = data.get("license")
            github_meta = {
                "status": "ARCHIVED" if data.get("archived") else "ACTIVE",
                "stars": int(data.get("stargazers_count", 0)),
                "language": data.get("language"),
                "license": lic_obj.get("spdx_id") if isinstance(lic_obj, dict) else None,
                "signal_score": sig_score,
                "signals": signals,
            }
        elif code == 404:
            errors.append(f"GitHub repository `{entry['repo']}` returned 404 (not found or private).")
        else:
            errors.append(f"GitHub API returned HTTP {code} while verifying `{entry['repo']}`.")

    if args.format == "json":
        output = json.dumps({"valid": not errors, "errors": errors, "entry": entry, "github": github_meta}, indent=2, ensure_ascii=False) + "\n"
    else:
        output = render_triage_comment(entry, errors, github_meta=github_meta)

    if args.out:
        args.out.write_text(output, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(output)

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
