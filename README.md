# GitHub Trending Tracker

每日定时采集 GitHub Trending，经多智能体流水线（Scout → Analyst ×N → Keeper → Editor）生成结构化中文日报；仓库级长期记忆以 Obsidian 兼容笔记沉淀于 `vault/`，跨日上下文（连续在榜天数、历史定位）自动注入后续分析——同一仓库再次上榜时不会被当作新面孔重复介绍。

## 快速开始

前置依赖：[uv](https://docs.astral.sh/uv/)（自动管理 Python ≥3.13）。

```bash
git clone https://github.com/t0rit0/Github-trending-tracker.git
cd Github-trending-tracker
uv sync                                   # 安装依赖并创建虚拟环境
cp .env.example .env                      # 配置 API key
cp interests.yaml.example interests.yaml  # 可选：兴趣画像，驱动日报的过滤与排序
```

`.env` 至少需要 `LLM_API_KEY`（任意 OpenAI 兼容端点）。接入端点与模型在 `settings.yaml` 的 `provider` / `models` 中配置，默认 DeepSeek `deepseek-flash`。

## 运行与产物

```bash
uv run main.py
```

流水线依次执行：采集榜单并与前一日快照做差分 → 并行生成各仓库结构化分析 → 更新长期记忆笔记 → 汇总撰写日报。运行产物：

| 产物 | 路径 |
|---|---|
| 日报（主要交付物） | `reports/YYYY-MM-DD.md`（样例见 `reports/EXAMPLE.md`） |
| 仓库长期记忆 | `vault/repos/{owner}/{repo}.md`：frontmatter 存结构化状态，正文按日期追加 |
| 榜单快照（差分基准） | `data/snapshots/YYYY-MM-DD.json` |
| 当日分析缓存 | `data/analyses/YYYY-MM-DD.json`，幂等重跑时直接复用 |

日报采用固定骨架：**TL;DR** → **新上榜** → **在榜变化** → **掉榜**；文末运行状态行汇总采集规模、分析成功率、笔记更新数及各环节健康度（✓/✗）。

同日重跑幂等：已分析的仓库不重复调用模型，笔记不产生重复条目，日报覆盖更新。

## 定时调度（Windows）

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1
```

按 `settings.yaml` 的 `schedule.time`（默认 08:00）注册计划任务；因关机/休眠错过的触发会在下次可用时补偿执行。注销任务：`Unregister-ScheduledTask -TaskName trending-tracker`。

## 配置

| 文件 | 职责 | 是否入库 |
|---|---|---|
| `settings.yaml` | 采集窗口与语言、模型接入、vault 路径、调度时间 | ✅ |
| `interests.yaml` | 兴趣画像（languages / topics / keywords） | ❌（模板 `interests.yaml.example`） |
| `.env` | `LLM_API_KEY`；可选 `GITHUB_COOKIE` | ❌（模板 `.env.example`） |

未认证请求仅能获取部分榜单（约 9 个/日）；如需完整榜单，将浏览器会话 Cookie 整串配置至 `GITHUB_COOKIE` 即可启用。

## 故障降级

- **采集失败**：输出占位日报并返回非零退出码；
- **单仓库分析失败**：该条目降级为数据行（链接、星数、语言），不阻塞其余仓库；
- **编辑失败**：以确定性模板渲染数据版日报，返回非零退出码；快照与分析已持久化，重跑仅重做编辑阶段。

## 开发

```bash
uv run pytest    # 全量测试，不依赖外部 LLM 与网络
```

领域术语表见 `CONTEXT.md`。
