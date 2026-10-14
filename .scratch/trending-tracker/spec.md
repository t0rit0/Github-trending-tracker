# GitHub Trending Tracker

每天抓取 GitHub Trending 页面，流水线（Scout → Analyst×N → Editor）生成 Markdown 日报；v1 加入 Keeper 维护 Obsidian 仓库笔记。

- 术语见 `CONTEXT.md`；关键决策见 `docs/adr/0001-0003`。
- v0 范围：Scout + Analyst + Editor + 编排/计划任务，无记忆层。
- v1 范围：Keeper + `vault/` 仓库笔记 + 日报历史上下文。

明确不做：常驻服务、Web、推送、weekly 单独抓取、逐仓库持续跟踪、记忆中间件。
