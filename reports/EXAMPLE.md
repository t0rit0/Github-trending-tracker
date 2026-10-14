# GitHub Trending 日报 · 2026-10-14

## TL;DR
- **mksglu/context-mode** — 把编码代理的工具输出沙箱化、号称压缩上下文 98%，今天最贴合日常开发痛点的项目。
- **lyogavin/airllm** — 单张 4GB 显卡跑 2.8T 参数模型推理，本地大模型的硬件门槛又被砍了一刀。
- **vercel-labs/skills** — `npx skills`，把 agent skill 变成可分发、可复用的包，Vercel Labs 出品。
- **xtool-org/xtool** — 跨平台 Xcode 替代，Linux/Windows 上用 SwiftPM 构建部署 iOS 应用。
- **morluto/rea** — 用 Agent 做逆向，从应用行为一路挖到原生二进制；单日 +54k 星，热度异常但方向值得扫一眼。

## 新上榜

### [mksglu/context-mode](https://github.com/mksglu/context-mode) — ⭐ 28,538（+969）· TypeScript
标签：`agent` `mcp` `context` `dev-tools`
一句话定位：为 AI 编码代理压缩上下文窗口。
为什么值得关注：工具输出挤爆上下文是所有编码代理的通病，它的做法是把工具结果沙箱化并号称削减 98%，同时持久化会话记忆，再通过 MCP + hooks 在 17 个平台上统一路由。如果你正在给代理写工具链，这套「隔离大输出 + 跨平台路由」的思路可以直接借鉴，尤其适合工具返回体巨大的场景（日志、抓取、构建产物）。

### [lyogavin/airllm](https://github.com/lyogavin/airllm) — ⭐ 38,508（+1,001）· Jupyter Notebook
标签：`llm` `inference` `gpu` `quantization`
一句话定位：单张 4GB 显卡跑 2.8T 大模型推理。
为什么值得关注：分层加载把超大模型在显存与内存之间调度，硬件门槛压到消费级 GPU。对本地推理、离线实验和成本敏感的场景很有吸引力。注意 Notebook 为主的仓库通常偏演示，工程化落地前要自己评估吞吐与延迟，尤其是长上下文下的换页开销。

### [vercel-labs/skills](https://github.com/vercel-labs/skills) — ⭐ 34,736（+190）· TypeScript
标签：`agent` `dev-tools` `cli`
一句话定位：用 `npx skills` 一条命令安装和管理 agent skills 的开源工具。
为什么值得关注：目前 agent 能力大多靠零散提示词和随手脚本拼凑，缺少统一的分发与版本化方式。它把 skill 做成可直接 npx 拉取的包，降低复用与共享门槛。Vercel Labs 出品意味着后续大概率会和现有前端/边缘工作流打通，值得早期跟进。

### [xtool-org/xtool](https://github.com/xtool-org/xtool) — ⭐ 9,846（+1,198）· Swift
标签：`ios` `swift` `build-tools` `cross-platform`
一句话定位：跨平台 Xcode 替代，用 SwiftPM 构建部署 iOS 应用。
为什么值得关注：直接拆掉 iOS 开发对 macOS + Xcode 的绑定，可在 Linux、Windows 上编译部署。日增近 1,200 星说明社区对跨平台 iOS 工具链的需求之强。现实约束是签名、模拟器、调试链路这些环节往往比编译更难复刻，建议先拿非核心项目试水。

### [morluto/rea](https://github.com/morluto/rea) — ⭐ 220,055（+54,679）· TypeScript
标签：`agent` `reverse-engineering` `security` `typescript`
一句话定位：用 Agent 逆向分析，从应用行为到原生二进制。
为什么值得关注：把逆向工程交给智能体，从观察应用行为起步，逐层深入到原生二进制，降低人工分析门槛，适用于安全研究与代码审计。但单日 +54k 星这个量级明显偏离常态，星数可信度存疑，建议直接看代码质量与提交活跃度，而不是看数字。

### [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) — ⭐ 54,695（+1,815）· HTML
标签：`dev-tools` `design` `diagram` `ai-coding`
一句话定位：为多种 AI 编程助手设计的编辑级图表规范。
为什么值得关注：面向 Claude Code、Codex、Cursor、GitHub Copilot 等工具，提供 44 种图表类型的自包含 HTML + SVG 样式，明确反对 Mermaid 风格的输出。价值在于用统一设计规范约束 AI 生成的图表，让文档里的架构图从「能看」变成「能交付」。

### [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) — ⭐ 64,330（+1,748）· Python
标签：`tts` `voice-cloning` `self-hosted` `speech`
一句话定位：全本地开源的 ElevenLabs 替代方案。
为什么值得关注：语音克隆、音色设计、视频配音、听写、转写、有声书一条龙，全部本地运行，支持 646 种语言，不依赖云端 API。对隐私敏感或长期用量大的团队，是自托管路线的备选。实际选型时重点看克隆音质、延迟和许可证条款。

### [storytold/artcraft](https://github.com/storytold/artcraft) — ⭐ 26,561（+4,081）· Rust
标签：`creative-tools` `rust` `graphics` `film`
一句话定位：面向艺术家、设计师与影视人的 Rust 创作引擎。
为什么值得关注：定位「刻意创作」，服务艺术与影视工作流，Rust 实现。单日涨星超 4,000，渲染与工作流设计值得一看，但和常规后端/工具链开发距离较远，按需围观。

### [bilawalsidhu/gods-eye-view](https://github.com/bilawalsidhu/gods-eye-view) — ⭐ 55,925（+1,961）· JavaScript
标签：`geospatial` `osint` `visualization` `3d`
一句话定位：浏览器里的侦察卫星模拟器，数据真实。
为什么值得关注：把开源卫星影像与地理数据叠加到逼真的 3D 地球上，实时查看空间情报。数据源接入方式与瓦片调度对大屏可视化类项目有参考价值，安全敏感度较高的团队也可以了解下它的数据可得性边界。

## 在榜变化
今日没有历史记录命中的仓库，staying 列表为空，所有条目均为首次上榜，暂无连续天数或星数对比可讲。

## 掉榜
今日 dropped 列表为空，无仓库掉榜。

---
**运行状态**：抓取 ✓ 9 仓库 | 分析 9/9 | 笔记 9 篇 | Editor ✓
