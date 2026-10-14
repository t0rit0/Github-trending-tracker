"""Analyst 自检：单仓库失败降级、prompt 携带事实（LLM 用假 agent 替身）。"""
import asyncio

from trending_tracker import analyst
from trending_tracker.analyst import RepoAnalysis
from trending_tracker.config import Settings


class _Run:
    def __init__(self, output):
        self.output = output


class _FakeAgent:
    def __init__(self, fail_for: set[str]):
        self.fail_for = fail_for
        self.prompts: list[str] = []

    async def run(self, prompt: str):
        self.prompts.append(prompt)
        for name in self.fail_for:
            if f"仓库：{name}" in prompt:
                raise RuntimeError("boom")
        return _Run(RepoAnalysis(one_liner="定位", why_care="看点", tags=["t"]))


def test_analyze_all_degrades_per_repo_failure(monkeypatch):
    fake = _FakeAgent(fail_for={"bad/bad"})
    monkeypatch.setattr(analyst, "make_agent", lambda s: fake)
    repos = [
        {"full_name": "good/good", "description": "d", "language": "Python",
         "stars": 10, "stars_today": 5, "days": 1},
        {"full_name": "bad/bad", "description": "", "language": "",
         "stars": None, "stars_today": None, "days": 2},
    ]
    out = asyncio.run(analyst.analyze_all(Settings(), repos))
    by_name = {r["full_name"]: r["analysis"] for r in out}
    assert by_name["good/good"].one_liner == "定位"      # 失败不拖累其他仓库
    assert by_name["bad/bad"] is None                     # 降级为数据行
    assert any("今日新增：5" in p and "已连续在榜 1 天" in p for p in fake.prompts)
    assert any("描述：（无）" in p for p in fake.prompts)  # 缺描述走降级文案
