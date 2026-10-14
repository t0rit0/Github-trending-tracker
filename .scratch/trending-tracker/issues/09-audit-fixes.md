# 09 全仓审计修复

Status: resolved

ponytail-audit 全仓审计：0 必修 + 3 应修 + 2 可选。本工单全部落地。

- [x] 1 应修：README 落后于代码 —— 流水线少了 Keeper、v1 还写着"计划"、pytest 命令带多余的 `-m`
- [x] 2 应修：API key 缺失时 Analyst 构造抛 KeyError，整天无日报（违背 main.py 自己声明的降级契约）→ `analyze_all` 外包 try/except 全部降级为数据行；补 main 流水线测试钉住契约
- [x] 3 应修：计划任务错过班次不补跑 → install_task.ps1 加 StartWhenAvailable（注册本身仍待用户执行）
- [x] 4 可选：状态行 ok 从缓存 done 计数，重跑后可能 "分析 10/9" → 改从当日 merged 计数（随 2 的测试一并覆盖）
- [x] 5 可选：RepoAnalysis.full_name 冗余（结果按仓库名为键、无人读该字段）→ 删除

## Comments

- 2026-10-14 完成：12 passed（新增 tests/test_main.py 钉住 Analyst 整体失败 → 日报照出 + 计数以当日榜单为准）。既有 data/analyses 里带 full_name 的旧条目向后兼容（row() 只取 3 个字段）。
- 计划任务注册仍未执行（系统级操作，留给用户）：`powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1`
