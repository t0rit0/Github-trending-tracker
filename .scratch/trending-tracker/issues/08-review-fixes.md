# 08 全栈 review 修复

Status: resolved

ponytail-review 对全部 6 个提交的审查结论：1 必修 + 2 应修 + 3 可选。本工单全部落地。

- [x] 1 必修：`uv run pytest` 收集失败（项目未装进 venv，`python -m` 只是碰巧能用）→ pyproject 加 `pythonpath = ["."]`
- [x] 2 应修：fetch 的 3 次重试是无人值守任务的保命路径，无测试 → 补一个（恒失败 → ScoutError，恰好 3 次）
- [x] 3 应修：`build_digest` 的 history 接线（v1 记忆进日报的桥）无测试 → 在现有测试里补两行断言
- [x] 4 可选：Keeper prompt 里新上榜仓库总带 "ΔNone" 噪声 → delta 为 None 时不输出该片段
- [x] 5 可选：同日重跑两处小偏差（掉榜又回榜不修正、history 不重建，次日自愈）→ 按 review 结论不改行为，只加 shortcut 注释
- [x] 6 可选：config 里 Python 从不读的 Schedule 类删除；OpenAIChatModel/Provider 三处重复 → config.make_model 单一入口

## Comments

- 2026-10-14 完成：`uv run pytest`（不带 -m）11 passed；删 Schedule 后 settings.yaml 的 schedule 键被 pydantic 忽略，加载正常（install_task.ps1 直读 yaml 不受影响）。净减约 10 行。
