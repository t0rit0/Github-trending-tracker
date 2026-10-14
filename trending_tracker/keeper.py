"""Keeper：维护 vault 仓库笔记（长期记忆）。

分工：frontmatter 与按日追加由代码确定性完成；LLM 只写当日叙事条目
（day_entry/one_liner/tags），事实与历史以输入为准。掉榜仓库纯代码更新，不调模型。
笔记路径 vault/repos/{owner}/{repo}.md。
"""
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.output import PromptedOutput
from pydantic_ai.providers.openai import OpenAIProvider

from .config import Settings


class KeeperEntry(BaseModel):
    day_entry: str   # 今日条目：1-3 条以 "- " 开头的中文要点
    one_liner: str   # 刷新后的定位，不超过 30 字（无变化可沿用旧值）
    tags: list[str]  # 2-4 个小写英文标签


def make_agent(settings: Settings) -> Agent[None, KeeperEntry]:
    # Keeper 是每仓库一次的高量调用，默认复用 analyst 的便宜模型（settings.models.keeper 可单独指定）
    model_name = settings.models.keeper or settings.models.analyst
    model = OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(
            base_url=settings.provider.base_url,
            api_key=os.environ[settings.provider.api_key_env],
        ),
    )
    return Agent(
        model,
        output_type=PromptedOutput(KeeperEntry),
        instructions=(
            "你是仓库观察员，为一个 GitHub 仓库维护长期笔记。根据旧笔记的历史条目和今日数据输出："
            "day_entry（1-3 条 '-' 开头的中文要点：今天发生了什么、与历史判断相比是延续还是变化，"
            "不要复述旧条目已有的信息）；one_liner（不超过 30 字的定位，无实质变化就沿用旧的）；"
            "tags（2-4 个小写英文领域标签）。事实以输入为准，不要编造。"
        ),
    )


def note_path(vault: Path, full_name: str) -> Path:
    owner, repo = full_name.split("/", 1)
    return Path(vault) / "repos" / owner / f"{repo}.md"


def load_note(path: Path) -> tuple[dict, str] | None:
    if not path.exists():
        return None
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", path.read_text(encoding="utf-8"), re.S)
    if not m:
        raise ValueError(f"笔记缺少 frontmatter：{path}")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def save_note(path: Path, fm: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    path.write_text(f"---\n{front}\n---\n{body}", encoding="utf-8")


def has_entry_for(body: str, day: str) -> bool:
    return f"## {day}" in body


async def update_all(
    settings: Settings, entries: list[dict], dropped: list[dict], today: str,
    concurrency: int = 5,
) -> dict:
    """更新当日所有受影响笔记（同日重跑幂等跳过），返回 {"history": {...}, "notes_updated": n}。

    history 基于更新前的旧笔记，供 Editor 引用"上次见到它是什么时候、当时怎么说"。
    """
    vault = Path(settings.vault)
    agent: Agent[None, KeeperEntry] | None = None  # 惰性构造：纯掉榜日不调 LLM 也不需要 key
    sem = asyncio.Semaphore(concurrency)
    history: dict[str, dict] = {}
    updated = 0

    async def one(entry: dict) -> None:
        nonlocal updated, agent
        full = entry["full_name"]
        path = note_path(vault, full)
        old = load_note(path)
        if old:
            fm, body = old
            if fm.get("last_seen") and fm["last_seen"] < today:
                history[full] = {
                    "last_seen": fm.get("last_seen"),
                    "days_on_list": fm.get("days_on_list"),
                    "one_liner": fm.get("one_liner"),
                }
        else:
            fm, body = {"full_name": full, "first_seen": today, "one_liner": "", "tags": []}, ""
        if has_entry_for(body, today):
            return  # 同日重跑：今日条目已在，跳过

        status = "新上榜" if entry.get("days", 1) == 1 else f"在榜第 {entry['days']} 天"
        a = entry.get("analysis") or {}
        facts = (
            f"仓库：{full}\n今日状态：{status}\n"
            f"总星 {entry.get('stars')}，今日 +{entry.get('stars_today')}，较昨日 Δ{entry.get('stars_delta')}\n"
            f"主语言：{entry.get('language') or '未知'}\n"
            f"今日分析定位：{a.get('one_liner', '（分析失败，无）')}\n"
            f"今日分析要点：{a.get('why_care', '（无）')}"
        )
        old_context = f"旧笔记最近的历史条目：\n{body[-1500:]}" if body else "（新仓库，无历史）"

        async with sem:
            try:
                if agent is None:
                    agent = make_agent(settings)
                out = (await agent.run(f"{old_context}\n\n{facts}\n")).output
            except Exception as e:  # LLM 失败降级：只记事实条目，frontmatter 照常更新
                print(f"  ! Keeper 失败 {full}: {type(e).__name__}: {e}")
                out = KeeperEntry(day_entry=f"- {status}，今日 +{entry.get('stars_today')}", one_liner="", tags=[])

        fm.update({
            "last_seen": today,
            "days_on_list": entry.get("days", 1),
            "stars": entry.get("stars"),
            "status": "on-list",
            "language": entry.get("language") or fm.get("language") or "",
            "tags": out.tags or fm.get("tags") or [],
            "one_liner": out.one_liner or fm.get("one_liner") or "",
        })
        header = body.rstrip() or f"# {full}"
        save_note(path, fm, f"{header}\n\n## {today}\n{out.day_entry}\n")
        updated += 1

    await asyncio.gather(*(one(e) for e in entries))

    for e in dropped:  # 掉榜：纯代码，只更新状态
        path = note_path(vault, e["full_name"])
        old = load_note(path)
        if not old:
            continue
        fm, body = old
        if has_entry_for(body, today):
            continue
        fm["status"] = "dropped"
        save_note(path, fm, f"{body.rstrip()}\n\n## {today}\n- 掉榜（在榜 {fm.get('days_on_list')} 天后）\n")
        updated += 1

    return {"history": history, "notes_updated": updated}
