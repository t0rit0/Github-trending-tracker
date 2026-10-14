"""main 流水线自检：Analyst 配置级失败时降级契约仍成立（日报照出、退出码 0）。"""
import asyncio
from datetime import date

import main
from trending_tracker import config


def _entry(name):
    return {"full_name": name, "url": f"https://github.com/{name}",
            "days": 1, "stars": 10, "stars_today": 5}


def test_analyst_config_failure_still_writes_report(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(main, "SNAPSHOTS", tmp_path / "snapshots")
    monkeypatch.setattr(main, "ANALYSES", tmp_path / "analyses")
    monkeypatch.setattr(main.config, "load", lambda: config.Settings(vault=str(tmp_path)))
    monkeypatch.setattr(main.scout, "run", lambda *a: {
        "snapshot": {"repos": [_entry("a/a")]},
        "diff": {"new": [_entry("a/a")], "staying": [], "dropped": []},
    })

    def boom(*a, **k):
        raise KeyError("LLM_API_KEY")

    async def fake_keep(*a, **k):
        return {"history": {}, "notes_updated": 0}

    async def fake_compose(*a, **k):
        return "# 日报"

    monkeypatch.setattr(main.analyst, "analyze_all", boom)
    monkeypatch.setattr(main.keeper, "update_all", fake_keep)
    monkeypatch.setattr(main.editor, "compose", fake_compose)

    assert asyncio.run(main.run()) == 0
    report = (tmp_path / "reports" / f"{date.today().isoformat()}.md").read_text(encoding="utf-8")
    assert "分析 0/1" in report  # Analyst 整体挂了也出日报；计数以当日榜单为准（不是缓存条数）
