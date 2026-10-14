"""入口：uv run main.py —— Scout → Analyst×N → Editor 流水线。

失败降级（Q15 共识）：
- 抓取失败：占位日报 + 退出码 1；
- 单仓库分析失败：日报里降级为数据行，不阻塞其他仓库；
- Editor 失败：快照与分析已落盘，用纯数据降级版日报顶上，退出码 1（重跑只重做 Editor）。
"""
import asyncio
import json
import sys
from datetime import date
from pathlib import Path

from trending_tracker import analyst, config, editor, keeper, scout

REPORTS = Path("reports")
SNAPSHOTS = Path("data/snapshots")
ANALYSES = Path("data/analyses")


async def run() -> int:
    settings = config.load()
    config.load_env()
    today = date.today().isoformat()

    # 1) Scout
    try:
        result = scout.run(SNAPSHOTS, settings.scrape.window, settings.scrape.languages)
    except scout.ScoutError as e:
        REPORTS.mkdir(parents=True, exist_ok=True)
        (REPORTS / f"{today}.md").write_text(
            f"# GitHub Trending 日报 · {today}\n\n今日抓取失败：{e}\n", encoding="utf-8")
        print(f"! 抓取失败：{e}")
        return 1
    snap, diff = result["snapshot"], result["diff"]
    print(f"{today} 快照：{len(snap['repos'])} 仓库 | 新上榜 {len(diff['new'])} 在榜 {len(diff['staying'])} 掉榜 {len(diff['dropped'])}")

    # 2) Analyst（当日已有分析的不重跑，重跑只补缺）
    analyses_path = ANALYSES / f"{today}.json"
    done: dict[str, dict] = {}
    if analyses_path.exists():
        done = json.loads(analyses_path.read_text(encoding="utf-8"))
    todo = [e for e in diff["new"] + diff["staying"] if e["full_name"] not in done]
    analyzed = []
    if todo:
        analyzed = await analyst.analyze_all(settings, todo)
        done.update({r["full_name"]: r["analysis"].model_dump() for r in analyzed if r["analysis"]})
    ANALYSES.mkdir(parents=True, exist_ok=True)
    analyses_path.write_text(json.dumps(done, ensure_ascii=False, indent=2), encoding="utf-8")
    merged = [{**e, "analysis": done.get(e["full_name"])} for e in diff["new"] + diff["staying"]]
    ok, total = sum(a is not None for a in done.values()), len(merged)

    # 3) Keeper：更新仓库笔记（同日重跑幂等），历史基于更新前的旧笔记
    keep = await keeper.update_all(settings, merged, diff["dropped"], today)

    # 4) Editor
    REPORTS.mkdir(parents=True, exist_ok=True)
    digest = editor.build_digest(today, settings.interests.model_dump(), merged, diff["dropped"], history=keep["history"])
    status_ok = f"抓取 ✓ {len(snap['repos'])} 仓库 | 分析 {ok}/{total} | 笔记 {keep['notes_updated']} 篇"
    try:
        body = await editor.compose(settings, digest)
        status = f"\n\n---\n**运行状态**：{status_ok} | Editor ✓\n"
        (REPORTS / f"{today}.md").write_text(body.rstrip() + status, encoding="utf-8")
    except Exception as e:
        print(f"! Editor 失败：{type(e).__name__}: {e}")
        status = f"\n\n---\n**运行状态**：{status_ok} | Editor ✗（降级为纯数据版）\n"
        (REPORTS / f"{today}.md").write_text(editor.fallback_report(today, diff).rstrip() + status, encoding="utf-8")
        return 1
    print(f"日报已生成：reports/{today}.md（{status_ok}）")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
