# 07 GITHUB_COOKIE 支持拿全量榜单

Status: in-progress

匿名请求只返回 ~9/25 个仓库（ADR-0001）。加 `GITHUB_COOKIE` 环境变量支持（请求头带 Cookie），用户提供登录 cookie 后验证是否恢复 25 个。需要用户提供 cookie。

## Comments

- 2026-10-14 实现完成：`GITHUB_COOKIE` 环境变量非空则随请求头发送（单测覆盖有/无 cookie 两态），`.env.example` 加了取法说明。**待用户提供 cookie 实测是否恢复 25 个。**
