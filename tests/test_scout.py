"""Scout 自检：解析真实页面 fixture + diff/days 逻辑。"""
import json
import re
from datetime import date
from pathlib import Path

import pytest

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


def _page_html(*full_names: str) -> str:
    rows = "".join(
        f'<article class="Box-row"><h2><a href="/{n}"></a></h2>'
        f'<p>desc</p><span itemprop="programmingLanguage">Python</span>'
        f'<a href="/{n}/stargazers">1,234</a> 56 stars today</article>'
        for n in full_names)
    return f"<html><body>{rows}</body></html>"


def test_fetch_merges_languages_and_dedupes(monkeypatch):
    calls = []

    class _Resp:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            pass

    def fake_get(url, params=None, headers=None, **kw):
        calls.append((url, params))
        pages = {
            "https://github.com/trending/python": _Resp(_page_html("a/a", "b/b")),
            "https://github.com/trending/rust": _Resp(_page_html("b/b", "c/c")),  # b/b 两边都上榜
        }
        return pages[url]

    monkeypatch.setattr(scout.httpx, "get", fake_get)
    repos = scout.fetch("daily", ["python", "rust"])
    assert [c[0] for c in calls] == ["https://github.com/trending/python", "https://github.com/trending/rust"]
    assert calls[0][1] == {"since": "daily"}
    by_name = {r["full_name"]: r for r in repos}
    assert set(by_name) == {"a/a", "b/b", "c/c"}
    assert by_name["b/b"]["trending_in"] == ["python", "rust"]


def test_fetch_sends_cookie_when_set(monkeypatch):
    captured = {}

    class _Resp:
        text = _page_html("a/a")

        def raise_for_status(self):
            pass

    def fake_get(url, params=None, headers=None, **kw):
        captured["headers"] = headers
        return _Resp()

    monkeypatch.setattr(scout.httpx, "get", fake_get)
    monkeypatch.setenv("GITHUB_COOKIE", "user_session=x")
    scout.fetch("daily", ["all"])
    assert captured["headers"]["Cookie"] == "user_session=x"
    monkeypatch.delenv("GITHUB_COOKIE")
    scout.fetch("daily", ["all"])
    assert "Cookie" not in captured["headers"]


def test_fetch_retries_then_raises_scout_error(monkeypatch):
    # 无人值守任务的保命路径：连接错误重试 3 次才认输，并包成 ScoutError 交给 pipeline 降级
    monkeypatch.setattr(scout.time, "sleep", lambda _s: None)
    calls = []

    def fake_get(*a, **kw):
        calls.append(1)
        raise scout.httpx.ConnectError("ssl eof")

    monkeypatch.setattr(scout.httpx, "get", fake_get)
    with pytest.raises(scout.ScoutError, match="抓取失败"):
        scout.fetch("daily", ["all"])
    assert len(calls) == 3
