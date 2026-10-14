"""入口：uv run main.py —— 跑当日流水线（当前只有 Scout，Analyst/Editor 随 02/03 落地）。"""
from pathlib import Path

from trending_tracker import config, scout


def main() -> None:
    settings = config.load()
    config.load_env()
    result = scout.run(Path("data/snapshots"), settings.scrape.window, settings.scrape.languages)
    snap, diff = result["snapshot"], result["diff"]
    print(f"{snap['date']} 快照：{len(snap['repos'])} 个仓库 | "
          f"新上榜 {len(diff['new'])} | 在榜 {len(diff['staying'])} | 掉榜 {len(diff['dropped'])}")
    for e in diff["new"][:5]:
        print(f"  ★ {e['full_name']} (+{e['stars_today']}/today, {e['language'] or '?'}) {e['description'][:60]}")


if __name__ == "__main__":
    main()
