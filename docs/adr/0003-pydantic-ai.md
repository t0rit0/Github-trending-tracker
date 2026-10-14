# 用 PydanticAI 做 agent 层，而非多智能体框架

本项目虽以"多智能体系统"为目标，但形态是确定性批处理流水线：Analyst 是同一段代码并发调 N 次 LLM，没有 agent 间对话与动态协作。因此选 PydanticAI（`pydantic-ai-slim[openai]`）——一个结构化输出专用的薄 agent 层（pydantic 校验失败自动重试、OpenAI 兼容端点一行接入），流水线编排保持手写 asyncio。硬性要求"支持第三方模型"（OpenAI 兼容接口，如 GLM/DeepSeek）。

## Considered Options

- **LangGraph**：状态图/checkpoint 在批处理流水线中用不上，依赖重。
- **CrewAI**：角色协作范式错位；2026-03 曝可链式 RCE 漏洞。
- **AutoGen/AG2**：会话式多 agent，最错位；AutoGen 已进维护模式。
- **OpenAI Agents SDK**：非 OpenAI 模型是二等公民（多 provider 靠 beta 扩展）。
- **LiteLLM + 自写**：备选。最透明，但结构化校验 + 重试需自己做。

已知坑：GLM/DeepSeek 等 chat-completions 端点需显式用 `OpenAIChatModel`（v2 默认走 OpenAI Responses API）。
