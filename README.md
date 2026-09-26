# Go Backend Interview 100

从语言设计到生产系统：用 100 个问题建立 Go 后端知识体系。

一套面向 Go 开发者的中文后端面试与工程实践课程，涵盖语言设计、类型与内存、并发、性能、数据库、缓存与消息、微服务、Kratos 和生产系统设计。适合已经掌握 Go 基本语法，希望系统准备面试、理解技术取舍或补齐工程知识的读者。

## 你能学到什么

- **理解语言与运行时**：从值传递、接口和内存共享，走到并发协调、GC 与性能诊断。
- **设计可靠的后端服务**：分析超时、事务、幂等、缓存一致性、消息重试和服务治理中的失败路径。
- **把设计落到代码**：运行 Go 示例，阅读代码 Review 的问题与修复，并通过 [Kratos HTTP/gRPC 服务](examples/catalog/README.md)串起协议、业务、仓储、中间件和生命周期。
- **练习系统设计与表达**：推演秒杀、异步任务和故障场景，用递进追问检查自己的答案是否覆盖机制与边界。

全书共 100 题，每题配有图解、简短回答、详细解析、常见误区与追问，以及延伸资料。可以按顺序学习，也可以按下面的路线选择专题。

## 知识地图

```mermaid
flowchart LR
    A[语言设计] --> B[类型与内存]
    B --> C[并发编程]
    C --> D[运行时与性能]
    D --> E[后端接口]
    E --> F[数据库]
    F --> G[缓存与消息]
    G --> H[微服务]
    H --> I[Kratos 工程]
    I --> J[生产与系统设计]
```

## 怎样使用

1. 先用一到两分钟口述答案，再阅读「简短回答」。
2. 跟着「详细解析」推演一次请求或一次故障，运行代码并核对输出。
3. 遮住答案回答追问，记录自己漏掉的边界，而不是背诵术语。
4. 用关联题补全依赖知识，用官方资料核对项目实际版本。

先读图中的对象与箭头，再回答「在哪一步失败会留下什么状态」。030 的竞态反例单独标注，098 的错误起点仅用于复现输入缺陷；不要把反例当成可复用的正确实现。

学习路线：入门按 001–030 → 041–052 → 081–085；后端工程按 041–080 → 091–095；性能专项按 017–018 → 025–040 → 060、070；Kratos 专项先读 005、009、026、050、071–079，再读 081–090。综合复习用 096–100。

## 版本与验证

示例基线为 Go 1.26，编写环境为 Go 1.26.5 / Windows amd64。语言保证、工具链实现和工程建议在正文中分别说明。标准库示例可将完整 Go 代码块保存为 main.go 后运行 `go run main.go`；依赖 Kratos 的示例需在本仓库根目录运行，以使用锁定的模块依赖。SQL、配置和架构步骤用于说明明确场景，不宣称已在真实集群中验证。

运行 `python scripts/course.py check --execute` 检查全部课程、站内链接并执行文章中的 Go 示例。环境、结果与适用范围见 [验证记录](docs/VALIDATION.md)，各模块的学习目标见 [学习计划](PLAN.md)。

## 100 题目录

### 01 · 语言设计

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 001 | 基础 | [为什么 Go 适合后端？它为简单性付出了什么代价？](01-language-design/001-go-design.md) |
| 002 | 基础 | [零值为什么重要？如何设计零值可用的类型？](01-language-design/002-zero-values.md) |
| 003 | 基础 | [Go 只有值传递，为什么修改切片却会影响调用者？](01-language-design/003-value-semantics.md) |
| 004 | 基础 | [组合与嵌入如何替代继承？](01-language-design/004-composition.md) |
| 005 | 基础 | [接口为什么隐式实现？应该由谁定义？](01-language-design/005-interfaces.md) |
| 006 | 中级 | [泛型、接口与代码生成应该如何选择？](01-language-design/006-generics.md) |
| 007 | 基础 | [error、panic、recover 分别解决什么问题？](01-language-design/007-errors.md) |
| 008 | 中级 | [defer 的求值、执行顺序与资源释放有什么陷阱？](01-language-design/008-defer.md) |
| 009 | 中级 | [包如何划分？怎样避免循环依赖和万能 utils？](01-language-design/009-packages.md) |
| 010 | 中级 | [Go Modules、版本选择与可复现构建如何工作？](01-language-design/010-modules.md) |

### 02 · 类型与内存

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 011 | 基础 | [数组和切片有什么区别？append 为什么需要接收返回值？](02-types-memory/011-slices.md) |
| 012 | 中级 | [切片截取为何可能造成内存滞留？如何控制共享？](02-types-memory/012-slice-retention.md) |
| 013 | 基础 | [string、byte、rune 如何选择？怎样正确截取中文？](02-types-memory/013-strings.md) |
| 014 | 基础 | [map 的零值、遍历和并发使用有哪些边界？](02-types-memory/014-maps.md) |
| 015 | 中级 | [接口里的 nil 为什么不等于 nil？](02-types-memory/015-typed-nil.md) |
| 016 | 中级 | [值接收者与指针接收者如何影响方法集？](02-types-memory/016-method-sets.md) |
| 017 | 中级 | [逃逸分析如何决定栈与堆分配？](02-types-memory/017-escape-analysis.md) |
| 018 | 高级 | [结构体布局、内存对齐与伪共享如何影响性能？](02-types-memory/018-memory-layout.md) |
| 019 | 中级 | [反射适合哪些边界？为什么业务热路径要谨慎？](02-types-memory/019-reflection.md) |
| 020 | 中级 | [unsafe 和零拷贝转换的收益与风险是什么？](02-types-memory/020-unsafe.md) |

### 03 · 并发编程

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 021 | 基础 | [并发与并行有什么区别？goroutine 为什么不是线程？](03-concurrency/021-concurrency.md) |
| 022 | 基础 | [channel 的发送、接收和关闭由谁负责？](03-concurrency/022-channels.md) |
| 023 | 中级 | [select 如何实现取消？为什么 default 可能造成忙等？](03-concurrency/023-select.md) |
| 024 | 基础 | [Mutex 和 RWMutex 如何选？为什么不能复制锁？](03-concurrency/024-mutex.md) |
| 025 | 中级 | [原子操作能否替代互斥锁？什么是 happens-before？](03-concurrency/025-atomics.md) |
| 026 | 基础 | [context 如何传递超时、取消和请求信息？](03-concurrency/026-context.md) |
| 027 | 中级 | [WaitGroup 与 errgroup 如何管理一组并发任务？](03-concurrency/027-task-groups.md) |
| 028 | 中级 | [如何设计有界 worker pool 和背压？](03-concurrency/028-worker-pool.md) |
| 029 | 高级 | [如何定位 goroutine 泄漏和死锁？](03-concurrency/029-leaks.md) |
| 030 | 高级 | [代码 Review：怎样修复并发聚合中的竞态与取消问题？](03-concurrency/030-concurrency-review.md) |

### 04 · 运行时与性能

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 031 | 中级 | [G、M、P 分别是什么？调度器如何分配执行机会？](04-runtime-performance/031-scheduler.md) |
| 032 | 中级 | [Go GC 如何工作？为什么低停顿不等于没有成本？](04-runtime-performance/032-gc.md) |
| 033 | 高级 | [GOGC 与 GOMEMLIMIT 如何共同影响吞吐和内存？](04-runtime-performance/033-gc-tuning.md) |
| 034 | 中级 | [sync.Pool 为什么不能用作连接池或持久缓存？](04-runtime-performance/034-sync-pool.md) |
| 035 | 中级 | [如何用 benchmark 测量性能而不是测量噪声？](04-runtime-performance/035-benchmarks.md) |
| 036 | 高级 | [CPU、堆和阻塞 profile 分别回答什么问题？](04-runtime-performance/036-pprof.md) |
| 037 | 高级 | [如何用 execution trace 定位调度与延迟问题？](04-runtime-performance/037-trace.md) |
| 038 | 中级 | [怎样减少分配、拷贝和无效格式化？](04-runtime-performance/038-allocations.md) |
| 039 | 高级 | [QPS、并发数与延迟如何做容量估算？](04-runtime-performance/039-capacity.md) |
| 040 | 高级 | [场景题：CPU 不高但 P99 激增，如何排查？](04-runtime-performance/040-tail-latency.md) |

### 05 · 后端接口

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 041 | 基础 | [一次 HTTP 请求在 Go 服务中经历哪些阶段？](05-backend-api/041-http-lifecycle.md) |
| 042 | 中级 | [HTTP 服务端与客户端超时应该如何配置？](05-backend-api/042-http-timeouts.md) |
| 043 | 基础 | [中间件的执行顺序如何影响日志、鉴权和恢复？](05-backend-api/043-middleware.md) |
| 044 | 基础 | [REST API 如何设计资源、状态码与分页？](05-backend-api/044-rest.md) |
| 045 | 中级 | [JSON 的零值、缺省与 null 如何表达？](05-backend-api/045-json.md) |
| 046 | 基础 | [认证与授权有什么区别？如何防止越权？](05-backend-api/046-auth.md) |
| 047 | 中级 | [如何实现可靠的接口幂等，而不是简单防重复？](05-backend-api/047-idempotency.md) |
| 048 | 中级 | [限流、并发限制和负载保护如何配合？](05-backend-api/048-rate-limits.md) |
| 049 | 中级 | [如何安全处理文件上传和流式响应？](05-backend-api/049-streaming.md) |
| 050 | 中级 | [优雅关闭如何处理在途请求与后台任务？](05-backend-api/050-shutdown.md) |

### 06 · 数据库

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 051 | 基础 | [database/sql 的 DB 是连接还是连接池？](06-database/051-connection-pool.md) |
| 052 | 基础 | [事务为什么必须使用同一个 Tx？如何处理提交失败？](06-database/052-transactions.md) |
| 053 | 中级 | [隔离级别、MVCC 与锁分别保证什么？](06-database/053-isolation.md) |
| 054 | 中级 | [索引为什么没有生效？如何阅读执行计划？](06-database/054-indexes.md) |
| 055 | 中级 | [如何避免 N+1 查询和深分页？](06-database/055-query-shapes.md) |
| 056 | 中级 | [乐观锁和悲观锁如何防止超卖？](06-database/056-stock-locking.md) |
| 057 | 中级 | [Schema 迁移怎样兼容滚动发布？](06-database/057-migrations.md) |
| 058 | 中级 | [读写分离为何导致刚写完却读不到？](06-database/058-replication.md) |
| 059 | 高级 | [分库分表应该如何选择分片键？](06-database/059-sharding.md) |
| 060 | 高级 | [场景题：数据库连接池耗尽，如何止血与定位？](06-database/060-pool-exhaustion.md) |

### 07 · 缓存与消息

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 061 | 基础 | [Cache Aside 如何处理命中、失效和一致性？](07-cache-messaging/061-cache-aside.md) |
| 062 | 中级 | [缓存穿透、击穿、雪崩应该分别怎样治理？](07-cache-messaging/062-cache-failures.md) |
| 063 | 中级 | [Redis 分布式锁为何需要所有权与 fencing token？](07-cache-messaging/063-distributed-locks.md) |
| 064 | 中级 | [本地缓存和分布式缓存怎样组合？](07-cache-messaging/064-cache-levels.md) |
| 065 | 中级 | [Redis 持久化与复制如何影响数据可靠性？](07-cache-messaging/065-redis-durability.md) |
| 066 | 基础 | [消息队列中的至少一次与至多一次是什么意思？](07-cache-messaging/066-delivery.md) |
| 067 | 中级 | [消费者如何做到业务幂等与有序处理？](07-cache-messaging/067-consumers.md) |
| 068 | 高级 | [Outbox 如何解决写数据库与发消息的双写问题？](07-cache-messaging/068-outbox.md) |
| 069 | 中级 | [重试、退避与死信队列如何避免故障放大？](07-cache-messaging/069-message-retries.md) |
| 070 | 高级 | [场景题：消息积压持续增长，如何算清恢复时间？](07-cache-messaging/070-backlog.md) |

### 08 · 微服务

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 071 | 基础 | [什么时候应该拆微服务？边界如何确定？](08-microservices/071-boundaries.md) |
| 072 | 基础 | [HTTP 与 gRPC 应该如何选择？](08-microservices/072-grpc.md) |
| 073 | 中级 | [Protobuf 如何演进而不破坏兼容性？](08-microservices/073-protobuf.md) |
| 074 | 中级 | [服务发现和负载均衡各解决什么问题？](08-microservices/074-discovery.md) |
| 075 | 中级 | [调用链怎样分配超时预算与重试预算？](08-microservices/075-budgets.md) |
| 076 | 中级 | [熔断、隔离与降级有什么区别？](08-microservices/076-resilience.md) |
| 077 | 高级 | [Saga 与 TCC 如何处理跨服务事务？](08-microservices/077-distributed-transactions.md) |
| 078 | 中级 | [配置与密钥怎样安全变更和轮换？](08-microservices/078-configuration.md) |
| 079 | 中级 | [日志、指标、追踪如何串起一次故障？](08-microservices/079-observability.md) |
| 080 | 高级 | [如何设计可回滚的灰度发布与流量切换？](08-microservices/080-rollouts.md) |

### 09 · Kratos 工程

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 081 | 基础 | [Kratos 解决哪些工程问题？何时值得引入？](09-kratos/081-kratos-overview.md) |
| 082 | 基础 | [Kratos 的 service、biz、data 层如何分工？](09-kratos/082-layers.md) |
| 083 | 中级 | [Kratos 如何通过 Protobuf 暴露 HTTP 与 gRPC？](09-kratos/083-transports.md) |
| 084 | 中级 | [Kratos 应用如何装配依赖并释放资源？](09-kratos/084-dependency-injection.md) |
| 085 | 中级 | [Kratos 的错误模型如何映射业务错误？](09-kratos/085-kratos-errors.md) |
| 086 | 中级 | [Kratos 中间件与 selector 应该怎样组织？](09-kratos/086-kratos-middleware.md) |
| 087 | 中级 | [Kratos 配置加载与热更新的边界是什么？](09-kratos/087-kratos-config.md) |
| 088 | 中级 | [Kratos 如何接入注册发现与客户端治理？](09-kratos/088-kratos-discovery.md) |
| 089 | 高级 | [如何测试 Kratos 服务而不依赖真实数据库？](09-kratos/089-kratos-tests.md) |
| 090 | 高级 | [实战题：如何设计一个可观测、可关闭的 Kratos 服务？](09-kratos/090-kratos-service.md) |

### 10 · 生产与系统设计

| 题号 | 难度 | 问题 |
| --- | --- | --- |
| 091 | 基础 | [Go 服务如何构建为可重复部署的容器？](10-production-design/091-containers.md) |
| 092 | 基础 | [单元、集成、契约与端到端测试如何分工？](10-production-design/092-testing.md) |
| 093 | 中级 | [Go fuzzing 与 race detector 能发现哪些问题？](10-production-design/093-fuzz-race.md) |
| 094 | 中级 | [CI 如何建立依赖、漏洞与构建质量门禁？](10-production-design/094-ci.md) |
| 095 | 中级 | [SLO、错误预算与告警阈值如何设计？](10-production-design/095-slo.md) |
| 096 | 高级 | [系统设计：如何实现不会超卖的秒杀下单链路？](10-production-design/096-flash-sale.md) |
| 097 | 高级 | [系统设计：如何构建支持重试的异步任务平台？](10-production-design/097-job-platform.md) |
| 098 | 中级 | [代码 Review：一个能运行的 HTTP 服务还缺什么？](10-production-design/098-backend-review.md) |
| 099 | 高级 | [故障演练：依赖超时如何演变为全站雪崩？](10-production-design/099-incident.md) |
| 100 | 高级 | [综合追问：从一个 Go 函数走到生产级系统设计](10-production-design/100-interview-chain.md) |

## 勘误与交流

遇到解释不清、示例错误或版本差异，欢迎提交 Issue 或 Pull Request。请附上课程题号、使用的版本、复现步骤和预期结果；涉及技术结论时，建议同时提供语言规范、标准库或组件官方文档链接。
