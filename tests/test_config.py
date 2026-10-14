"""config 自检：settings.yaml 加载（未知键容忍）与简版 .env 解析。"""
import os

from trending_tracker import config


def test_load_parses_yaml_and_tolerates_unknown_keys(tmp_path):
    # settings.yaml 里有 Python 侧不再建模的键（schedule，仅供 install_task.ps1 直读），不得崩溃
    p = tmp_path / "settings.yaml"
    p.write_text(
        "schedule:\n  time: '08:00'\n"
        "scrape:\n  languages: [python, rust]\n"
        "models:\n  analyst: m1\n  editor: m2\n  keeper: ''\n", encoding="utf-8")
    s = config.load(p)
    assert s.scrape.languages == ["python", "rust"]
    assert s.models.analyst == "m1" and s.models.editor == "m2" and s.models.keeper == ""


def test_load_defaults_on_empty_yaml(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("", encoding="utf-8")
    s = config.load(p)
    assert s.scrape.window == "daily" and s.scrape.languages == ["all"]
    assert s.provider.api_key_env == "LLM_API_KEY" and s.vault == "vault"
    assert s.interests.languages == [] and s.interests.topics == []


def test_load_env_sets_new_keys_and_keeps_existing(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text("# 注释\n\nLLM_API_KEY=sk-x\nGITHUB_COOKIE=\n", encoding="utf-8")
    monkeypatch.setenv("LLM_API_KEY", "sk-real")   # 已有环境变量优先于 .env
    config.load_env(p)
    assert os.environ["LLM_API_KEY"] == "sk-real"
    assert os.environ["GITHUB_COOKIE"] == ""       # 空值也写入（scout 侧按 falsy 处理）
    os.environ.pop("GITHUB_COOKIE", None)          # 别泄漏给其他测试


def test_load_env_missing_file_is_noop(tmp_path):
    config.load_env(tmp_path / "nope.env")
