"""Analyst：对单个仓库产出结构化分析。PydanticAI + OpenAI 兼容端点，按仓库并行。"""
from __future__ import annotations

import asyncio
import os

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.output import PromptedOutput
from pydantic_ai.providers.openai import OpenAIProvider

from .config import Settings


class RepoAnalysis(BaseModel):
    full_name: str
    one_liner: str   # 一句话定位：这是什么
    why_care: str    # 为什么值得关注
    tags: list[str]  # 2-4 个小写英文领域标签


def make_agent(settings: Settings) -> Agent[None, RepoAnalysis]:
    # DeepSeek 等 chat-completions 端点必须显式 OpenAIChatModel：v2 默认走 OpenAI Responses API（ADR-0003）
    model = OpenAIChatModel(
        settings.models.analyst,
        provider=OpenAIProvider(
            base_url=settings.provider.base_url,
            api_key=os.environ[settings.provider.api_key_env],
        ),
    )
    return Agent(
        model,
        # DeepSeek 思考模型：强制 tool_choice 被 400，json_schema response_format 也不可用；
        # prompted 模式把 schema 放进提示词、从回复文本解析 JSON 并校验重试，最可移植
        output_type=PromptedOutput(RepoAnalysis),
        instructions=(
            "你是 GitHub 仓库分析师。根据提供的仓库信息（名称、描述、语言、star 动态）"
            "用简洁中文做结构化分析：one_liner 不超过 30 字；why_care 讲清它解决什么问题、"
            "看点在哪，不超过 80 字；tags 是 2-4 个小写英文领域标签（如 agent、dev-tools、database）。"
            "信息里没有的细节不要编造。"
        ),
    )


async def analyze_all(settings: Settings, repos: list[dict], concurrency: int = 5) -> list[dict]:
    """并行分析全部仓库；单个失败降级为 analysis=None，不阻塞其他仓库。"""
    agent = make_agent(settings)
    sem = asyncio.Semaphore(concurrency)

    async def one(repo: dict) -> dict:
        prompt = (
            f"仓库：{repo['full_name']}\n"
            f"描述：{repo['description'] or '（无）'}\n"
            f"主语言：{repo['language'] or '未知'}\n"
            f"总星数：{repo['stars']}，今日新增：{repo['stars_today']}，已连续在榜 {repo['days']} 天"
        )
        async with sem:
            try:
                result = await agent.run(prompt)
                return {**repo, "analysis": result.output}
            except Exception as e:  # 降级：日报里该仓库退回纯数据行
                print(f"  ! 分析失败 {repo['full_name']}: {type(e).__name__}: {e}")
                return {**repo, "analysis": None}

    return list(await asyncio.gather(*(one(r) for r in repos)))
