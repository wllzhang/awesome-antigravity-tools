---
name: antigravity-tools-advisor
description: Search, compare, and recommend verified 100% Google Antigravity-exclusive tools (quota HUDs, Windows runtime fixes, proxy injectors, ACP gateways, official CLI/SDKs) from the awesome-antigravity-tools catalog. Trigger when the user asks for Antigravity extensions, quota monitors, Windows/NTFS/Defender/proxy/login fixes, ACP adapters, or wants to verify/submit a tool to awesome-antigravity-tools.
---

# Antigravity Tools Advisor

Recommend **strictly Antigravity-exclusive, health-audited engineering tools** backed by `awesome-antigravity-tools` (`data/tools.json` + live `catalog-bundle.json`).

## Locating the Catalog

Prefer the native MCP server tools (`mcp_config.json` -> `scripts/mcp_server.py`) when available, otherwise run the local CLI or fetch the live remote index:

- **Native MCP Tools & Resources (Preferred when loaded)**:
  - Tools: `aat_recommend`, `aat_search`, `aat_compare`, `aat_info`, `aat_stats`, `aat_doctor`
  - Resources: `aat://catalog` (canonical `data/tools.json`), `aat://llms.txt` (compact AI index)
- **Local CLI (offline & fastest)**:
  ```bash
  python "<plugin-root>/scripts/aat_cli.py" recommend "<goal or bug>" --lang zh
  python "<plugin-root>/scripts/aat_cli.py" doctor
  python "<plugin-root>/scripts/aat_cli.py" compare <tool1> <tool2> --markdown
  python "<plugin-root>/scripts/aat_cli.py" search "<keywords>" --sort stars
  python "<plugin-root>/scripts/aat_cli.py" list --category <cat> --platform <plat> --sort score
  python "<plugin-root>/scripts/aat_cli.py" info "<tool-id>"
  python "<plugin-root>/scripts/aat_cli.py" stats
  ```
- **Remote Live Indexes (if running outside the cloned repo)**:
  - Compact AI index: `https://wllzhang.github.io/awesome-antigravity-tools/llms.txt`
  - Full JSON telemetry bundle: `https://wllzhang.github.io/awesome-antigravity-tools/catalog-bundle.json`

## Problem-to-Tool Routing Guide

When diagnosing common Google Antigravity environment issues, query the catalog and recommend the matching verified tool with its live health score and install hint:

1. **Windows skill discovery fails for `mklink /J` or `mklink /D` links**: Recommend `antigravity-junction-skill-fix`.
2. **VS Code official extension keeps re-downloading ~202 MB `agy.exe` (Windows Defender timeout)**: Recommend `vscode-antigravity-backend-fix`.
3. **Antigravity ignores system proxy without TUN mode on Windows**: Recommend `antigravity-proxy`.
4. **Desktop 2.0 context, telemetry, UI cockpits, and `agy` CLI statuslines**: Compare `antigravity-context-viewer`, `agy-powertools`, `agy-capsule`, `obsidian-prism`, `vscode-antigravity-cockpit`, `antigravity-panel`, `agy-hud`, and `agy-powerline`.
5. **Multi-account switching and isolated sandboxes**: Compare `Antigravity-Manager`, `AntigravityManager`, `agy-switch`, `agy-auth`, and `paragravity`.
6. **MCP turn/token acceleration and KV cache optimization**: Compare `agy-fast` and `Antigravity-agy-dart`.
7. **Localization & RTL layout fixes**: Compare `antigravity2-cn`, `Antigravity-Chinese-Localization`, `agy-desktop-exo`, and `antigravity-rtl`.
8. **Expose `agy acp` / Enterprise Gateway or connect ACP hosts**: Compare `liftgate`, `agy-gyro`, `ACP-Ant`, `antigravity-acp`, `refined-antigravity-acp`, `pi-antigravity-acp-provider`, and `paseo-agy-acp`.
9. **Google Flow image/video generation (Veo 3.1, Nano Banana, Omni) over OpenAI/Gemini APIs**: Recommend `flow2api`.
10. **Remote mobile / web control of local `agy` & Antigravity sessions**: Compare `agy-remote-wecom` (WeCom on macOS) and `porta` (self-hosted mobile PWA).

## Output Rules

- Always verify the tool's live `telemetry.status` and `health_score` before recommending; warn the user if a tool is `STALE` or `ARCHIVED`.
- Include the GitHub repository URL and `install_hint` from the catalog.
- Never recommend generic multi-agent `SKILL.md` prompt packs when the user asks for Antigravity-native engineering tooling.
