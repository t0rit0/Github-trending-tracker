# 05 Keeper：仓库笔记与长期记忆（v1，暂缓）

Status: resolved

流水线（v0）跑通后开工：读写 `vault/repos/owner-name.md`（frontmatter 状态 + 正文按日累积分析），跨仓库提炼洞察，日报获得"上次见到它"上下文。

## Comments

- 2026-10-14 实跑通过：9 篇笔记生成（`vault/repos/{owner}/{repo}.md`），frontmatter/追加由代码确定性完成，LLM 只写当日叙事条目；掉榜纯代码更新不调模型。
- 同日重跑幂等（当日条目已存在则跳过）；分析缓存复用，本次重跑只花了 Keeper 9 次 + Editor 1 次调用。
- history（上次见到/当时定位）已接入 Editor 输入与指令——今天全是新面孔所以暂无体现，明天起或仓库再次上榜时生效。
- 测试逼出的修复：agent 惰性构造（纯掉榜日不再因缺 API key 而炸）。
- 期间真实经历一次抓取 SSL 断连，占位日报 + 退出码 1 的降级路径按设计工作。
