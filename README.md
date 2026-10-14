# GitHub Trending Tracker

每天抓取 GitHub Trending，多角色流水线（Scout → Analyst×N → Editor）生成中文 Markdown 日报。

```bash
uv sync                  # 装依赖
uv run main.py           # 跑当日流水线（日报在 reports/，快照在 data/snapshots/）
uv run -m pytest         # 测试
powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1   # 注册每日计划任务
```

- 配置：`settings.yaml`（语言/模型/provider/interests/时间）；API key 放 `.env`（参考 `.env.example`）。
- 术语见 `CONTEXT.md`；决策见 `docs/adr/`；工单见 `.scratch/trending-tracker/`。
- v1 计划：Keeper agent 维护 Obsidian 仓库笔记（`vault/`），见工单 05。
