# 直接爬取 GitHub Trending 页面，而非用 Search API 近似

GitHub 没有 Trending 官方 API（2025-06 官方社区确认）。我们决定直接爬 `github.com/trending` 页面并以它为 trending 定义的唯一事实来源，而不是用 Search API 按 star 增量自行近似——自己算出的"trending"与官方榜单有系统性偏差，且要维护查询与排序逻辑。代价是页面结构变更需跟进，以解析失败时生成占位日报 + 非零退出码兜底。

## Consequences

- 匿名（未登录）请求只返回部分榜单：2026-10 实测每天约 9/25 个仓库。管线对数量不敏感，先接受；要全量需在请求头带登录 cookie（将来加 `GITHUB_COOKIE` 环境变量，非本期范围）。

