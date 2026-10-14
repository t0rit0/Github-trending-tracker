# 01 Scout：抓取 trending 页 + 快照 + diff

Status: resolved

- 抓 `github.com/trending`（window/languages 来自 settings.yaml），解析 `article.Box-row`。
- 每日快照存 `data/snapshots/YYYY-MM-DD.json`，含 days（连续在榜天数）与 stars_delta。
- diff 产出 新上榜/在榜/掉榜；解析出 0 仓库视为页面改版，抛 ScoutError。

## Comments

- 2026-10-14 实跑通过：9 仓库入快照、首日全部新上榜；3 个测试（真实页面解析 / diff+days+delta / 同日重跑基准）全绿。
- 发现并记录（ADR-0001 Consequences）：匿名请求只返回约 9/25 个仓库；全量需登录 cookie，非本期范围。
- 环境坑：系统 `Temp\pytest-of-vic` ACL 损坏（WinError 5，删不掉），pytest basetemp 固定为 repo 根下 `.pytest-tmp/`。
