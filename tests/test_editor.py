"""Editor 纯函数自检：digest 构建 + 降级版日报渲染（不调 LLM）。"""
from trending_tracker import editor


def _repo(full_name: str, **kw) -> dict:
    return {
        "full_name": full_name, "url": f"https://github.com/{full_name}",
        "description": "d", "language": "Python", "stars": 100, "stars_today": 10,
        "days": 1, "stars_delta": None, **kw,
    }


def test_build_digest_shapes_and_null_analysis():
    entries = [
        {**_repo("a/a"), "analysis": {"one_liner": "x", "why_care": "y", "tags": ["t"]}},
        {**_repo("b/b"), "analysis": None},
        {**_repo("d/d", days=2, stars_delta=5), "analysis": None},
    ]
    digest = editor.build_digest(
        "2026-10-14", {"topics": ["agent"]}, entries, [_repo("c/c", days=4)],
        history={"a/a": {"last_seen": "2026-10-01", "days_on_list": 5, "one_liner": "旧定位"}},
    )
    assert [e["full_name"] for e in digest["new"]] == ["a/a", "b/b"]
    assert digest["new"][0]["analysis"]["one_liner"] == "x"
    assert digest["new"][1]["analysis"] is None
    assert digest["new"][0]["history"]["last_seen"] == "2026-10-01"  # 老面孔带上历史
    assert digest["new"][1]["history"] is None
    assert [e["full_name"] for e in digest["staying"]] == ["d/d"]
    assert digest["dropped"] == [{"full_name": "c/c", "stars": 100, "days": 4}]
    assert digest["analysis_failed"] == ["b/b", "d/d"]


def test_fallback_report_lists_repos():
    diff = {"new": [_repo("a/a")], "staying": [_repo("b/b", days=2, stars_delta=5)], "dropped": [_repo("c/c")]}
    text = editor.fallback_report("2026-10-14", diff)
    assert "[a/a](https://github.com/a/a)" in text
    assert "第 2 天" in text and "Δ5" in text
    assert "- c/c" in text
