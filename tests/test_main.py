"""main 流水线自检：四条降级路径与重跑缓存（网络/LLM 全部用替身）。"""
import asyncio
import json
from datetime import date

import main
from trending_tracker import analyst, config


def _entry(name):
    return {"full_name": name, "url": f"https://github.com/{name}",
            "days": 1, "stars": 10, "stars_today": 5}


def _patch(tmp_path, monkeypatch, analyze=None, compose=None, scout=None):
    monkeypatch.setattr(main, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(main, "SNAPSHOTS", tmp_path / "snapshots")
    monkeypatch.setattr(main, "ANALYSES", tmp_path / "analyses")
    monkeypatch.setattr(main.config, "load", lambda: config.Settings(vault=str(tmp_path)))
    entry = _entry("a/a")
    monkeypatch.setattr(main.scout, "run", scout or (lambda *a: {
        "snapshot": {"repos": [entry]},
        "diff": {"new": [entry], "staying": [], "dropped": []},
    }))

    async def fake_keep(*a, **k):
        return {"history": {}, "notes_updated": 0}

    monkeypatch.setattr(main.keeper, "update_all", fake_keep)
    if analyze:
        monkeypatch.setattr(main.analyst, "analyze_all", analyze)
    if compose:
        monkeypatch.setattr(main.editor, "compose", compose)


def _report(tmp_path) -> str:
    return (tmp_path / "reports" / f"{date.today().isoformat()}.md").read_text(encoding="utf-8")


async def _fake_compose(_s, _digest):
    return "# 日报"


def test_happy_path_writes_report(tmp_path, monkeypatch):
    async def fake_analyze(_s, todo):
        return [{**r, "analysis": analyst.RepoAnalysis(one_liner="定位", why_care="看点", tags=["t"])} for r in todo]

    async def compose(_s, digest):
        assert digest["new"][0]["analysis"]["one_liner"] == "定位"   # 分析真实送进了 Editor 的输入
        return "# 日报"

    _patch(tmp_path, monkeypatch, analyze=fake_analyze, compose=compose)
    assert asyncio.run(main.run()) == 0
    text = _report(tmp_path)
    assert "Editor ✓" in text and "分析 1/1" in text and "笔记 0 篇" in text


def test_rerun_uses_cached_analyses(tmp_path, monkeypatch):
    # 当日重跑：已有分析直接复用，不再调 LLM（省钱 + 幂等）
    analyses = tmp_path / "analyses"
    analyses.mkdir(parents=True)
    (analyses / f"{date.today().isoformat()}.json").write_text(json.dumps(
        {"a/a": {"one_liner": "缓存定位", "why_care": "w", "tags": ["t"]}}, ensure_ascii=False), encoding="utf-8")

    def must_not_call(*a, **k):
        raise AssertionError("当日已有分析不应重跑")

    _patch(tmp_path, monkeypatch, analyze=must_not_call, compose=_fake_compose)
    assert asyncio.run(main.run()) == 0
    assert "分析 1/1" in _report(tmp_path)


def test_analyst_config_failure_still_writes_report(tmp_path, monkeypatch):
    # 配置级失败（如 key 缺失）→ 全部降级为数据行，日报照出、退出码 0（main.py 声明的降级契约）
    def boom(*a, **k):
        raise KeyError("LLM_API_KEY")

    async def compose(_s, _d):
        return "# 日报"

    _patch(tmp_path, monkeypatch, analyze=boom, compose=compose)
    assert asyncio.run(main.run()) == 0
    assert "分析 0/1" in _report(tmp_path)  # 计数以当日榜单为准（不是缓存条数）


def test_editor_failure_falls_back_and_exits_1(tmp_path, monkeypatch):
    async def fake_analyze(_s, todo):
        return [{**r, "analysis": None} for r in todo]

    async def boom(*a, **k):
        raise RuntimeError("editor down")

    _patch(tmp_path, monkeypatch, analyze=fake_analyze, compose=boom)
    assert asyncio.run(main.run()) == 1
    text = _report(tmp_path)
    assert "## 新上榜" in text and "[a/a](https://github.com/a/a)" in text and "Editor ✗" in text


def test_scout_failure_placeholder_and_exits_1(tmp_path, monkeypatch):
    def boom(*a):
        raise main.scout.ScoutError("抓取失败 https://github.com/trending: x")

    _patch(tmp_path, monkeypatch, scout=boom)
    assert asyncio.run(main.run()) == 1
    assert "抓取失败" in _report(tmp_path)
