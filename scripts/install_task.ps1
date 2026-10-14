# 注册 Windows 计划任务：每天按 settings.yaml 的 schedule.time 跑一次流水线。
# 用法：powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1
$ErrorActionPreference = "Stop"

$yaml = Get-Content (Join-Path $PSScriptRoot "..\settings.yaml") -Raw
if ($yaml -notmatch 'time:\s*"?(\d{1,2}:\d{2})"?') { throw "settings.yaml 里找不到 schedule.time" }
$time = $Matches[1]
$repo = Split-Path $PSScriptRoot -Parent

$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) { throw "找不到 uv，请先确认它在 PATH 里" }

$action = New-ScheduledTaskAction -Execute $uv -Argument "run main.py" -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At $time
Register-ScheduledTask -TaskName "trending-tracker" -Action $action -Trigger $trigger -Force | Out-Null
Write-Host "已注册计划任务 trending-tracker：每天 $time 在 $repo 运行 uv run main.py"
