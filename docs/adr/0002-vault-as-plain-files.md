# Obsidian vault 以纯文件方式读写，不引入记忆中间件

仓库笔记（Repo Note）由代码直接 `pathlib` 读写 markdown：frontmatter 存结构化状态，正文按日期追加分析条目。调研排除了 mem0（向量库存储，人无法直接浏览）、Letta（完整 agent 运行时，过重）和 mcp-obsidian（要求 Obsidian 桌面端常开 + REST 插件，与无人值守定时任务冲突）。按仓库名精确查找 + 每天 25 篇的规模用不上语义检索；若将来需要跨仓库图谱检索，升级路径是 basic-memory（格式保持其 Observation 兼容）。
