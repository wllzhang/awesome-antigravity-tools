<!-- 由 scripts/generate_docs.py 基于 data/tools.json 自动生成 — 请勿直接手动编辑 -->

# Awesome Antigravity Tools (Antigravity 专有工程工具精选榜) [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.zh-CN.md)
[![收录工具数](https://img.shields.io/badge/精选收录-37%20%E4%B8%AA%E5%B7%A5%E5%85%B7-4285F4.svg)](#目录)
[![每日健康巡检](https://github.com/wllzhang/awesome-antigravity-tools/actions/workflows/health-check.yml/badge.svg)](https://github.com/wllzhang/awesome-antigravity-tools/actions/workflows/health-check.yml)
[![巡检状态](https://img.shields.io/badge/巡检状态-37/37%20%E6%B4%BB%E8%B7%83%20%28100%25%29-brightgreen)](health_report.zh-CN.md)
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

> **生态脉搏**：共收录 `37` 款专有工具（`4` 个分类）· 合计 `73.1k` Stars · `37/37` 活跃（`100.0%`）· 平均健康分：`88.9/100`（[完整巡检报告](health_report.zh-CN.md)）

---

## 目录

- [🚀 官方 CLI 与开发套件 (3)](#-官方-cli-与开发套件)
- [🖥️ IDE 扩展与专属控制台 (14)](#️-ide-扩展与专属控制台)
- [🔧 平台补丁与底层运行时修复 (7)](#-平台补丁与底层运行时修复)
- [🔌 专用网关、ACP 适配器与迁移工具 (13)](#-专用网关acp-适配器与迁移工具)
- [🏷️ 项目徽章 (Badge)](#️-项目徽章-badge)
- [🤝 参与贡献](#-参与贡献)

---

## 🚀 官方 CLI 与开发套件

由 Google 官方（`google-antigravity` 与 `google-deepmind`）维护的终端命令行工具、SDK 与官方原生插件，支持命令行编排与程序化 Agent 开发。

- [antigravity-cli](https://github.com/google-antigravity/antigravity-cli) - Google Antigravity 官方命令行工具（`agy`），将 Antigravity 的推理、执行与编排能力原生引入终端环境。 `Official` `CLI` `Terminal`
- [antigravity-sdk-python](https://github.com/google-antigravity/antigravity-sdk-python) - Google Antigravity 官方 Apache-2.0 Python SDK，用于以代码方式构建和编排 Antigravity AI 智能体。 `Official` `Python` `SDK`
- [robotics-antigravity-plugin](https://github.com/google-deepmind/robotics-antigravity-plugin) - Google DeepMind 官方发布的 Antigravity 机器人插件套件，提供面向 MuJoCo 仿真与真机控制的智能体工作流与工具。 `Official` `DeepMind` `Python` `Robotics` `Plugin`

---

## 🖥️ IDE 扩展与专属控制台

专为 Antigravity 模型配额监控、状态栏倒计时与账号管理打造的桌面应用与扩展。

- [agy-auth](https://github.com/fikrilal/agy-auth) - 基于 Go 编写的轻量级命令行多账号管理工具，支持在 Google Antigravity CLI（`agy`）与桌面端之间快速切换登录身份。 `Go` `CLI` `Multi-Account`
- [agy-capsule](https://github.com/Lumidarin/agy-capsule) - 嵌入 Antigravity 输入框底栏的悬浮胶囊 HUD（支持桌面端与独立 IDE 扩展），实时显示上下文占用、多模型配额、缓存状态与生成速度。 `Desktop` `HUD` `Quota` `Context` `JavaScript`
- [agy-hud](https://github.com/franksde/agy-hud) - 专为 Google Antigravity CLI（`agy`）打造的终端状态栏 HUD 插件，实时展示上下文占用、模型配额余量、当前模型信息与智能体运行状态。 `TypeScript` `CLI` `HUD` `Quota` `Plugin`
- [agy-meme](https://github.com/jiangnanquan/agy-meme) - 专为 Google Antigravity 桌面端打造的双向猫娘表情贴纸渲染、Cmd/Ctrl+Shift+M 输入框选图面板与终端静默隔离原生 MCP 插件（内置 48 张全球通用无字透明模切贴纸）。 `Desktop` `Plugin` `MCP` `Node.js`
- [agy-powerline](https://github.com/wassim-azi/agy-powerline) - 零依赖的 Antigravity CLI（`agy`）Powerline 终端状态栏插件，支持 Gemini/Claude 配额消耗速率预警、上下文仪表、Git 组件与 22 套主题。 `JavaScript` `CLI` `Statusline` `Quota` `Plugin`
- [agy-powertools](https://github.com/WhiteBr1ck/agy-powertools) - Antigravity 2.0 原生工作台增强插件，集成紧凑排版与阶段汇报、上下文与缓存监控、会话分支、本地用量面板及中文界面。 `Desktop` `Plugin` `UX` `Telemetry` `JavaScript`
- [agy-switch](https://github.com/anglee0323/agy-switch) - 跨平台 Antigravity 多客户端账号切换与用量统计工具（桌面端、系统托盘与终端 CLI），支持桌面 App、`agy` CLI、IDE 与 VS Code 扩展凭据同步及低额度智能切号。 `Rust` `Tauri` `CLI` `Multi-Account` `Quota`
- [antigravity-context-viewer](https://github.com/elviscjn-cjn/antigravity-context-viewer) - 面向 Google Antigravity 2.x 的对话上下文与用量看板，支持实时上下文预算、5h/周模型额度圆环、生成速度与桌面/CLI 历史统计。 `Desktop` `CLI` `Context` `Quota` `JavaScript`
- [Antigravity-Manager](https://github.com/lbjlaq/Antigravity-Manager) - 基于 Rust (Tauri v2) + React 构建的桌面级 Antigravity 账号管理与一键切换工具。 `Desktop` `Rust` `Tauri`
- [antigravity-panel](https://github.com/n2ns/antigravity-panel) - 专为 Google Antigravity IDE 打造的配额监控与缓存管理面板，支持多模型额度、周限额与趋势统计。 `VS Code` `TypeScript` `Quota`
- [AntigravityManager](https://github.com/Draculabo/AntigravityManager) - 面向 Antigravity Classic、Antigravity IDE 与 `agy` CLI 的多客户端账号管理桌面端，支持实时配额查看与无缝切换。 `Desktop` `TypeScript` `Quota`
- [obsidian-prism](https://github.com/RMvdesi/obsidian-prism) - 专为 Google Antigravity 桌面端打造的原生光学界面套件，内置四套深浅棱镜主题、512K 呼吸上下文试管、推理档位滑块与像素桌宠。 `Desktop` `UI` `WebGL2` `Plugin` `JavaScript`
- [paragravity](https://github.com/edison-land/paragravity) - 无侵入式 Google Antigravity 多账号并行与独立沙箱多开管理器，支持同时运行多个隔离实例。 `Python` `CLI` `Multi-Account` `Sandbox`
- [vscode-antigravity-cockpit](https://github.com/jlcodes99/vscode-antigravity-cockpit) - Antigravity 标杆级 VS Code 扩展，支持多模型配额实时监控、状态栏倒计时提示、多模型置顶及模型能力 HUD。 `VS Code` `TypeScript` `HUD`

---

## 🔧 平台补丁与底层运行时修复

正面攻克 Antigravity 官方客户端特定缺陷、汉化注入、无 TUN 代理、符号链接失效与进程死锁的底层工具。

- [agy-desktop-exo](https://github.com/jiangnanquan/agy-desktop-exo) - 面向 Google Antigravity 桌面端的体验增强（紧凑加宽布局开关、Office/EPUB 侧边栏速览）与简体中文汉化引擎。 `Desktop` `Localization` `UX` `Node.js`
- [Antigravity-Chinese-Localization](https://github.com/antigravity-cn-community/Antigravity-Chinese-Localization) - MIT 开源协议的 Antigravity IDE 一键中文汉化工具包，精准覆盖客户端界面与菜单词条。 `Localization` `JavaScript` `Patch`
- [antigravity-junction-skill-fix](https://github.com/wllzhang/antigravity-junction-skill-fix) - 零磁盘占用 NTFS 硬链接目录桥接工具，彻底解决 Antigravity Go Language Server 无法加载 Windows 目录联接 (`mklink /J`) 与符号链接 (`mklink /D`) 的硬伤问题。 `Windows` `PowerShell` `NTFS`
- [antigravity-proxy](https://github.com/yuaotian/antigravity-proxy) - 专为 Antigravity 打造的 Windows 免 TUN 强制代理工具，基于 DLL 注入实现进程级 SOCKS5/HTTP 流量转发。 `Windows` `C++` `Proxy`
- [antigravity-rtl](https://github.com/mmnaderi/antigravity-rtl) - 面向 Google Antigravity 桌面端与 IDE 的智能从右至左（RTL）双向排版与字体补丁，原生适配波斯语、阿拉伯语与希伯来语。 `Localization` `RTL` `JavaScript` `Patch`
- [antigravity2-cn](https://github.com/qqxpee/antigravity2-cn) - 专为 Antigravity 2.0 Electron 新架构打造的零依赖简繁中文汉化注入引擎，采用语法校验原子替换与 Shadow DOM 代码区严格隔离，支持一键无损还原。 `Desktop` `Localization` `Node.js` `Patch`
- [vscode-antigravity-backend-fix](https://github.com/HeshamNoaman/vscode-antigravity-backend-fix) - 官方 VS Code 插件热修补工具，彻底解决 Windows Defender 超时引发的每次启动重复下载 ~202MB `agy.exe` 的网络拥堵与进程锁死问题。 `Windows` `Node.js` `PowerShell`

---

## 🔌 专用网关、ACP 适配器与迁移工具

围绕 Antigravity 官方核心协议（`agy acp`）、原生插件规范（`plugin.json`）以及 Google AI（Flow）生态配套媒体网关打造的高性能工程工具。

- [ACP-Ant](https://github.com/czg86389-hub/ACP-Ant) - 基于 Google 官方 Antigravity CLI ACP 协议构建的 OpenAI/Anthropic 兼容 API 服务，支持多账号独立代理与工具调用。 `Python` `ACP` `Gateway`
- [agy-fast](https://github.com/INK-Q/agy-fast) - 面向 Google Antigravity（CLI、桌面端与 IDE）的零依赖合规本地 MCP 加速插件，显著降低对话轮次、Token 配额消耗与上传流量且不破坏原生 Diff。 `TypeScript` `MCP` `Plugin` `Performance`
- [agy-gyro](https://github.com/topjohnwu/agy-gyro) - 基于 Rust 构建的高性能本地 Antigravity Enterprise Gateway（`genai` 协议网关）、HTTP 429/5xx 自动重试代理与实时 Token 监控器。 `Rust` `Gateway` `Proxy` `Telemetry`
- [agy-remote-wecom](https://github.com/lukeinx/agy-remote-wecom) - macOS 守护进程与生命周期 Hook 插件，通过企微智能机器人长连接（无需公网服务器）在手机企业微信遥控本机 Antigravity (agy) 终端会话与后台 agy acp 会话，支持会话切换与历史恢复、附件投递、模型/权限模式切换、工具审批卡片与产物回传。 `Node.js` `ACP` `WeCom` `Remote Control` `Hook Plugin`
- [antigravity-acp](https://github.com/shubzkothekar/antigravity-acp) - 基于 Bun 构建的 Google Antigravity `agy` CLI ACP 服务端，支持实时流式输出与会话历史回放。 `TypeScript` `Bun` `ACP`
- [Antigravity-agy-dart](https://github.com/zou172866/Antigravity-agy-dart) - Google Antigravity 原生性能优化插件，集成 KV 提示词缓存自动预热保活、FTS5 上下文降噪、实时上下文监控与崩溃会话恢复。 `JavaScript` `Plugin` `MCP` `Cache` `Context`
- [antigravity-skill-porter](https://github.com/Pranav-Nexus/antigravity-skill-porter) - 专门用于将外部技能代码适配并打包为规范 Antigravity 原生插件（自动补全 `plugin.json` 与生命周期配置）的转换脚手架。 `CLI` `Converter` `Plugin`
- [flow2api](https://github.com/TheSmallHanCat/flow2api) - 面向 Google Flow（Veo 3.1、Nano Banana 与 Omni）的 OpenAI 与 Gemini 兼容 API 网关，支持多账号池负载均衡、Cookie 自动刷新、代理与 Web 管理后台。 `Python` `Docker` `Google-Flow` `Gateway`
- [liftgate](https://github.com/acking-you/liftgate) - 专为 Antigravity 官方 `agy acp`（Agent Client Protocol）通道构建的原生 API 网关与 GPUI 桌面控制中心，免除任何账号池与封号风险。 `Rust` `GPUI` `Gateway`
- [paseo-agy-acp](https://github.com/tiezbro/paseo-agy-acp) - 基于官方 `agy acp` 内核的 Apache-2.0 Paseo 适配器，支持与内置客户端共存登录第二个 Antigravity Pro 账号、模式映射与技能发现。 `TypeScript` `ACP` `Provider` `Multi-Account`
- [pi-antigravity-acp-provider](https://github.com/zacbemis/pi-antigravity-acp-provider) - 基于官方 `agy acp` 协议构建的原生扩展，将 Google Antigravity CLI 会话与模型无缝接入 Pi 编程智能体。 `TypeScript` `ACP` `Provider`
- [porta](https://github.com/L1M80/porta) - 轻量级自托管 Google Antigravity 远程 Web 控制端与移动端 PWA 伴侣应用，基于 WebSocket 实时同步与操控本机会话。 `TypeScript` `Web` `Mobile` `PWA`
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
