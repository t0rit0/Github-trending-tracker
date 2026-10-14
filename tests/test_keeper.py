"""Keeper 自检：笔记读写、新建/掉榜更新、同日重跑幂等（LLM 用假 agent 替身）。"""
from trending_tracker import keeper
from trending_tracker.config import Settings
from trending_tracker.keeper import KeeperEntry


class _FakeRun:
    def __init__(self, output):
        self.output = output


class _FakeAgent:
    async def run(self, prompt: str):
        assert "仓库：" in prompt
        return _FakeRun(KeeperEntry(day_entry="- 测试条目", one_liner="新定位", tags=["t"]))


def _settings(vault) -> Settings:
    return Settings(models={"analyst": "m", "editor": "m"}, vault=str(vault))


def _entry(full_name: str, days: int = 1) -> dict:
    return {"full_name": full_name, "days": days, "stars": 100, "stars_today": 10,
            "stars_delta": None, "language": "Python", "url": "", "description": "",
            "analysis": {"one_liner": "a", "why_care": "b", "tags": ["x"]}}


def test_new_repo_creates_note(tmp_path, monkeypatch):
    monkeypatch.setattr(keeper, "make_agent", lambda s: _FakeAgent())
    out = __import__("asyncio").run(keeper.update_all(_settings(tmp_path), [_entry("o/r")], [], "2026-10-14"))
    assert out["notes_updated"] == 1 and out["history"] == {}
    fm, body = keeper.load_note(keeper.note_path(tmp_path, "o/r"))
    assert fm["first_seen"] == "2026-10-14" and fm["last_seen"] == "2026-10-14"
    assert fm["status"] == "on-list" and fm["one_liner"] == "新定位"
    assert "## 2026-10-14" in body and "- 测试条目" in body


def test_staying_repo_history_and_rerun_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(keeper, "make_agent", lambda s: _FakeAgent())
    # 第一天
    __import__("asyncio").run(keeper.update_all(_settings(tmp_path), [_entry("o/r", days=1)], [], "2026-10-13"))
    # 第二天：在榜第 2 天，应产生 history 且追加条目
    out = __import__("asyncio").run(keeper.update_all(_settings(tmp_path), [_entry("o/r", days=2)], [], "2026-10-14"))
    assert out["history"]["o/r"]["last_seen"] == "2026-10-13"
    assert out["notes_updated"] == 1
    _, body = keeper.load_note(keeper.note_path(tmp_path, "o/r"))
    assert body.count("## 2026-10-") == 2
    # 同日重跑：幂等，不再调用、不再追加
    out2 = __import__("asyncio").run(keeper.update_all(_settings(tmp_path), [_entry("o/r", days=2)], [], "2026-10-14"))
    assert out2["notes_updated"] == 0
    _, body2 = keeper.load_note(keeper.note_path(tmp_path, "o/r"))
    assert body2 == body


def test_dropped_updates_status_without_llm(tmp_path, monkeypatch):
    def _boom(_):
        raise AssertionError("掉榜不应调用 LLM")
    monkeypatch.setattr(keeper, "make_agent", _boom)
    __import__("asyncio").run(keeper.update_all(_settings(tmp_path), [_entry("o/r")], [], "2026-10-14"))
    out = __import__("asyncio").run(keeper.update_all(_settings(tmp_path), [], [_entry("o/r")], "2026-10-15"))
    assert out["notes_updated"] == 1
    fm, body = keeper.load_note(keeper.note_path(tmp_path, "o/r"))
    assert fm["status"] == "dropped"
    assert "掉榜" in body and fm["last_seen"] == "2026-10-14"  # last_seen 保持最后见到那天
