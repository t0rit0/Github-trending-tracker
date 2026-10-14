# 06 验证多语言抓取路径

Status: resolved

`settings.yaml` 里 `languages: [python, rust]` 时的分语言 URL 拼接与合并去重逻辑已写但从未实测。跑一次多语言配置验证快照正确。

## Comments

- 2026-10-14 实测：`fetch('daily', ['python', 'rust'])` 合并 22 个仓库，重复仓库 `trending_in` 正确标注双语言；单测钉住 URL 形态、`since` 参数与去重行为。
- 期间撞上间歇性 SSL 断连（第二次），fetch 加了 3 次递增退避重试。
