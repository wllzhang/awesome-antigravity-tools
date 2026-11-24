<!-- 由 scripts/generate_docs.py 基于 data/tools.json 自动生成 — 请勿直接手动编辑 -->

# Awesome Antigravity Tools (Antigravity 专有工程工具精选榜) [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.zh-CN.md)
[![收录工具数](https://img.shields.io/badge/精选收录-18%20%E4%B8%AA%E5%B7%A5%E5%85%B7-4285F4.svg)](#目录)
[![每日健康巡检](https://github.com/wllzhang/awesome-antigravity-tools/actions/workflows/health-check.yml/badge.svg)](https://github.com/wllzhang/awesome-antigravity-tools/actions/workflows/health-check.yml)
[![巡检状态](https://img.shields.io/badge/巡检状态-18/18%20%E6%B4%BB%E8%B7%83%20%28100%25%29-brightgreen)](health_report.zh-CN.md)
[![Antigravity](https://img.shields.io/badge/Google-Antigravity-4285F4.svg?logo=google)](https://antigravity.google)

> 纯粹且极致：由 Schema 严格校验的精选目录，只收录 **100% 专为 Google Antigravity 设计研发** 的原生 IDE 扩展、底层系统补丁、运行时热修补与专用工程网关。

[🌐 交互式网页目录](https://wllzhang.github.io/awesome-antigravity-tools/?lang=zh) · [📊 横向对比矩阵](COMPARISON.md) · [English Documentation](README.md) · [贡献指南](CONTRIBUTING.zh-CN.md) · [每日健康与清退报告](health_report.zh-CN.md) · [提交新工具](https://github.com/wllzhang/awesome-antigravity-tools/issues/new/choose)

---

## 🎯 我们的纯粹性原则：严拒泛用充数，只收专有原生

当前 AI 编程领域的绝大多数 Awesome 列表充斥着两大臃肿噪音：
1. **纯 Markdown 提示词堆砌**（`SKILL.md`）：在 Claude Code、Cursor、Codex 间无差别通用，毫无工程壁垒；
2. **跨平台泛用工具贴牌**：原本为 Claude Code 或通用 LLM 开发，仅在 README 里贴一个“Antigravity”关键词引流。

**本项目坚决拒绝一切泛用充数。** 列表中收录的每一个项目，**其核心使命 100% 专为 Google Antigravity 而生**：
- 专为 Antigravity IDE、官方 CLI (`agy`) 或 `agy acp` 底层协议深度研发；
- 正面攻克 Antigravity 运行时的特定缺陷、系统级死锁或配额盲区；
- 由统一数据源 `data/tools.json` 驱动，每日自动执行健康度与活性巡检（`scripts/health-check.py`）。

> **生态脉搏**：共收录 `18` 款专有工具（`4` 个分类）· 合计 `60.2k` Stars · `18/18` 活跃（`100.0%`）· 平均健康分：`86.9/100`（[完整巡检报告](health_report.zh-CN.md)）

---

## 目录

- [🚀 官方 CLI 与开发套件 (2)](#-官方-cli-与开发套件)
- [🖥️ IDE 扩展与专属控制台 (5)](#️-ide-扩展与专属控制台)
- [🔧 平台补丁与底层运行时修复 (5)](#-平台补丁与底层运行时修复)
- [🔌 专用网关、ACP 适配器与迁移工具 (6)](#-专用网关acp-适配器与迁移工具)
- [🏷️ 项目徽章 (Badge)](#️-项目徽章-badge)
- [🤝 参与贡献](#-参与贡献)

---

## 🚀 官方 CLI 与开发套件

由 `google-antigravity` 官方维护的终端命令行工具与 SDK，支持命令行编排与程序化 Agent 开发。

- [antigravity-cli](https://github.com/google-antigravity/antigravity-cli) - Google Antigravity 官方命令行工具（`agy`），将 Antigravity 的推理、执行与编排能力原生引入终端环境。 `Official` `CLI` `Terminal`
- [antigravity-sdk-python](https://github.com/google-antigravity/antigravity-sdk-python) - Google Antigravity 官方 Apache-2.0 Python SDK，用于以代码方式构建和编排 Antigravity AI 智能体。 `Official` `Python` `SDK`

---

## 🖥️ IDE 扩展与专属控制台

专为 Antigravity 模型配额监控、状态栏倒计时与账号管理打造的桌面应用与扩展。

- [agy-meme](https://github.com/jiangnanquan/agy-meme) - 专为 Google Antigravity 桌面端打造的双向猫娘表情贴纸渲染、Cmd/Ctrl+Shift+M 输入框选图面板与终端静默隔离原生 MCP 插件（内置 48 张全球通用无字透明模切贴纸）。 `Desktop` `Plugin` `MCP` `Node.js`
- [Antigravity-Manager](https://github.com/lbjlaq/Antigravity-Manager) - 基于 Rust (Tauri v2) + React 构建的桌面级 Antigravity 账号管理与一键切换工具。 `Desktop` `Rust` `Tauri`
- [antigravity-panel](https://github.com/n2ns/antigravity-panel) - 专为 Google Antigravity IDE 打造的配额监控与缓存管理面板，支持多模型额度、周限额与趋势统计。 `VS Code` `TypeScript` `Quota`
- [AntigravityManager](https://github.com/Draculabo/AntigravityManager) - 面向 Antigravity Classic、Antigravity IDE 与 `agy` CLI 的多客户端账号管理桌面端，支持实时配额查看与无缝切换。 `Desktop` `TypeScript` `Quota`
- [vscode-antigravity-cockpit](https://github.com/jlcodes99/vscode-antigravity-cockpit) - Antigravity 标杆级 VS Code 扩展，支持多模型配额实时监控、状态栏倒计时提示、多模型置顶及模型能力 HUD。 `VS Code` `TypeScript` `HUD`

---

## 🔧 平台补丁与底层运行时修复

正面攻克 Antigravity 官方客户端特定缺陷、汉化注入、无 TUN 代理、符号链接失效与进程死锁的底层工具。

- [agy-desktop-exo](https://github.com/jiangnanquan/agy-desktop-exo) - 面向 Google Antigravity 桌面端的体验增强（紧凑加宽布局开关、Office/EPUB 侧边栏速览）与简体中文汉化引擎。 `Desktop` `Localization` `UX` `Node.js`
- [Antigravity-Chinese-Localization](https://github.com/antigravity-cn-community/Antigravity-Chinese-Localization) - MIT 开源协议的 Antigravity IDE 一键中文汉化工具包，精准覆盖客户端界面与菜单词条。 `Localization` `JavaScript` `Patch`
- [antigravity-junction-skill-fix](https://github.com/wllzhang/antigravity-junction-skill-fix) - 零磁盘占用 NTFS 硬链接目录桥接工具，彻底解决 Antigravity Go Language Server 无法加载 Windows 目录联接 (`mklink /J`) 与符号链接 (`mklink /D`) 的硬伤问题。 `Windows` `PowerShell` `NTFS`
- [antigravity-proxy](https://github.com/yuaotian/antigravity-proxy) - 专为 Antigravity 打造的 Windows 免 TUN 强制代理工具，基于 DLL 注入实现进程级 SOCKS5/HTTP 流量转发。 `Windows` `C++` `Proxy`
- [vscode-antigravity-backend-fix](https://github.com/HeshamNoaman/vscode-antigravity-backend-fix) - 官方 VS Code 插件热修补工具，彻底解决 Windows Defender 超时引发的每次启动重复下载 ~202MB `agy.exe` 的网络拥堵与进程锁死问题。 `Windows` `Node.js` `PowerShell`

---

## 🔌 专用网关、ACP 适配器与迁移工具

围绕 Antigravity 官方核心协议（`agy acp`）、原生插件规范（`plugin.json`）以及 Google AI（Flow）生态配套媒体网关打造的高性能工程工具。

- [ACP-Ant](https://github.com/czg86389-hub/ACP-Ant) - 基于 Google 官方 Antigravity CLI ACP 协议构建的 OpenAI/Anthropic 兼容 API 服务，支持多账号独立代理与工具调用。 `Python` `ACP` `Gateway`
- [antigravity-acp](https://github.com/shubzkothekar/antigravity-acp) - 基于 Bun 构建的 Google Antigravity `agy` CLI ACP 服务端，支持实时流式输出与会话历史回放。 `TypeScript` `Bun` `ACP`
- [antigravity-skill-porter](https://github.com/Pranav-Nexus/antigravity-skill-porter) - 专门用于将外部技能代码适配并打包为规范 Antigravity 原生插件（自动补全 `plugin.json` 与生命周期配置）的转换脚手架。 `CLI` `Converter` `Plugin`
- [flow2api](https://github.com/TheSmallHanCat/flow2api) - 面向 Google Flow（Veo 3.1、Nano Banana 与 Omni）的 OpenAI 与 Gemini 兼容 API 网关，支持多账号池负载均衡、Cookie 自动刷新、代理与 Web 管理后台。 `Python` `Docker` `Google-Flow` `Gateway`
- [liftgate](https://github.com/acking-you/liftgate) - 专为 Antigravity 官方 `agy acp`（Agent Client Protocol）通道构建的原生 API 网关与 GPUI 桌面控制中心，免除任何账号池与封号风险。 `Rust` `GPUI` `Gateway`
- [refined-antigravity-acp](https://github.com/simonepri/refined-antigravity-acp) - 开箱即用的 Google Antigravity ACP 协议增强封装二进制，修复第三方 ACP 客户端接入时的兼容性边界问题。 `TypeScript` `ACP` `Wrapper`

---

## 🏷️ 项目徽章 (Badge)

如果您的工具已被收录到本榜单，欢迎在您的 README 中展示收录徽章：

[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/wllzhang/awesome-antigravity-tools)

```markdown
[![Awesome Antigravity Tools](https://img.shields.io/badge/Awesome-Antigravity--Tools-brightgreen?logo=google&logoColor=white)](https://github.com/wllzhang/awesome-antigravity-tools)
```

---

## 🤝 参与贡献

欢迎提交您的专有工具！所有收录条目统一维护于 [`data/tools.json`](data/tools.json)，通过 `python scripts/generate_docs.py` 自动同步生成中英文文档。

> **提示**：本仓库本身亦遵循 Antigravity 原生插件规范（[`plugin.json`](plugin.json) + `antigravity-tools-advisor` 技能），同时内置零依赖 CLI（`python scripts/aat_cli.py search <关键词>`）。

在提交前请阅读我们的 [贡献指南](CONTRIBUTING.zh-CN.md) 与 [行为准则](CODE_OF_CONDUCT.md)。
