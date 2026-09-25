# 与参考项目的行文思路核查

核查日期：2026-09-25。Go 课程基线提交为 `3538d9a`；参考项目固定为 [Agent-Interview-100 / ee5d4f6](https://github.com/BigKunLun/Agent-Interview-100/tree/ee5d4f6df74ec0008d2d8571b918fa461c230641)。

## 结论

问题驱动、主题递进、先给结论再解释、误区与追问、参考资料的基本思路一致。当前 Go 版本更接近精练的面试讲义，在案例展开、问题代码诊断和递进追问的教学深度上，尚未完全达到参考项目的展开程度。

100 篇完整正文及代码验证已经完成，这是交付完整性的结论；不能据此推断与参考项目具有同等教学深度。本次是写法核查，没有把参考项目的技术判断或示例正确性作为已验证结论。

## 文件事实与对照

| 维度 | 参考项目实际写法 | Go 仓库实际写法 | 判断 |
| --- | --- | --- | --- |
| 组织方式 | README 按主题与难度组织问题，提供学习路径 | 10 个主题、三级难度、分方向学习路径 | 主线一致，模块按 Go 后端领域调整合理 |
| 文章骨架 | 核心为简短回答、详细解析、误区与追问、参考资料；部分另列代码示例 | 100 篇均有四个核心部分，示例位于详细解析中 | 核心结构一致，不要求标题层级完全相同 |
| 基础题 | 001 先解释概念，再对照多个维度，并展示代码 | [001](../01-language-design/001-go-design.md)从订单接口解释设计取舍，附收益与成本表 | 都解释原因与取舍，Go 版本展开更短 |
| 代码 Review | 107 先展示问题代码，再逐项说明风险与修复，最后汇总 | [030](../03-concurrency/030-concurrency-review.md)、[098](../10-production-design/098-backend-review.md)主要展示修复后的完整程序与解释 | 缺少让读者独立找问题的起点及修复前后对照 |
| 故障题 | 104 展开多个故障场景，包括现象、排查步骤、根因和修复 | [040](../04-runtime-performance/040-tail-latency.md)有现象、证据表、因果链与恢复条件 | 排查思路一致，但缺少更具体的诊断输出与操作演示 |
| 系统设计 | 010 从需求、架构、组件与数据流写到扩展及成本 | [096](../10-production-design/096-flash-sale.md)明确不变量、库存权威、消息及支付失败路径 | 关键取舍存在，但接口、状态转换和容量推演仍较简略 |
| 递进追问 | 108 每层列问题、期望答案、评分标准和下一层的过渡逻辑 | [100](../10-production-design/100-interview-chain.md)列十层问题、简答及关联题 | 递进主题一致，缺少分层评分与承接说明 |

参考原文：[基础题 001](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/01-agent-architecture/001-what-is-llm-agent.md)、[代码 Review 107](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/10-production-and-deployment/107-agent-code-review.md)、[故障题 104](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/10-production-and-deployment/104-agent-production-troubleshooting.md)、[系统设计 010](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/01-agent-architecture/010-production-agent-system-design.md)、[追问链 108](https://github.com/BigKunLun/Agent-Interview-100/blob/ee5d4f6df74ec0008d2d8571b918fa461c230641/01-agent-architecture/108-interview-deep-dive-chain.md)。

## 全库统计与解释边界

参考集合取其 README 直接链接的 100 篇课程，Go 集合取本仓库 catalog.tsv 的 100 篇课程；不统计首页和独立示例工程。

| 指标 | 参考项目 | Go 仓库 |
| --- | --- | --- |
| 每篇中文字符数中位数 | 1528 | 672.5 |
| 含 Mermaid 围栏的课程数 | 81 | 1 |

中文字符按完整文件中 Unicode U+4E00–U+9FFF 计数，包含标题和代码注释；这不是中文字数分词统计，也不是质量评分。Mermaid 统计不包含表格、图片或其他图示。数字说明篇幅和呈现方式确有差异；深度判断主要来自上面的具体课程对照，不能单靠字数或图表数量下结论。

核查方式为全库结构与统计检查，加基础、Review、故障、系统设计、追问等代表题型的人工内容对照；没有声称逐句审阅两边全部 200 篇文章。

## 建议的改进顺序

1. 优先补强 030、098：问题代码 → 可复现触发条件 → 逐项诊断 → 对应修复 → 验证结果。错误代码必须清楚标为反例，与可执行正确示例的自动验证规则分开。
2. 补强 100：为各层增加答案要点、合格与优秀的区别，以及为什么自然过渡到下一问。
3. 补强 040、096 等综合题：按需要加入请求时序、状态转移、具体诊断证据和带数字的容量推演；模拟数据须明确标注。

应以读者能否完成推演和练习为准，不为凑篇幅给所有课程机械增加图表，也不要求复制参考项目的措辞与技术实现。
