#!/usr/bin/env python3
"""
Strict zero-dependency catalog validator and linter for awesome-antigravity-tools.

Validates `data/tools.json` against structural, semantic, formatting, and
exclusivity quality gates, and optionally enforces README synchronization.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_EXCLUSIONS = REPO_ROOT / "data" / "exclusions.json"
DEFAULT_SCHEMA = REPO_ROOT / "data" / "catalog.schema.json"
DEFAULT_ISSUE_TEMPLATE = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "submit_tool.yml"

ALLOWED_EXCLUSION_CATEGORIES = {
    "tos-risk-proxy",
    "region-bypass",
    "cross-agent",
    "prompt-pack",
    "pruned-stale",
    "pruned-dead",
}
ALLOWED_EXCLUSION_TOP_KEYS = {"schema_version", "repository", "exclusions"}
REQUIRED_EXCLUSION_KEYS = {"repo", "category", "reason_en", "reason_zh", "excluded_at"}

ALLOWED_PLATFORMS = {
    "Windows",
    "macOS",
    "Linux",
    "Cross-Platform",
    "VS Code",
    "Antigravity IDE",
    "Mobile",
    "Web",
}

ALLOWED_TOP_KEYS = {"schema_version", "repository", "categories", "tools"}
ALLOWED_CATEGORY_KEYS = {"id", "icon", "name_en", "name_zh", "description_en", "description_zh"}
REQUIRED_TOOL_KEYS = {
    "id",
    "name",
    "repo",
    "url",
    "category",
    "description_en",
    "description_zh",
    "exclusivity_reason_en",
    "exclusivity_reason_zh",
    "platforms",
    "tags",
    "added_at",
}
OPTIONAL_TOOL_KEYS = {"install_hint", "featured", "archived_note"}
ALLOWED_TOOL_KEYS = REQUIRED_TOOL_KEYS | OPTIONAL_TOOL_KEYS

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
HYPERBOLE_RE = re.compile(r"\b(the best|ultimate|revolutionary|game[- ]?changing|world[- ]?class)\b", re.IGNORECASE)


def validate_catalog_data(data: Any) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a loaded catalog structure."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return ["Catalog root must be a JSON object."], warnings

    missing_top = ALLOWED_TOP_KEYS - set(data.keys())
    extra_top = set(data.keys()) - ALLOWED_TOP_KEYS
    if missing_top:
        errors.append(f"Missing top-level keys: {sorted(missing_top)}")
    if extra_top:
        errors.append(f"Unexpected top-level keys: {sorted(extra_top)}")

    schema_ver = data.get("schema_version")
    if not isinstance(schema_ver, str) or not SEMVER_RE.match(schema_ver):
        errors.append(f"Invalid schema_version: {schema_ver!r}")

    self_repo = data.get("repository", "")
    if not isinstance(self_repo, str) or not REPO_RE.match(self_repo):
        errors.append(f"Invalid repository slug: {self_repo!r}")

    categories = data.get("categories")
    category_ids: list[str] = []
    category_set: set[str] = set()
    if not isinstance(categories, list) or not categories:
        errors.append("`categories` must be a non-empty array.")
    else:
        for idx, cat in enumerate(categories):
            prefix = f"categories[{idx}]"
            if not isinstance(cat, dict):
                errors.append(f"{prefix} must be an object.")
                continue
            missing_c = ALLOWED_CATEGORY_KEYS - set(cat.keys())
            extra_c = set(cat.keys()) - ALLOWED_CATEGORY_KEYS
            if missing_c:
                errors.append(f"{prefix} missing keys: {sorted(missing_c)}")
            if extra_c:
                errors.append(f"{prefix} unexpected keys: {sorted(extra_c)}")
            cid = cat.get("id", "")
            if not isinstance(cid, str) or not SLUG_RE.match(cid):
                errors.append(f"{prefix}.id invalid slug: {cid!r}")
            elif cid in category_set:
                errors.append(f"Duplicate category id: {cid!r}")
            else:
                category_set.add(cid)
                category_ids.append(cid)

            for field in ("icon", "name_en", "name_zh", "description_en", "description_zh"):
                val = cat.get(field)
                if not isinstance(val, str) or not val.strip():
                    errors.append(f"{prefix}.{field} must be a non-empty string.")

    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        errors.append("`tools` must be a non-empty array.")
        return errors, warnings

    seen_ids: set[str] = set()
    seen_repos: set[str] = set()
    by_category_names: dict[str, list[str]] = {cid: [] for cid in category_ids}

    for idx, tool in enumerate(tools):
        prefix = f"tools[{idx}]"
        if not isinstance(tool, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        keys = set(tool.keys())
        missing_t = REQUIRED_TOOL_KEYS - keys
        extra_t = keys - ALLOWED_TOOL_KEYS
        if missing_t:
            errors.append(f"{prefix} missing keys: {sorted(missing_t)}")
        if extra_t:
            errors.append(f"{prefix} unexpected keys: {sorted(extra_t)}")

        tid = tool.get("id", "")
        label = f"tools[{idx}]({tid or '?'})"
        if not isinstance(tid, str) or not SLUG_RE.match(tid):
            errors.append(f"{label}: invalid slug id {tid!r}")
        elif tid in seen_ids:
            errors.append(f"{label}: duplicate tool id {tid!r}")
        else:
            seen_ids.add(tid)

        name = tool.get("name", "")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}: name must be a non-empty string.")

        repo = tool.get("repo", "")
        if not isinstance(repo, str) or not REPO_RE.match(repo):
            errors.append(f"{label}: invalid GitHub repo slug {repo!r}")
        else:
            repo_lower = repo.lower()
            if repo_lower == str(self_repo).lower():
                errors.append(f"{label}: catalog must not reference itself ({repo}).")
            if repo_lower in seen_repos:
                errors.append(f"{label}: duplicate repository {repo!r}")
            seen_repos.add(repo_lower)

        url = tool.get("url", "")
        expected_url = f"https://github.com/{repo}"
        if url != expected_url:
            errors.append(f"{label}: url {url!r} must exactly equal {expected_url!r}")

        cat = tool.get("category", "")
        if cat not in category_set:
            errors.append(f"{label}: unknown category {cat!r}")
        else:
            by_category_names[cat].append(str(name))

        desc_en = tool.get("description_en", "")
        if not isinstance(desc_en, str) or len(desc_en) < 15 or len(desc_en) > 240:
            errors.append(f"{label}: description_en must be 15-240 chars.")
        else:
            if not (desc_en[0].isupper() or desc_en[0].isdigit()):
                errors.append(f"{label}: description_en must start with a capital letter.")
            if not desc_en.endswith("."):
                errors.append(f"{label}: description_en must end with a period.")
            if HYPERBOLE_RE.search(desc_en):
                warnings.append(f"{label}: description_en contains promotional language.")

        desc_zh = tool.get("description_zh", "")
        if not isinstance(desc_zh, str) or len(desc_zh) < 8 or len(desc_zh) > 160:
            errors.append(f"{label}: description_zh must be 8-160 chars.")
        elif not desc_zh.endswith("。"):
            errors.append(f"{label}: description_zh must end with '。'.")

        for reason_key in ("exclusivity_reason_en", "exclusivity_reason_zh"):
            val = tool.get(reason_key, "")
            if not isinstance(val, str) or len(val.strip()) < 6:
                errors.append(f"{label}: {reason_key} must provide a clear Antigravity exclusivity rationale.")

        platforms = tool.get("platforms")
        if not isinstance(platforms, list) or not platforms:
            errors.append(f"{label}: platforms must be a non-empty list.")
        else:
            if len(set(platforms)) != len(platforms):
                errors.append(f"{label}: duplicate entries in platforms.")
            unknown_p = [p for p in platforms if p not in ALLOWED_PLATFORMS]
            if unknown_p:
                errors.append(f"{label}: invalid platforms {unknown_p}; allowed: {sorted(ALLOWED_PLATFORMS)}")

        tags = tool.get("tags")
        if not isinstance(tags, list) or not (1 <= len(tags) <= 5):
            errors.append(f"{label}: tags must contain 1 to 5 items.")
        else:
            if len(set(tags)) != len(tags):
                errors.append(f"{label}: duplicate entries in tags.")
            for tag in tags:
                if not isinstance(tag, str) or not (1 <= len(tag) <= 24):
                    errors.append(f"{label}: invalid tag {tag!r}")

        added_at = tool.get("added_at", "")
        if not isinstance(added_at, str) or not DATE_RE.match(added_at):
            errors.append(f"{label}: added_at must be YYYY-MM-DD.")
        else:
            try:
                date.fromisoformat(added_at)
            except ValueError:
                errors.append(f"{label}: added_at is not a valid calendar date: {added_at!r}")

        if "featured" in tool and not isinstance(tool["featured"], bool):
            errors.append(f"{label}: featured must be a boolean.")
        if "install_hint" in tool and not isinstance(tool["install_hint"], str):
            errors.append(f"{label}: install_hint must be a string.")
        if "archived_note" in tool and not isinstance(tool["archived_note"], str):
            errors.append(f"{label}: archived_note must be a string.")

    # Verify canonical alphabetical ordering within each category
    for cid, names in by_category_names.items():
        if names != sorted(names, key=lambda s: s.lower()):
            warnings.append(
                f"Category '{cid}' tools are not alphabetically sorted in tools.json: {names}"
            )

    return errors, warnings


def _is_valid_repo_slug(repo: Any) -> bool:
    if not isinstance(repo, str) or not REPO_RE.match(repo):
        return False
    if repo.lower().endswith(".git"):
        return False
    owner, name = repo.split("/", 1)
    return owner not in (".", "..") and name not in (".", "..")


def validate_exclusions_data(exclusions_data: Any, catalog_data: Any = None) -> list[str]:
    """Validate data/exclusions.json structure and verify zero overlap with active catalog tools."""
    errors: list[str] = []
    if not isinstance(exclusions_data, dict):
        return ["Exclusions root must be a JSON object."]

    missing_top = ALLOWED_EXCLUSION_TOP_KEYS - set(exclusions_data.keys())
    extra_top = set(exclusions_data.keys()) - ALLOWED_EXCLUSION_TOP_KEYS
    if missing_top:
        errors.append(f"Exclusions missing top-level keys: {sorted(missing_top)}")
    if extra_top:
        errors.append(f"Exclusions unexpected top-level keys: {sorted(extra_top)}")

    schema_ver = exclusions_data.get("schema_version")
    if not isinstance(schema_ver, str) or not SEMVER_RE.match(schema_ver):
        errors.append(f"Exclusions invalid schema_version: {schema_ver!r}")

    self_repo = exclusions_data.get("repository", "")
    if not _is_valid_repo_slug(self_repo):
        errors.append(f"Exclusions invalid repository slug: {self_repo!r}")

    entries = exclusions_data.get("exclusions")
    if not isinstance(entries, list):
        errors.append("`exclusions` must be an array.")
        return errors

    active_repos: set[str] = set()
    if isinstance(catalog_data, dict):
        tools_list = catalog_data.get("tools")
        if isinstance(tools_list, list):
            active_repos = {
                str(t.get("repo", "")).lower()
                for t in tools_list
                if isinstance(t, dict) and t.get("repo")
            }

    seen_repos: set[str] = set()
    for idx, entry in enumerate(entries):
        prefix = f"exclusions[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        keys = set(entry.keys())
        missing_e = REQUIRED_EXCLUSION_KEYS - keys
        extra_e = keys - REQUIRED_EXCLUSION_KEYS
        if missing_e:
            errors.append(f"{prefix} missing keys: {sorted(missing_e)}")
        if extra_e:
            errors.append(f"{prefix} unexpected keys: {sorted(extra_e)}")

        repo = entry.get("repo", "")
        if not _is_valid_repo_slug(repo):
            errors.append(f"{prefix}: invalid GitHub repo slug {repo!r}")
        else:
            repo_l = repo.lower()
            if repo_l == str(self_repo).lower():
                errors.append(f"{prefix}: exclusions must not reference itself ({repo}).")
            if repo_l in seen_repos:
                errors.append(f"{prefix}: duplicate excluded repository {repo!r}")
            if repo_l in active_repos:
                errors.append(f"{prefix}: repository {repo!r} overlaps with active catalog tools")
            seen_repos.add(repo_l)

        cat = entry.get("category", "")
        if not isinstance(cat, str) or cat not in ALLOWED_EXCLUSION_CATEGORIES:
            errors.append(
                f"{prefix}: invalid exclusion category {cat!r}; allowed: {sorted(ALLOWED_EXCLUSION_CATEGORIES)}"
            )

        for rkey in ("reason_en", "reason_zh"):
            val = entry.get(rkey, "")
            if not isinstance(val, str) or len(val.strip()) < 6:
                errors.append(f"{prefix}: {rkey} must be a clear non-empty explanation.")

        excl_at = entry.get("excluded_at", "")
        if not isinstance(excl_at, str) or not DATE_RE.match(excl_at):
            errors.append(f"{prefix}: excluded_at must be YYYY-MM-DD.")
        else:
            try:
                date.fromisoformat(excl_at)
            except ValueError:
                errors.append(f"{prefix}: excluded_at is not a valid calendar date: {excl_at!r}")

    return errors


def sort_catalog_tools(data: dict[str, Any]) -> dict[str, Any]:
    cat_rank = {c["id"]: i for i, c in enumerate(data.get("categories", []))}
    data["tools"] = sorted(
        data["tools"],
        key=lambda t: (cat_rank.get(t["category"], 999), t["name"].lower()),
    )
    return data


_CATEGORY_BLOCK_RE = re.compile(
    r"(  - type: dropdown\n    id: category\n[\s\S]*?      options:\n)((?:        - .*\n)+)"
)


def extract_issue_template_categories(template_text: str) -> list[str]:
    match = _CATEGORY_BLOCK_RE.search(template_text.replace("\r\n", "\n"))
    if not match:
        return []
    options: list[str] = []
    for line in match.group(2).strip().splitlines():
        item = line.strip().removeprefix("-").strip().strip('"').strip("'")
        if item:
            options.append(item)
    return options


def sync_issue_template_categories(catalog: dict[str, Any], template_path: Path = DEFAULT_ISSUE_TEMPLATE) -> bool:
    if not template_path.exists():
        return False
    raw = template_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    expected_lines = "".join(f'        - "{c["name_en"]}"\n' for c in catalog.get("categories", []))
    updated, count = _CATEGORY_BLOCK_RE.subn(rf"\g<1>{expected_lines}", raw, count=1)
    if count == 0:
        return False
    template_path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"[+] Synced category options in {template_path}")
    return True


def validate_issue_template_categories(
    catalog: dict[str, Any], template_path: Path = DEFAULT_ISSUE_TEMPLATE
) -> tuple[bool, str]:
    if not template_path.exists():
        return False, f"Missing issue template: {template_path}"
    expected = [c["name_en"] for c in catalog.get("categories", [])]
    actual = extract_issue_template_categories(template_path.read_text(encoding="utf-8"))
    if actual != expected:
        return (
            False,
            f"Issue template categories {actual} out of sync with tools.json {expected} (run `python scripts/aat_cli.py sync`)",
        )
    return True, f"[OK] Issue template categories in sync: {template_path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate awesome-antigravity-tools catalog.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="Path to data/tools.json")
    parser.add_argument("--exclusions", type=Path, default=None, help="Optional path to data/exclusions.json")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to data/catalog.schema.json")
    parser.add_argument("--check-sync", action="store_true", help="Also verify README.md and README.zh-CN.md are in sync")
    parser.add_argument("--fix-order", action="store_true", help="Sort tools canonically in data/tools.json")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    if not args.catalog.exists():
        print(f"[ERROR] Catalog not found: {args.catalog}", file=sys.stderr)
        return 1

    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON in {args.catalog}: {exc}", file=sys.stderr)
        return 1

    if args.schema.exists():
        try:
            json.loads(args.schema.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[ERROR] Invalid JSON in schema {args.schema}: {exc}", file=sys.stderr)
            return 1

    if args.fix_order and isinstance(catalog, dict) and isinstance(catalog.get("tools"), list):
        catalog = sort_catalog_tools(catalog)
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"[+] Canonicalized tool order in {args.catalog}")

    errors, warnings = validate_catalog_data(catalog)

    exclusions_path = args.exclusions
    if exclusions_path is None and args.catalog.resolve() == DEFAULT_CATALOG.resolve() and DEFAULT_EXCLUSIONS.exists():
        exclusions_path = DEFAULT_EXCLUSIONS
    if exclusions_path is not None:
        if not exclusions_path.exists():
            errors.append(f"Exclusions file not found: {exclusions_path}")
        else:
            try:
                exclusions_obj = json.loads(exclusions_path.read_text(encoding="utf-8"))
                errors.extend(validate_exclusions_data(exclusions_obj, catalog))
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON in {exclusions_path}: {exc}")

    for w in warnings:
        print(f"[WARN] {w}")
    for e in errors:
        print(f"[ERROR] {e}", file=sys.stderr)

    sync_ok = True
    if args.check_sync and not errors:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import generate_docs

        snapshot = generate_docs.load_json(generate_docs.DEFAULT_SNAPSHOT)
        ok_en = generate_docs.write_or_check(
            REPO_ROOT / "README.md", generate_docs.render_readme_en(catalog, snapshot), check_only=True
        )
        ok_zh = generate_docs.write_or_check(
            REPO_ROOT / "README.zh-CN.md", generate_docs.render_readme_zh(catalog, snapshot), check_only=True
        )
        ok_tpl = True
        if args.catalog.resolve() == DEFAULT_CATALOG.resolve():
            ok_tpl, tpl_msg = validate_issue_template_categories(catalog, DEFAULT_ISSUE_TEMPLATE)
            if ok_tpl:
                print(tpl_msg)
            else:
                print(f"[FAIL] {tpl_msg}", file=sys.stderr)
        sync_ok = ok_en and ok_zh and ok_tpl

    if errors or not sync_ok or (args.strict_warnings and warnings):
        print(f"[FAIL] Validation failed ({len(errors)} errors, {len(warnings)} warnings).", file=sys.stderr)
        return 1

    print(
        f"[OK] Catalog valid: {len(catalog['tools'])} tools across {len(catalog['categories'])} categories "
        f"({len(warnings)} warnings)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
