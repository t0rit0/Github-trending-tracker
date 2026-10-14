# GitHub Trending Tracker

跟踪 GitHub Trending 榜单变化并生成日报的多智能体系统。

## Language

**快照 (Snapshot)**:
某个日期抓取的 Trending 榜单完整列表，是计算一切变化的事实来源。
_Avoid_: 榜单、抓取结果、缓存

**新上榜 (New)**:
今天在快照中、昨天不在的仓库。
_Avoid_: 新面孔、新仓库

**在榜 (Staying)**:
连续两天以上出现在快照中的仓库；首次出现的那天是其**上榜日**。
_Avoid_: 留榜、持续在榜

**掉榜 (Dropped)**:
昨天在快照中、今天不在的仓库。
_Avoid_: 下榜、消失

**日报 (Daily Report)**:
每天一份、给人读的 Markdown 文档，汇总当日快照的变化与分析。
_Avoid_: 摘要、digest、推送

**仓库笔记 (Repo Note)**:
vault 中每个仓库唯一对应的一篇笔记：frontmatter 存结构化状态，正文按日期累积分析条目。
_Avoid_: 记忆卡片、memory entry

**兴趣配置 (Interests)**:
用户以配置文件维护的关注点（语言/领域/关键词），是日报过滤与排序的唯一依据。
_Avoid_: 偏好、profile

## Roles

**Scout**:
获取当日快照的角色，纯确定性代码，不调用模型。
_Avoid_: 爬虫 agent、fetcher

**Analyst**:
对单个仓库产出结构化分析的角色，按仓库并行。
_Avoid_: worker、分析器

**Editor**:
把当日全部变化与分析汇总成一份日报的角色，每天仅一次。
_Avoid_: 汇总器、writer

**Keeper**:
读写仓库笔记、维护长期记忆的角色；流水线（v0）跑通后加入（v1）。
_Avoid_: 记忆 agent、memory manager
