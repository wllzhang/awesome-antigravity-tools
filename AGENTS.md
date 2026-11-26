# Repository Guidelines (`awesome-antigravity-tools`)

Curated, schema-validated index, CLI, health telemetry engine, and interactive static web explorer for **100% Google Antigravity-exclusive** engineering tools, IDE extensions, runtime hotfixes, and ACP gateways.

## Curatorial & Engineering Rules

- **Strict Exclusivity Gate**: Only include open-source software built specifically for Google Antigravity (`agy`, `agy acp`, Antigravity Desktop 2.0, Antigravity IDE, `plugin.json`, or companion Google Flow APIs). Reject generic cross-agent tools and bare `SKILL.md` prompt packs.
- **Zero External Dependencies**: All Python tooling under `scripts/` uses the Python >=3.10 standard library only, and `docs/` uses zero-framework vanilla HTML/CSS/ES modules (`tests/test_web.mjs` runs via `node:test`).
- **Single Source of Truth**: Edit `data/tools.json` (governed by `data/catalog.schema.json`) or use `python scripts/aat_cli.py add|remove ... --sync-docs`. Never hand-edit derived files (`README.md`, `README.zh-CN.md`, `COMPARISON.md`, `data/badges/*`, `data/exports/*`, `docs/catalog-bundle.json`, `docs/feed.xml`, `docs/sitemap.xml`, `docs/robots.txt`, `docs/llms.txt`, `docs/logo.svg`, `.github/ISSUE_TEMPLATE/submit_tool.yml` category dropdown).

## Architecture Map

- `data/` — Canonical catalog (`tools.json`, `catalog.schema.json`), live telemetry (`health_snapshot.json`, `health_history.json`), Shields.io JSON badges (`badges/`), and exports (`exports/tools.csv`, `exports/catalog.jsonld`).
- `scripts/` — Zero-dependency tooling:
  - `aat_cli.py`: Interactive & maintainer CLI (`list`, `search`, `recommend`, `compare`, `doctor`, `info`, `stats`, `add`, `remove`, `sync`, `verify`).
  - `validate_catalog.py`: Schema, formatting, alphabetical order, and sync linter (`--fix-order`, `--check-sync`, `--strict-warnings`).
  - `health-check.py`: GitHub REST API health scorer (0–100), 90-day history tracker, and bilingual audit report generator (`health_report.md`, `health_report.zh-CN.md`).
  - `discover_candidates.py`: GitHub radar scoring emerging Antigravity-exclusive repositories (`--max-days-inactive`, `--sort`, `--format md|json|aat-cmd`).
  - `parse_submission.py`: GitHub Issue Form parser and live validator for `submit_tool.yml`.
  - `generate_docs.py`, `generate_badges.py`, `export_catalog.py`, `build_site.py`: Deterministic artifact generators.
  - `dev.ps1`: Windows PowerShell task runner (`all`, `validate`, `generate`, `export`, `build-site`, `test`, `audit`, `discover`, `doctor`, `serve`).
- `docs/` — GitHub Pages static web explorer (`index.html`, `app.js`, `catalog-logic.js`, `insights.js`, `styles.css`) plus generated bundles (`catalog-bundle.json`, `llms.txt`, `feed.xml`, `sitemap.xml`, `robots.txt`, `logo.svg`).
- `skills/antigravity-tools-advisor/` & `plugin.json` — Native Antigravity plugin packaging for advisor discovery.
- `tests/` — Offline Python (`test_tooling.py`, `test_site_artifacts.py`) and Node.js (`test_web.mjs`) test suites.

## Canonical Commands

```bash
# Sync all derived docs, badges, exports, and docs/ artifacts after editing data/tools.json
python scripts/aat_cli.py sync

# Strict schema + byte-level artifact sync verification (CI gate)
python scripts/aat_cli.py verify --check-sync --strict-warnings

# CLI discovery, recommendation, side-by-side comparison, and local environment diagnostics
python scripts/aat_cli.py recommend "<goal or symptom>" --lang zh
python scripts/aat_cli.py compare <tool1> <tool2> --markdown
python scripts/aat_cli.py doctor --json

# Refresh live GitHub telemetry snapshot + 90-day history
python scripts/health-check.py --use-gh-cli

# Run full test suites
python -m unittest discover -s tests -v
node --check docs/catalog-logic.js && node --check docs/insights.js && node --check docs/app.js
node --test tests/test_web.mjs
```

On Windows PowerShell, `pwsh .\scripts\dev.ps1 -Task all` (or `validate`, `test`, `audit`, `discover`, `doctor`, `serve`) wraps these steps with strict `$LASTEXITCODE` checking.

## Key CI & Contract Invariants

- **DOM & i18n Parity (`tests/test_site_artifacts.py`)**: Every `document.getElementById("...")` in `docs/app.js` must exist in `docs/index.html`, and every `data-i18n="..."` attribute in `docs/index.html` must exist in both `I18N.en` and `I18N.zh` inside `docs/app.js`. All frontend DOM updates must remain free of `innerHTML` / `outerHTML` / `insertAdjacentHTML`.
- **Catalog Formatting (`scripts/validate_catalog.py`)**: `description_en` must be 15–240 chars starting uppercase and ending with `.` (no promotional hyperbole); `description_zh` must be 8–160 chars ending with `。`; `tools` must remain canonically sorted by category and lowercase `name`.
- **Native Plugin Manifest (`tests/test_site_artifacts.py`)**: `plugin.json` keys must remain within `{name, displayName, description, logo, version, author, homepage, repository, suggestedPrompts, disabled}`.
- **Workflow Staging (`.github/workflows/health-check.yml`)**: Any new generated artifact emitted by `build_site.py`, `generate_docs.py`, `generate_badges.py`, or `export_catalog.py` must be included in `health-check.yml`'s `git add` list.
