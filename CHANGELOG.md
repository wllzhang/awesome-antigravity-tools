# Changelog

All notable changes to **awesome-antigravity-tools** are documented in this file.

## [2.1.0] - 2026-11-27

A major ecosystem expansion, native MCP distribution upgrade, and curatorial hardening release across the catalog, CLI, discovery radar, and static web explorer.

### Added
- **Expanded Curated Catalog (19 → 37 Verified Tools across 4 Categories)**: Added 18 live-verified Antigravity-exclusive projects across all 4 categories: Official CLI & SDKs (`robotics-antigravity-plugin`), IDE Extensions & Cockpits (`agy-auth`, `agy-capsule`, `agy-hud`, `agy-powerline`, `agy-powertools`, `agy-switch`, `antigravity-context-viewer`, `obsidian-prism`, `paragravity`), Platform Fixes & Runtime Patches (`antigravity-rtl`, `antigravity2-cn`), and Dedicated Gateways & Migration (`agy-fast`, `agy-gyro`, `Antigravity-agy-dart`, `paseo-agy-acp`, `pi-antigravity-acp-provider`, `porta`).
- **Zero-Dependency Native Stdio MCP Server (`scripts/mcp_server.py` + `mcp_config.json`)**: Implements JSON-RPC 2.0 over UTF-8 LF stdio with 6 read-only tools (`aat_recommend`, `aat_search`, `aat_compare`, `aat_info`, `aat_stats`, `aat_doctor`), 2 resources (`aat://catalog`, `aat://llms.txt`), strict JSON-RPC validation (`-32700`/`-32600`/`-32601`/`-32602`/`-32603`), `--self-test` mode, `pyproject.toml` v2.1.0 console entrypoint (`aat-mcp`), and updated `skills/antigravity-tools-advisor/SKILL.md`.
- **Canonical Exclusions Ledger & Weekly Discovery Radar (`data/exclusions.json` + `.github/workflows/discovery-radar.yml`)**: Records 14 rejected/excluded repositories across strict policy categories (`tos-risk-proxy`, `region-bypass`, `cross-agent`, `prompt-pack`, `pruned-stale`, `pruned-dead`) with zero-overlap validation in `scripts/validate_catalog.py`, integrated filtering across `discover_candidates.py`, `parse_submission.py`, and `aat_cli.py add`, plus a read-only weekly discovery GitHub Actions workflow (`--out-aat-cmd`).
- **CLI Decision Workflows (`scripts/aat_cli.py`)**: Added bilingual intent recommender (`recommend`), 2–4 tool side-by-side matrix (`compare --markdown`), validated tool removal (`remove --sync-docs`), and local environment diagnostics (`doctor --os windows|macos|linux --json`).
- **Web Explorer Power-User UX & Agent Surfaces (`docs/`)**: Added tag chip filtering (`?tag=`), featured toggle (`?featured=1`), programming language filtering (`?code=`), 90-day star-growth SVG trend chart (`docs/insights.js`), per-card install-hint copy button, `?` keyboard shortcuts dialog (`#shortcutsDialog`), persistent `?tool=` RSS deep-links (`docs/feed.xml`), vector brand mark (`docs/logo.svg`), and agent-readable `docs/llms.txt`.
- **Developer Documentation & Quality Gates**: Added canonical `AGENTS.md`, `Makefile`/`scripts/dev.ps1` `doctor` and `mcp-test` tasks, and expanded Python `unittest` (`tests/test_mcp_server.py`, `tests/test_tooling.py`, `tests/test_site_artifacts.py`) and Node.js (`tests/test_web.mjs`) suites.

## [2.0.0] - 2026-11-18

A complete architectural evolution from a hand-edited Markdown list into a schema-validated, self-auditing, bilingual Antigravity-exclusive engineering index platform.

### Added
- **Single Source of Truth (`data/tools.json` + `data/catalog.schema.json`)**: Canonical JSON catalog with strict schema validation, bilingual EN/ZH descriptions, explicit Antigravity exclusivity rationales, platform enums, tags, and install hints.
- **Expanded Curated Catalog (10 → 21 Verified Tools across 4 Categories)**: Added `Official CLI & SDKs` (`antigravity-cli`, `antigravity-sdk-python`), plus live-verified Antigravity-exclusive tools (`AntigravityManager`, `antigravity-panel`, `Antigravity-Chinese-Localization`, `antigravity-fixer`, `antigravity-proxy`, `ACP-Ant`, `agy-acp`, `antigravity-acp`, `refined-antigravity-acp`), representing 59,000+ combined GitHub stars with 0 generic cross-agent padding.
- **Deterministic Bilingual Generator (`scripts/generate_docs.py`)**: Generates `README.md` and `README.zh-CN.md` with guaranteed EN/ZH parity, alphabetical ordering, live Ecosystem Pulse metrics, and `--check` CI sync verification.
- **Strict Zero-Dependency Validator (`scripts/validate_catalog.py`)**: Enforces schema compliance, duplicate/self-reference checks, URL integrity, punctuation & anti-hyperbole rules, canonical sorting (`--fix-order`), and README sync checks.
- **Health Engine v2 (`scripts/health-check.py`)**: Adds deterministic `0–100` Health Score, richer GitHub metadata (stars, forks, language, SPDX license, latest release), machine-readable `data/health_snapshot.json`, bilingual audit reports (`health_report.md` & `health_report.zh-CN.md`), rolling 90-day trend history (`data/health_history.json`), status transition diffing, and offline `--from-snapshot` mode.
- **Shields.io Dynamic Endpoint Badges (`scripts/generate_badges.py`)**: Emits `data/badges/{count,health,stars,score}.json`.
- **Candidate Discovery Radar (`scripts/discover_candidates.py`)**: Automated GitHub search & Antigravity-exclusivity heuristic scorer to surface emerging native tools while filtering out prompt dumps and multi-agent noise.
- **Interactive Catalog CLI (`scripts/aat_cli.py`)**: Zero-dependency CLI supporting `list`, `search`, `info`, `stats`, `add --sync-docs`, and `verify`.
- **Submission Triage Parser (`scripts/parse_submission.py`)**: Converts `.github/ISSUE_TEMPLATE/submit_tool.yml` issues into validated `data/tools.json` snippets with live GitHub verification.
- **Interactive GitHub Pages Web Explorer (`docs/`)**: Zero-framework bilingual directory (`index.html`, `styles.css`, `app.js`, `catalog-logic.js`, `insights.js`) featuring live search, category/platform/status filtering, sorting, native `<dialog closedby="any">` modals with scroll containment, collapsible Ecosystem Insights charts, 3-tool side-by-side comparison drawer, URL deep-linking, keyboard navigation (`/`, `j`/`k`, `l`), print styles, RSS feed (`docs/feed.xml`), sitemap, and JSON bundle (`docs/catalog-bundle.json`).
- **Exports & Developer Ergonomics**: Added `scripts/export_catalog.py` (`COMPARISON.md`, `data/exports/tools.csv`, `data/exports/catalog.jsonld`), `scripts/dev.ps1`, `Makefile`, `pyproject.toml`, and `CONTRIBUTING.zh-CN.md`.
- **Automated Test Suite (`tests/`) & CI/CD Workflows**: Added 17 Python `unittest` tests + 5 Node.js `node:test` frontend tests, upgraded `lint-and-links.yml` and `health-check.yml`, and added `pages.yml` and `submission-triage.yml`.

## [1.0.0] - 2026-11-17

- Initial release with 10 curated Antigravity-exclusive repositories, bilingual READMEs, and initial daily GitHub Actions health check workflow.
