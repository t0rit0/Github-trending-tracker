"""settings.yaml 加载与校验，以及简版 .env 读取。"""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel


class Schedule(BaseModel):
    time: str = "08:00"


class Scrape(BaseModel):
    window: str = "daily"
    languages: list[str] = ["all"]


class Provider(BaseModel):
    base_url: str = ""
    api_key_env: str = "LLM_API_KEY"


class Models(BaseModel):
    analyst: str = ""
    editor: str = ""
    keeper: str = ""   # 留空则复用 analyst 模型


class Interests(BaseModel):
    languages: list[str] = []
    topics: list[str] = []
    keywords: list[str] = []


class Settings(BaseModel):
    schedule: Schedule = Schedule()
    scrape: Scrape = Scrape()
    provider: Provider = Provider()
    models: Models = Models()
    vault: str = "vault"
    interests: Interests = Interests()


def load_env(path: Path = Path(".env")) -> None:
    # shortcut: 只支持 KEY=VALUE 与 # 注释，覆盖 .env 语义里的引号/变量展开等用不上的部分
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load(path: Path = Path("settings.yaml")) -> Settings:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Settings(**data)
