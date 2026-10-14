# 04 pipeline 编排 + Windows 计划任务

Status: resolved

- main.py 串起 Scout→Analyst→Editor，分层失败降级（抓取失败=占位日报+退出码 1）。
- `scripts/install_task.ps1` 读 settings.yaml 的 schedule.time 注册计划任务。
