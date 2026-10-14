"""Editor：把当日变化与分析汇总成 Markdown 日报。骨架固定（TL;DR→新上榜→在榜变化→掉榜），血肉自由。"""
from __future__ import annotations

import json
import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import Settings

SKELETON = (
    "# GitHub Trending 日报 · {date}\n\n"
    "## TL;DR\n（3-5 条今天最值得看的，按我的兴趣排）\n\n"
    "## 新上榜\n（逐个：仓库链接、⭐总数(+今日)、语言、标签、一句话定位、为什么值得关注）\n\n"
    "## 在榜变化\n（只列有动静的：连续天数、星数变化、和上次分析相比有什么新东西）\n\n"
    "## 掉榜\n（每个一行带过）\n"
)


def make_agent(settings: Settings) -> Agent[None, str]:
    model = OpenAIChatModel(
        settings.models.editor,
        provider=OpenAIProvider(
            base_url=settings.provider.base_url,
            api_key=os.environ[settings.provider.api_key_env],
        ),
    )
    return Agent(
        model,
        output_type=str,
        instructions=(
            "你是技术日报编辑，读者是一位资深开发者。把提供的当日 GitHub trending 数据写成中文 Markdown 日报，"
            f"严格遵循这个骨架（小节顺序与标题一字不变，TL;DR 用无序列表）：\n{SKELETON}\n"
            "规则：兴趣相关（见 interests）的排前面、写详细；无关的一笔带过；"
            "analysis 为 null 的仓库降级为一行纯数据（链接+星数+语言），不要虚构分析；"
            "带 history 的仓库是老面孔（哪怕 days=1 也是再次上榜）：在榜变化里提一句上次见到的时间"
            "（last_seen）与当时的定位（one_liner），对比今天有什么不同，别当新面孔介绍；"
            "掉榜部分每仓库一行。只输出 Markdown 正文，不要代码围栏。"
        ),
    )


async def compose(settings: Settings, digest: dict) -> str:
    agent = make_agent(settings)
    prompt = (
        f"今日数据（JSON）：\n{json.dumps(digest, ensure_ascii=False, indent=1)}\n\n"
        "写成今天的日报。"
    )
    result = await agent.run(prompt)
    return result.output


def build_digest(date: str, interests: dict, entries: list[dict], dropped: list[dict], history: dict | None = None) -> dict:
    """把带分析的当日条目压成给 Editor 的紧凑输入（纯函数，可测）。

    entries 已含 analysis 字段；days==1 归新上榜，>1 归在榜。
    history 来自 Keeper 更新前的旧笔记：{full_name: {last_seen, days_on_list, one_liner}}。
    """
    def row(e: dict) -> dict:
        out = {k: e.get(k) for k in ("full_name", "url", "description", "language", "stars", "stars_today", "days", "stars_delta")}
        a = e.get("analysis")
        # analysis 统一为 dict（落盘/读回的形态），不收 pydantic 对象
        out["analysis"] = {k: a[k] for k in ("one_liner", "why_care", "tags")} if a else None
        out["history"] = (history or {}).get(e["full_name"])
        return out

    return {
        "date": date,
        "interests": interests,
        "new": [row(e) for e in entries if e.get("days", 1) == 1],
        "staying": [row(e) for e in entries if e.get("days", 1) > 1],
        "dropped": [{"full_name": e["full_name"], "stars": e.get("stars"), "days": e.get("days")} for e in dropped],
        "analysis_failed": [e["full_name"] for e in entries if e.get("analysis") is None],
    }


def fallback_report(date: str, diff: dict) -> str:
    """Editor 失败时的纯数据降级版（确定性渲染，无 LLM）。"""
    lines = [f"# GitHub Trending 日报 · {date}", "", "## 新上榜"]
    for e in diff["new"]:
        lines.append(f"- [{e['full_name']}]({e['url']}) ⭐{e.get('stars')} (+{e.get('stars_today')}) {e.get('language') or ''}")
    lines += ["", "## 在榜变化"]
    for e in diff["staying"]:
        lines.append(f"- [{e['full_name']}]({e['url']}) 第 {e['days']} 天 ⭐{e.get('stars')} (Δ{e.get('stars_delta')})")
    lines += ["", "## 掉榜"]
    for e in diff["dropped"]:
        lines.append(f"- {e['full_name']}")
    return "\n".join(lines) + "\n"
