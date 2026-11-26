# Repository Guidelines (`awesome-antigravity-tools`)

Curated, schema-validated index, CLI, health telemetry engine, and interactive static web explorer for **100% Google Antigravity-exclusive** engineering tools, IDE extensions, runtime hotfixes, and ACP gateways.

## Curatorial & Engineering Rules

- **Strict Exclusivity Gate**: Only include open-source software built specifically for Google Antigravity (`agy`, `agy acp`, Antigravity Desktop 2.0, Antigravity IDE, `plugin.json`, or companion Google Flow APIs). Reject generic cross-agent tools, region/sanctions bypassers, OAuth/ToS-risk free-tier proxies, and bare `SKILL.md` prompt packs; record permanent exclusions in `data/exclusions.json`.
- **Zero External Dependencies**: All Python tooling under `scripts/` uses the Python >=3.10 standard library only, and `docs/` uses zero-framework vanilla HTML/CSS/ES modules (`tests/test_web.mjs` runs via `node:test`).
- **Single Source of Truth**: Edit `data/tools.json` (governed by `data/catalog.schema.json`) or use `python scripts/aat_cli.py add|remove ... --sync-docs`. Never hand-edit derived files (`README.md`, `README.zh-CN.md`, `COMPARISON.md`, `data/badges/*`, `data/exports/*`, `docs/catalog-bundle.json`, `docs/feed.xml`, `docs/sitemap.xml`, `docs/robots.txt`, `docs/llms.txt`, `docs/logo.svg`, `.github/ISSUE_TEMPLATE/submit_tool.yml` category dropdown).

## Architecture Map

- `data/` — Canonical catalog (`tools.json`, `catalog.schema.json`), rejected repository ledger (`exclusions.json`), live telemetry (`health_snapshot.json`, `health_history.json`), Shields.io JSON badges (`badges/`), and exports (`exports/tools.csv`, `exports/catalog.jsonld`).
- `scripts/` — Zero-dependency tooling:
  - `aat_cli.py`: Interactive & maintainer CLI (`list`, `search`, `recommend`, `compare`, `doctor`, `info`, `stats`, `add`, `remove`, `sync`, `verify`).
  - `mcp_server.py`: JSON-RPC 2.0 stdio MCP server exposing 6 read-only advisor tools (`aat_recommend`, `aat_search`, `aat_compare`, `aat_info`, `aat_stats`, `aat_doctor`), 2 resources (`aat://catalog`, `aat://llms.txt`), and `--self-test`.
  - `validate_catalog.py`: Schema, exclusions zero-overlap, formatting, alphabetical order, and sync linter (`--fix-order`, `--check-sync`, `--strict-warnings`).
  - `health-check.py`: GitHub REST API health scorer (0–100), 90-day history tracker, and bilingual audit report generator (`health_report.md`, `health_report.zh-CN.md`).
  - `discover_candidates.py`: GitHub radar scoring emerging Antigravity-exclusive repositories while filtering `data/exclusions.json` and policy risks (`--max-days-inactive`, `--sort`, `--format md|json|aat-cmd`, `--out-aat-cmd`).
  - `parse_submission.py`: GitHub Issue Form parser, exclusions gate, and live validator for `submit_tool.yml`.
  - `generate_docs.py`, `generate_badges.py`, `export_catalog.py`, `build_site.py`: Deterministic artifact generators.
  - `dev.ps1`: Windows PowerShell task runner (`all`, `validate`, `generate`, `export`, `build-site`, `test`, `mcp-test`, `audit`, `discover`, `doctor`, `serve`).
- `docs/` — GitHub Pages static web explorer (`index.html`, `app.js`, `catalog-logic.js`, `insights.js`, `styles.css` with `?tag=`, `?featured=`, `?code=` language filter, `?compare=`, card install copy, and `?` shortcuts dialog) plus generated bundles (`catalog-bundle.json`, `llms.txt`, `feed.xml`, `sitemap.xml`, `robots.txt`, `logo.svg`).
- `skills/antigravity-tools-advisor/`, `plugin.json`, & `mcp_config.json` — Native Antigravity plugin and stdio MCP server packaging.
- `.github/workflows/` — CI workflows including `lint-and-links.yml`, `health-check.yml`, `pages.yml`, `submission-triage.yml`, and read-only weekly `discovery-radar.yml` (`contents: read`).
- `tests/` — Offline Python (`test_mcp_server.py`, `test_tooling.py`, `test_site_artifacts.py`) and Node.js (`test_web.mjs`) test suites.

## Canonical Commands

```bash
# Sync all derived docs, badges, exports, and docs/ artifacts after editing data/tools.json
python scripts/aat_cli.py sync

# Strict schema + exclusions zero-overlap + byte-level artifact sync verification (CI gate)
python scripts/aat_cli.py verify --check-sync --strict-warnings

# CLI discovery, recommendation, side-by-side comparison, and local environment diagnostics
python scripts/aat_cli.py recommend "<goal or symptom>" --lang zh
python scripts/aat_cli.py compare <tool1> <tool2> --markdown
python scripts/aat_cli.py doctor --json

# MCP stdio server self-test
python scripts/mcp_server.py --self-test

# Refresh live GitHub telemetry snapshot + 90-day history
python scripts/health-check.py --use-gh-cli

# Run full test suites
python -m unittest discover -s tests -v
node --check docs/catalog-logic.js && node --check docs/insights.js && node --check docs/app.js
node --test tests/test_web.mjs
```

On Windows PowerShell, `pwsh -NoProfile -File .\scripts\dev.ps1 -Task all` (or `validate`, `test`, `mcp-test`, `audit`, `discover`, `doctor`, `serve`) wraps these steps with strict `$LASTEXITCODE` checking.

## Key CI & Contract Invariants

- **DOM & i18n Parity (`tests/test_site_artifacts.py`)**: Every `document.getElementById("...")` in `docs/app.js` must exist in `docs/index.html`, and every `data-i18n="..."` attribute in `docs/index.html` must exist in both `I18N.en` and `I18N.zh` inside `docs/app.js`. All frontend DOM updates must remain free of `innerHTML` / `outerHTML` / `insertAdjacentHTML`.
- **Catalog & Exclusions Integrity (`scripts/validate_catalog.py`)**: `description_en` must be 15–240 chars starting uppercase and ending with `.` (no promotional hyperbole); `description_zh` must be 8–160 chars ending with `。`; `tools` must remain canonically sorted by category and lowercase `name`; `data/exclusions.json` must maintain zero overlap with `data/tools.json`.
- **Native Plugin & MCP Packaging (`tests/test_site_artifacts.py`, `tests/test_mcp_server.py`)**: `plugin.json` keys must remain within `{name, displayName, description, logo, version, author, homepage, repository, suggestedPrompts, disabled}`; MCP server configuration lives in `mcp_config.json` and stdio output must use UTF-8 LF newlines.
- **Workflow Contracts (`.github/workflows/`)**: Any new generated artifact emitted by `build_site.py`, `generate_docs.py`, `generate_badges.py`, or `export_catalog.py` must be staged in `health-check.yml`; `discovery-radar.yml` must remain `contents: read` with `workflow_dispatch` inputs passed solely via `env:`.
