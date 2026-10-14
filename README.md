# GitHub Trending Tracker

每天定时抓取 GitHub Trending，四个角色接力（Scout → Analyst×N → Keeper → Editor）产出一份中文 Markdown 日报；每个仓库的长期记忆沉淀在 `vault/` 的 Obsidian 风格笔记里——第二天再见到同一个仓库，日报会记得上次是怎么评价它的，不再当新面孔介绍。

## 快速开始

前置：[uv](https://docs.astral.sh/uv/)（Python ≥3.13 由它自动管理）。

```bash
git clone https://github.com/t0rit0/Github-trending-tracker.git
cd Github-trending-tracker
uv sync                                   # 装依赖（自动建 .venv）
cp .env.example .env                      # 然后填入你的 API key
cp interests.yaml.example interests.yaml  # 可选：写下兴趣，日报按此排序详略
```

`.env` 至少需要：

```
LLM_API_KEY=sk-...      # 任意 OpenAI 兼容端点的 key
```

端点与模型在 `settings.yaml` 的 `provider` / `models` 里改（默认 DeepSeek 的 `deepseek-flash`）。

## 跑一次，看结果

```bash
uv run main.py
```

一次运行依次做四件事：抓取榜单并对比昨日快照 → 并行分析每个仓库 → 更新 vault 长期笔记 → 撰写日报。跑完去这些地方看：

| 想看什么 | 在哪 |
|---|---|
| **当日日报**（主要产物） | `reports/YYYY-MM-DD.md`（样例见 `reports/EXAMPLE.md`） |
| 仓库长期记忆 | `vault/repos/{owner}/{repo}.md`：frontmatter 存结构化状态，正文按日期追加条目 |
| 原始快照（diff 的事实来源） | `data/snapshots/YYYY-MM-DD.json` |
| 当日分析缓存（重跑不重复花钱） | `data/analyses/YYYY-MM-DD.json` |

日报骨架固定：**TL;DR**（最值得看的 3-5 条）→ **新上榜**（一句话定位 + 为什么值得关注）→ **在榜变化**（连续天数、星数变化、与上次分析相比有什么新东西）→ **掉榜**（一行带过）。文末运行状态行（如 `抓取 ✓ 9 仓库 | 分析 9/9 | 笔记 9 篇 | Editor ✓`）概览当次质量，✗ 表示该环节已降级（见下节）。

同日重跑安全：已有分析的仓库不再调模型，笔记不追加重复条目，日报覆盖重写。

## 每天自动跑（Windows）

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1
```

按 `settings.yaml` 的 `schedule.time`（默认 08:00）注册计划任务；关机/休眠错过的班次会在下次可用时补跑。取消：`Unregister-ScheduledTask -TaskName trending-tracker`。

## 配置一览

| 文件 | 管什么 | 入库吗 |
|---|---|---|
| `settings.yaml` | 抓取窗口与语言、provider、模型、vault 路径、任务时间 | ✅ |
| `interests.yaml` | 兴趣（languages / topics / keywords），日报据此排序与取舍详略 | ❌（模板 `interests.yaml.example`） |
| `.env` | `LLM_API_KEY`；可选 `GITHUB_COOKIE` | ❌（模板 `.env.example`） |

匿名抓取每天只有 ~9 个仓库是已知现状（ADR-0001）；想拿全量 25 个，把浏览器登录 GitHub 的 cookie 整串填进 `GITHUB_COOKIE`。

## 失败时的样子（降级设计）

- **抓取失败**：写占位日报（`今日抓取失败：原因`），退出码 1；
- **单仓库分析失败**：该仓库在日报里退化为纯数据行（链接 + 星数 + 语言），不影响其他仓库；
- **Editor 失败**：用确定性模板渲染纯数据版日报，退出码 1；快照与分析已落盘，重跑只重做 Editor。

## 开发

```bash
uv run pytest    # 全量测试，不调真实 LLM 与网络
```

术语表见 `CONTEXT.md`，架构决策见 `docs/adr/`，工单见 `.scratch/trending-tracker/`。
