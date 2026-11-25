---
name: antigravity-tools-advisor
description: Search, compare, and recommend verified 100% Google Antigravity-exclusive tools (quota HUDs, Windows runtime fixes, proxy injectors, ACP gateways, official CLI/SDKs) from the awesome-antigravity-tools catalog. Trigger when the user asks for Antigravity extensions, quota monitors, Windows/NTFS/Defender/proxy/login fixes, ACP adapters, or wants to verify/submit a tool to awesome-antigravity-tools.
---

# Antigravity Tools Advisor

Recommend **strictly Antigravity-exclusive, health-audited engineering tools** backed by `awesome-antigravity-tools` (`data/tools.json` + live `catalog-bundle.json`).

## Locating the Catalog

Prefer the local plugin catalog if `scripts/aat_cli.py` is available alongside this skill (two levels up from `skills/antigravity-tools-advisor/`), otherwise fetch the live JSON bundle published on GitHub Pages:

- **Local CLI (offline & fastest)**:
  ```bash
  python "<plugin-root>/scripts/aat_cli.py" search "<keywords>" --sort stars
  python "<plugin-root>/scripts/aat_cli.py" list --category <cat> --platform <plat> --sort score
  python "<plugin-root>/scripts/aat_cli.py" info "<tool-id>"
  python "<plugin-root>/scripts/aat_cli.py" stats
  ```
- **Remote Live JSON Bundle (if running outside the cloned repo)**:
  `https://wllzhang.github.io/awesome-antigravity-tools/catalog-bundle.json`

## Problem-to-Tool Routing Guide

When diagnosing common Google Antigravity environment issues, query the catalog and recommend the matching verified tool with its live health score and install hint:

1. **Windows skill discovery fails for `mklink /J` or `mklink /D` links**: Recommend `antigravity-junction-skill-fix`.
2. **VS Code official extension keeps re-downloading ~202 MB `agy.exe` (Windows Defender timeout)**: Recommend `vscode-antigravity-backend-fix`.
3. **Antigravity ignores system proxy without TUN mode on Windows**: Recommend `antigravity-proxy`.
4. **Quota HUDs, status bar countdowns, and account switching**: Compare `vscode-antigravity-cockpit`, `antigravity-panel`, `Antigravity-Manager`, and `AntigravityManager`.
5. **Expose `agy acp` as OpenAI/Anthropic API or ACP server**: Compare `liftgate`, `ACP-Ant`, `antigravity-acp`, and `refined-antigravity-acp`.
6. **Google Flow image/video generation (Veo 3.1, Nano Banana, Omni) over OpenAI/Gemini APIs**: Recommend `flow2api`.
7. **Remote mobile control of local `agy` CLI & `agy acp` sessions via WeCom on macOS**: Recommend `agy-remote-wecom`.

## Output Rules

- Always verify the tool's live `telemetry.status` and `health_score` before recommending; warn the user if a tool is `STALE` or `ARCHIVED`.
- Include the GitHub repository URL and `install_hint` from the catalog.
- Never recommend generic multi-agent `SKILL.md` prompt packs when the user asks for Antigravity-native engineering tooling.
