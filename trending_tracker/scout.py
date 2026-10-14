"""Scout：抓取 trending 页、解析、落每日快照、算 diff。纯代码，不调模型。"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) trending-tracker/0.1"


class ScoutError(RuntimeError):
    """抓取或解析失败（页面改版、网络问题等），pipeline 捕获后生成占位日报。"""


def parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    repos = []
    for rank, art in enumerate(soup.select("article.Box-row"), 1):
        link = art.select_one("h2 a") or art.select_one("h1 a")
        if link is None or not link.get("href"):
            continue
        full_name = link["href"].strip("/")
        # "N stars today" 用正则从整段文本里捞，比锚定 class 更抗页面微调
        m = re.search(r"([\d,]+)\s+stars\s+(?:today|this week|this month)", art.get_text(" ", strip=True))
        stars_el = art.select_one('a[href$="/stargazers"]')
        desc_el = art.select_one("p")
        lang_el = art.select_one('[itemprop="programmingLanguage"]')
        repos.append({
            "rank": rank,
            "full_name": full_name,
            "url": f"https://github.com/{full_name}",
            "description": desc_el.get_text(strip=True) if desc_el else "",
            "language": lang_el.get_text(strip=True) if lang_el else "",
            "stars": _to_int(stars_el.get_text(strip=True)) if stars_el else None,
            "stars_today": _to_int(m.group(1)) if m else None,
        })
    return repos


def _to_int(s: str | None) -> int | None:
    return int(s.replace(",", "")) if s else None


def fetch(window: str, languages: list[str]) -> list[dict]:
    merged: dict[str, dict] = {}
    for lang in languages or ["all"]:
        url = TRENDING_URL if lang == "all" else f"{TRENDING_URL}/{lang}"
        try:
            resp = httpx.get(
                url, params={"since": window},
                headers={"User-Agent": UA}, follow_redirects=True, timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise ScoutError(f"抓取失败 {url}: {e}") from e
        repos = parse_page(resp.text)
        if not repos:
            raise ScoutError(f"解析到 0 个仓库：{url}（页面结构变了？）")
        for repo in repos:
            entry = merged.setdefault(repo["full_name"], {**repo, "trending_in": []})
            entry["trending_in"].append(lang)
    return list(merged.values())


def run(snapshots_dir: Path, window: str, languages: list[str], today: date | None = None) -> dict:
    """抓当日快照、对比前一份快照，返回 {"snapshot": ..., "diff": {new, staying, dropped}}。"""
    today = today or date.today()
    prev_by_name = _prev_lookup(snapshots_dir, today)
    entries = []
    for repo in fetch(window, languages):
        old = prev_by_name.get(repo["full_name"])
        entries.append({
            **repo,
            "days": old["days"] + 1 if old else 1,
            "stars_delta": repo["stars"] - old["stars"] if old and repo["stars"] and old["stars"] else None,
        })
    snapshot = {
        "date": today.isoformat(), "window": window, "languages": languages,
        "repos": entries,
    }
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    (snapshots_dir / f"{today.isoformat()}.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    today_names = {e["full_name"] for e in entries}
    diff = {
        "new": [e for e in entries if e["days"] == 1],
        "staying": [e for e in entries if e["days"] > 1],
        "dropped": [r for r in prev_by_name.values() if r["full_name"] not in today_names],
    }
    return {"snapshot": snapshot, "diff": diff}


def _prev_snapshot(snapshots_dir: Path, today: date) -> dict | None:
    files = sorted(p for p in snapshots_dir.glob("*.json") if p.stem < today.isoformat())
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _prev_lookup(snapshots_dir: Path, today: date) -> dict[str, dict]:
    prev = _prev_snapshot(snapshots_dir, today)
    return {r["full_name"]: r for r in prev["repos"]} if prev else {}
