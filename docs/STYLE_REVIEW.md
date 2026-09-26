# 与参考项目的行文思路核查

复核日期：2026-09-26。Go 首轮基线为 `3538d9a`，本轮 100 篇深化正文完成于 `972efb8`。参考项目固定为 [Agent-Interview-100 / ee5d4f6](https://github.com/BigKunLun/Agent-Interview-100/tree/ee5d4f6df74ec0008d2d8571b918fa461c230641)，避免把其后续变化混入比较。

## 结论

当前版本已对齐参考项目的主要行文思路：以问题切入，先给简短回答，再展开机制、场景与取舍，用误区和递进追问检验理解，最后提供资料。第二轮补上了首次核查发现的主要缺口：Review 的错误起点与修复对照、故障证据链、系统状态及容量推演、逐层追问评分，并为全部课程加入主题相关图解。

这是对教学组织方式的判断，不代表两套课程的每题长度、知识难度或技术正确性完全相同。Go 课程围绕语言、后端、微服务与 Kratos 独立撰写，没有复制参考项目的正文；本次也没有执行参考项目的全部代码。

## 文件事实与对照

| 维度 | 参考项目实际写法 | Go 深化后实际写法 | 判断 |
| --- | --- | --- | --- |
| 组织方式 | README 按主题与难度组织问题，提供学习路径 | 10 个主题、三级难度、分方向学习路径 | 递进组织一致，主题适配 Go 后端 |
| 文章骨架 | 简短回答、详细解析、误区与追问、参考资料；部分另列代码示例 | 100 篇保留四个核心部分，代码及图解嵌入详细解析 | 主线一致，标题层级无需逐项复制 |
| 基础题 | 001 用概念对照和代码解释差别 | [001](../01-language-design/001-go-design.md)从订单接口、语言约束、取舍表和边界展开；[003](../01-language-design/003-value-semantics.md)用别名图及程序解释值传递 | 从结论走到机制和选择边界 |
| 代码 Review | 107 展示问题代码，逐项诊断和修复，再汇总 | [030](../03-concurrency/030-concurrency-review.md)提供竞态反例、复现与修复；[098](../10-production-design/098-backend-review.md)展示 5 种错误输入结果，并运行修复后的 8 种边界案例 | 已补齐可独立找问题的起点和前后对照 |
| 故障题 | 104 按现象、排查、根因与恢复展开多个场景 | [040](../04-runtime-performance/040-tail-latency.md)连接时间预算、排队和诊断证据；[060](../06-database/060-pool-exhaustion.md)、[099](../10-production-design/099-incident.md)推演故障时间线与恢复阈值 | 遵循证据驱动的排查顺序，模拟数据明确标注 |
| 系统设计 | 010 从需求到组件、数据流、扩展和成本 | [096](../10-production-design/096-flash-sale.md)说明库存守恒、状态竞争、入口准入、轮询流量与容量取舍；[097](../10-production-design/097-job-platform.md)说明租约、状态和取消确认 | 以不变量贯穿正常和失败路径，避免只列组件 |
| 递进追问 | 108 每层列问题、答案要点、评分与下一层过渡 | [100](../10-production-design/100-interview-chain.md)持续修改同一订单背景，提供十层答案、20 分学习评分卡及承接理由 | 已补齐评价与递进逻辑，允许有依据的替代方案 |

参考原文：[基础题 001](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/01-agent-architecture/001-what-is-llm-agent.md)、[代码 Review 107](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/10-production-and-deployment/107-agent-code-review.md)、[故障题 104](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/10-production-and-deployment/104-agent-production-troubleshooting.md)、[系统设计 010](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/01-agent-architecture/010-production-agent-system-design.md)、[追问链 108](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/01-agent-architecture/108-interview-deep-dive-chain.md)。

## 全库统计与解释边界

参考集合取其 README 直接链接的 100 篇课程，Go 集合取本仓库 catalog.tsv 的 100 篇课程；不统计首页和独立示例工程。

| 指标 | 参考项目 | Go 首轮 | Go 深化后 |
| --- | --- | --- | --- |
| 每篇中文字符数中位数 | 1528 | 672.5 | 1553.5 |
| 含 Mermaid 围栏的课程数 | 81 | 1 | 100 |

中文字符按完整文件中 Unicode U+4E00–U+9FFF 计数，包含标题和代码注释；这不是分词统计或质量评分。Mermaid 数量不包含表格、图片等其他图示。Go 当前每篇一张图，全部实际渲染成功，并对代表性图解做目视检查；不把“可以渲染”视为所有图形表达质量已经自动验证。

核查方式为全库结构与统计检查，加基础、Review、故障、系统设计、追问等代表题型的人工内容对照，没有声称逐句审阅双方全部 200 篇文章。篇幅用于发现遗漏，表中的具体场景、因果、边界和验证才是写法判断的依据。

## 保留的差异

参考项目部分综合题在一篇中展开多个大场景；本仓库把数据库、消息、运行时和服务治理分散到相关课程，并用站内链接连接。Go 示例可以直接运行，外部数据库与分布式系统题则以明确前提推演，其验证范围见 [验收记录](VALIDATION.md)。这些差异符合课程主题，不应通过堆字数或声称不存在的生产实验来抹平。
