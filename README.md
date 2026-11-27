<!-- AUTO-GENERATED FROM data/tools.json BY scripts/generate_docs.py — DO NOT EDIT DIRECTLY -->

# Awesome Antigravity Tools [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Curated Tools](https://img.shields.io/badge/Curated-37%20Tools-4285F4.svg)](#contents)
[![Daily Health Audit](https://github.com/wllzhang/awesome-antigravity-tools/actions/workflows/health-check.yml/badge.svg)](https://github.com/wllzhang/awesome-antigravity-tools/actions/workflows/health-check.yml)
[![Repository Health](https://img.shields.io/badge/Health%20Audit-37/37%20Active%20%28100%25%29-brightgreen)](health_report.md)
[![Antigravity](https://img.shields.io/badge/Google-Antigravity-4285F4.svg?logo=google)](https://antigravity.google)

> A strictly curated, schema-validated directory of **100% native, dedicated tools, IDE extensions, runtime hotfixes, and engineering gateways** built exclusively for Google Antigravity.

[🌐 Interactive Web Explorer](https://wllzhang.github.io/awesome-antigravity-tools/) · [📊 Comparison Matrix](COMPARISON.md) · [🤖 LLMs.txt](https://wllzhang.github.io/awesome-antigravity-tools/llms.txt) · [中文文档 (Chinese)](README.zh-CN.md) · [Contributing Guidelines](CONTRIBUTING.md) · [Daily Health Report](health_report.md) · [Submit a Tool](https://github.com/wllzhang/awesome-antigravity-tools/issues/new/choose)

---

## 🎯 Our Manifesto: Strictly Antigravity-Exclusive

Most "awesome" lists in the AI agent space are flooded with two types of noise:
1. **Generic Markdown prompt dumps** (`SKILL.md`) that work identically across Claude Code, Cursor, and Codex.
2. **Generic multi-agent tools** that were designed for other platforms and merely slapped "Antigravity" onto their tags.

**This repository rejects all generic padding.** Every single project curated here is **100% dedicated to Google Antigravity**:
- Built specifically for the Antigravity IDE, CLI (`agy`), or `agy acp` protocol.
- Directly fixes critical Antigravity bugs, OS runtime limitations, or telemetry blind spots.
- Verified daily by our automated health audit (`scripts/health-check.py`) and backed by a single-source-of-truth JSON catalog (`data/tools.json`).

> **Ecosystem Pulse**: `37` curated tools across `4` categories · `74.6k` combined GitHub stars · `37/37` active (`100.0%`) · Avg Health Score: `88.9/100` ([Full Audit](health_report.md))

---

## Contents

- [Official CLI & SDKs (3)](#-official-cli--sdks)
- [IDE Extensions & Cockpits (14)](#️-ide-extensions--cockpits)
- [Platform Fixes & Runtime Patches (7)](#-platform-fixes--runtime-patches)
- [Dedicated Gateways, ACP Adapters & Migration Tooling (13)](#-dedicated-gateways-acp-adapters--migration-tooling)
- [Badge](#️-badge)
- [Contributing](#-contributing)

---

## 🚀 Official CLI & SDKs

First-party command-line harnesses, SDKs, and official plugins maintained by Google (`google-antigravity` and `google-deepmind`) for terminal workflows and programmatic agent orchestration.

- [antigravity-cli](https://github.com/google-antigravity/antigravity-cli) - Official Antigravity CLI (`agy`) bringing the reasoning, execution, and orchestration capabilities of the Antigravity agent harness directly into the terminal. `Official` `CLI` `Terminal`
- [antigravity-sdk-python](https://github.com/google-antigravity/antigravity-sdk-python) - Official Apache-2.0 Python SDK for building programmatic AI agents and workflows powered directly by Google Antigravity. `Official` `Python` `SDK`
- [robotics-antigravity-plugin](https://github.com/google-deepmind/robotics-antigravity-plugin) - Official Google DeepMind Antigravity plugin suite providing Python tooling and workflows for MuJoCo simulation and real-world agentic robotics. `Official` `DeepMind` `Python` `Robotics` `Plugin`

---

## 🖥️ IDE Extensions & Cockpits

Extensions and desktop applications designed exclusively to monitor Antigravity model quotas, manage accounts, and provide HUD telemetry.

- [agy-auth](https://github.com/fikrilal/agy-auth) - Lightweight Go CLI utility for fast multi-account profile management and credential switching across Google Antigravity CLI (`agy`) and Desktop. `Go` `CLI` `Multi-Account`
- [agy-capsule](https://github.com/Lumidarin/agy-capsule) - Inline composer capsule HUD for Google Antigravity Desktop and Antigravity IDE displaying live context usage, model quotas, cache hit status, and generation speed. `Desktop` `HUD` `Quota` `Context` `JavaScript`
- [agy-hud](https://github.com/franksde/agy-hud) - Native terminal statusline HUD plugin for Google Antigravity CLI (`agy`) displaying real-time context consumption, model quota usage, active model info, and agent status. `TypeScript` `CLI` `HUD` `Quota` `Plugin`
- [agy-meme](https://github.com/jiangnanquan/agy-meme) - Bidirectional Neko reaction stickers, Cmd/Ctrl+Shift+M inline composer picker, and Desktop-isolated zero-dependency MCP plugin (48 universal RGBA die-cut WebP stickers) for Google Antigravity Desktop. `Desktop` `Plugin` `MCP` `Node.js`
- [agy-powerline](https://github.com/wassim-azi/agy-powerline) - Zero-dependency Powerline statusline plugin for Antigravity CLI (`agy`) featuring Gemini and Claude quota pacing, context meters, Git widgets, and 22 terminal themes. `JavaScript` `CLI` `Statusline` `Quota` `Plugin`
- [agy-powertools](https://github.com/WhiteBr1ck/agy-powertools) - Native workbench enhancement plugin for Antigravity 2.0 adding compact layout typography, phase summaries, context and cache telemetry, session branching, and zh-CN UI. `Desktop` `Plugin` `UX` `Telemetry` `JavaScript`
- [agy-switch](https://github.com/anglee0323/agy-switch) - Cross-platform Tauri desktop app, tray widget, and CLI synchronizing Antigravity accounts, quota-based smart switching, and token analytics across Desktop, CLI, and IDE. `Rust` `Tauri` `CLI` `Multi-Account` `Quota`
- [antigravity-context-viewer](https://github.com/elviscjn-cjn/antigravity-context-viewer) - Context window and token usage dashboard for Google Antigravity 2.x tracking real-time context budgets, 5h/weekly model quotas, generation speed, and CLI history. `Desktop` `CLI` `Context` `Quota` `JavaScript`
- [Antigravity-Manager](https://github.com/lbjlaq/Antigravity-Manager) - Native desktop account manager and one-click switcher for Antigravity built with Tauri v2 (Rust) and React. `Desktop` `Rust` `Tauri`
- [antigravity-panel](https://github.com/n2ns/antigravity-panel) - Quota monitor and cache manager for Google Antigravity IDE tracking Gemini, Claude, and GPT limits with usage trend analytics. `VS Code` `TypeScript` `Quota`
- [AntigravityManager](https://github.com/Draculabo/AntigravityManager) - Desktop application for managing Google accounts across Antigravity Classic, Antigravity IDE, and `agy` CLI with real-time quota views. `Desktop` `TypeScript` `Quota`
- [obsidian-prism](https://github.com/RMvdesi/obsidian-prism) - Optical UI suite for Google Antigravity Desktop featuring WebGL2 prism themes, damped-spring motion, a 512K context vial, reasoning slider, and pixel mascots. `Desktop` `UI` `WebGL2` `Plugin` `JavaScript`
- [paragravity](https://github.com/edison-land/paragravity) - Non-invasive parallel multi-account and isolated sandbox instance manager for Google Antigravity with CLI controls and local dashboard. `Python` `CLI` `Multi-Account` `Sandbox`
- [vscode-antigravity-cockpit](https://github.com/jlcodes99/vscode-antigravity-cockpit) - VS Code extension for real-time Antigravity model quota tracking, status bar countdowns, multi-model pinning, and capability HUDs. `VS Code` `TypeScript` `HUD`

---

## 🔧 Platform Fixes & Runtime Patches

System-level hotfixes, localization injectors, network bridges, and patches solving core Antigravity bugs and OS runtime limitations.

- [agy-desktop-exo](https://github.com/jiangnanquan/agy-desktop-exo) - UX enhancements (compact wide-layout toggle, inline Office/EPUB sidebar preview) and Simplified Chinese localization for Google Antigravity Desktop. `Desktop` `Localization` `UX` `Node.js`
- [Antigravity-Chinese-Localization](https://github.com/antigravity-cn-community/Antigravity-Chinese-Localization) - MIT-licensed one-click Chinese localization toolkit and UI translation patch tailored for Google Antigravity IDE. `Localization` `JavaScript` `Patch`
- [antigravity-junction-skill-fix](https://github.com/wllzhang/antigravity-junction-skill-fix) - Zero-copy NTFS hardlink directory bridge that resolves Go language server discovery failures for Windows directory junctions (`mklink /J`) and symlinks (`mklink /D`). `Windows` `PowerShell` `NTFS`
- [antigravity-proxy](https://github.com/yuaotian/antigravity-proxy) - Transparent Windows DLL-injection proxy utility that routes Antigravity process traffic through SOCKS5/HTTP proxies without requiring TUN mode. `Windows` `C++` `Proxy`
- [antigravity-rtl](https://github.com/mmnaderi/antigravity-rtl) - Smart Right-to-Left (RTL) layout and bidirectional typography patcher for Google Antigravity Desktop and Antigravity IDE supporting Persian, Arabic, and Hebrew. `Localization` `RTL` `JavaScript` `Patch`
- [antigravity2-cn](https://github.com/qqxpee/antigravity2-cn) - Zero-dependency Simplified and Traditional Chinese localization injector for Antigravity 2.0 Desktop using syntax-verified atomic ASAR patching and Shadow DOM code isolation. `Desktop` `Localization` `Node.js` `Patch`
- [vscode-antigravity-backend-fix](https://github.com/HeshamNoaman/vscode-antigravity-backend-fix) - Hotfix for the official VS Code Antigravity extension resolving the repeated ~202 MB `agy.exe` background download loop caused by Windows Defender timeouts. `Windows` `Node.js` `PowerShell`

---

## 🔌 Dedicated Gateways, ACP Adapters & Migration Tooling

Engineering utilities built around the official Antigravity Agent Client Protocol (`agy acp`), native plugin specifications (`plugin.json`), and companion Google AI (Flow) media API gateways.

- [ACP-Ant](https://github.com/czg86389-hub/ACP-Ant) - OpenAI and Anthropic compatible API server bridging Google's official Antigravity CLI over ACP with per-account proxy and tool-calling support. `Python` `ACP` `Gateway`
- [agy-fast](https://github.com/INK-Q/agy-fast) - Zero-dependency, policy-compliant local MCP accelerator plugin for Google Antigravity (CLI, Desktop, and IDE) cutting agent turns, billable token quota, and upload traffic. `TypeScript` `MCP` `Plugin` `Performance`
- [agy-gyro](https://github.com/topjohnwu/agy-gyro) - High-performance Rust local Antigravity Enterprise Gateway (`genai` wire protocol), transient HTTP 429/5xx retry proxy, and live token usage monitor. `Rust` `Gateway` `Proxy` `Telemetry`
- [agy-remote-wecom](https://github.com/lukeinx/agy-remote-wecom) - Control local Antigravity (agy) terminal and background agy acp sessions from WeCom on macOS over an outbound WebSocket connection, with session resume, attachments, model/mode switching, and tool-approval cards. `Node.js` `ACP` `WeCom` `Remote Control` `Hook Plugin`
- [antigravity-acp](https://github.com/shubzkothekar/antigravity-acp) - Bun-powered Agent Client Protocol server for Google Antigravity's `agy` CLI featuring live streaming and session history replay. `TypeScript` `Bun` `ACP`
- [Antigravity-agy-dart](https://github.com/zou172866/Antigravity-agy-dart) - Native Google Antigravity plugin combining automatic KV prompt-cache warm-up, SQLite FTS5 context compression, live context metering, and crashed session recovery. `JavaScript` `Plugin` `MCP` `Cache` `Context`
- [antigravity-skill-porter](https://github.com/Pranav-Nexus/antigravity-skill-porter) - CLI tool specifically adapting, wrapping, and validating external skills into native Antigravity plugins with `plugin.json` and tool name mapping. `CLI` `Converter` `Plugin`
- [flow2api](https://github.com/TheSmallHanCat/flow2api) - OpenAI and Gemini compatible API gateway for Google Flow (Veo 3.1, Nano Banana, and Omni) featuring multi-account pooling, automatic cookie refresh, and proxy support. `Python` `Docker` `Google-Flow` `Gateway`
- [liftgate](https://github.com/acking-you/liftgate) - Run Antigravity as a local OpenAI Responses and Anthropic Messages gateway via official `agy acp` over stdio with native GPUI desktop and TUI controls. `Rust` `GPUI` `Gateway`
- [paseo-agy-acp](https://github.com/tiezbro/paseo-agy-acp) - Apache-2.0 Paseo provider powered by the official `agy acp` kernel enabling dual Antigravity Pro account coexistence, mode mapping, admission queuing, and skill discovery. `TypeScript` `ACP` `Provider` `Multi-Account`
- [pi-antigravity-acp-provider](https://github.com/zacbemis/pi-antigravity-acp-provider) - First-class Agent Client Protocol (`agy acp`) provider extension bridging Google Antigravity CLI sessions and models natively into the Pi coding agent. `TypeScript` `ACP` `Provider`
- [porta](https://github.com/L1M80/porta) - Self-hosted lightweight remote web interface and mobile PWA companion for controlling and monitoring local Google Antigravity sessions over WebSocket. `TypeScript` `Web` `Mobile` `PWA`
- [refined-antigravity-acp](https://github.com/simonepri/refined-antigravity-acp) - Drop-in refined Google Antigravity ACP binary wrapper resolving protocol compatibility quirks for external ACP clients. `TypeScript` `ACP` `Wrapper`

---

## 🏷️ Badge

If your tool is featured in this list, add this badge to your README:

[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/wllzhang/awesome-antigravity-tools)

```markdown
[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/wllzhang/awesome-antigravity-tools)
```

---

## 🤝 Contributing

Contributions are welcome! All entries are managed in [`data/tools.json`](data/tools.json) and rendered deterministically into both English and Chinese READMEs via `python scripts/generate_docs.py`.

> **Tip**: This repository also ships as a native Antigravity plugin ([`plugin.json`](plugin.json) + `antigravity-tools-advisor` skill) and CLI (`python scripts/aat_cli.py recommend "<intent>"`, `doctor`, `search <query>`).

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request or issue.
