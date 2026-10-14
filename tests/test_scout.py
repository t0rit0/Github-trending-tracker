"""Scout 自检：解析真实页面 fixture + diff/days 逻辑。"""
import json
import re
from datetime import date
from pathlib import Path

from trending_tracker import scout

FIXTURE = Path(__file__).parent / "fixtures" / "trending.html"


def test_parse_real_page():
    repos = scout.parse_page(FIXTURE.read_text(encoding="utf-8"))
    # 2026-10 实测：匿名请求 trending 页只返回约 9 个仓库（见 ADR-0001）
    assert len(repos) >= 9, "trending 页应至少解析出 9 个仓库"
    first = repos[0]
    assert re.fullmatch(r"[^/]+/[^/]+", first["full_name"])
    assert first["url"] == f"https://github.com/{first['full_name']}"
    assert first["stars_today"] is not None
    assert first["rank"] == 1


def test_run_diff_days_and_delta(tmp_path, monkeypatch):
    day1 = {
        "date": "2026-10-13", "window": "daily", "languages": ["all"],
        "repos": [
            {"full_name": "a/a", "days": 1, "stars": 100, "url": "", "description": "", "language": "Python"},
            {"full_name": "b/b", "days": 3, "stars": 50, "url": "", "description": "", "language": "Rust"},
        ],
    }
    (tmp_path / "2026-10-13.json").write_text(json.dumps(day1), encoding="utf-8")
    monkeypatch.setattr(scout, "fetch", lambda *a: [
        {"rank": 1, "full_name": "a/a", "url": "", "description": "", "language": "Python", "stars": 120, "stars_today": 20},
        {"rank": 2, "full_name": "c/c", "url": "", "description": "", "language": "Rust", "stars": 10, "stars_today": 5},
    ])

    out = scout.run(tmp_path, "daily", ["all"], today=date(2026, 10, 14))
    diff = out["diff"]
    assert [r["full_name"] for r in diff["new"]] == ["c/c"]
    assert diff["new"][0]["days"] == 1
    staying = diff["staying"][0]
    assert staying["full_name"] == "a/a" and staying["days"] == 2 and staying["stars_delta"] == 20
    assert [r["full_name"] for r in diff["dropped"]] == ["b/b"]
    # 当天快照已落盘
    assert (tmp_path / "2026-10-14.json").exists()


def test_same_day_rerun_uses_previous_day(tmp_path, monkeypatch):
    # 同日重跑：对比基准仍是前一天，而不是自己
    (tmp_path / "2026-10-13.json").write_text(json.dumps(
        {"date": "2026-10-13", "repos": [{"full_name": "a/a", "days": 2, "stars": 100}]}), encoding="utf-8")
    (tmp_path / "2026-10-14.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(scout, "fetch", lambda *a: [
        {"rank": 1, "full_name": "a/a", "url": "", "description": "", "language": "", "stars": 110, "stars_today": 10}])
    out = scout.run(tmp_path, "daily", ["all"], today=date(2026, 10, 14))
    assert out["snapshot"]["repos"][0]["days"] == 3
