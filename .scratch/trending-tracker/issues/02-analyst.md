# 02 Analyst：PydanticAI 单仓库分析（并行 N 个）

Status: resolved

- `pydantic-ai-slim[openai]`，OpenAI 兼容端点（GLM 等 chat-completions 需 `OpenAIChatModel`）。
- 输入：快照条目；输出 pydantic 模型（一句话定位 / 为什么值得关注 / 标签）。
- 模型与 provider 读 settings.yaml；失败降级为数据行，不阻塞其他仓库。
