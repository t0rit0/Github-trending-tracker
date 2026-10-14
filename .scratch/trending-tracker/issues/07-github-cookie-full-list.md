# 07 GITHUB_COOKIE 支持拿全量榜单

Status: open

匿名请求只返回 ~9/25 个仓库（ADR-0001）。加 `GITHUB_COOKIE` 环境变量支持（请求头带 Cookie），用户提供登录 cookie 后验证是否恢复 25 个。需要用户提供 cookie。
