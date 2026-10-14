"""settings.yaml 加载与校验，以及简版 .env 读取。"""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


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


def make_model(settings: Settings, name: str) -> OpenAIChatModel:
    """模型构造单一入口（Analyst/Editor/Keeper 共用）。"""
    # DeepSeek 等 chat-completions 端点必须显式 OpenAIChatModel：v2 默认走 OpenAI Responses API（ADR-0003）
    return OpenAIChatModel(
        name,
        provider=OpenAIProvider(
            base_url=settings.provider.base_url,
            api_key=os.environ[settings.provider.api_key_env],
        ),
    )
