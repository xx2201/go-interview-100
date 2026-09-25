# 090 实战题：如何设计一个可观测、可关闭的 Kratos 服务？

> 难度：高级 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

先定义业务与协议契约，再显式装配依赖、配置有界超时、接入日志与指标，最后用应用生命周期协调退出。本题的完整实现是双协议只读目录服务；它可运行、可测试，不用未实现的仓储或占位 handler 代替实际行为。

## 详细解析

### 功能范围与真实入口

[示例说明](../examples/catalog/README.md) 给出启动命令与端口。[入口](../examples/catalog/cmd/server/main.go) 创建内存商品目录，查询 book 返回名称，查询不存在商品返回稳定缺失错误。HTTP 和 gRPC 由同一 Protobuf 契约生成并注册到同一个 service。

```text
go run ./examples/catalog/cmd/server

HTTP GET /v1/items/book → 商品响应
HTTP GET /v1/items/missing → 404 / ITEM_NOT_FOUND
gRPC Catalog.GetItem → 同一业务用例
HTTP GET /metrics → 请求与失败累计计数
```

目录构造后只读，因此多个请求可以共享查询；没有写入功能，也没有假装内存数据具有跨重启持久性。应用默认仅监听本机，明文连接便于学习；生产身份与 TLS 属于部署时必须明确接入的边界。

### 观测与退出如何串起来

[server.go](../examples/catalog/server.go) 将计数、结构化调用日志和 recovery 配置到两种协议上，设置传输期限及 HTTP 读写边界。指标只使用有限名称，不把商品 ID 变成标签，避免基数随业务数据增长。

App 接管两种 server 的启动和停止，StopTimeout 给退出设上限。CLI 正常收到退出信号后由 Run 收尾并返回；测试则显式调用 Stop 并等待 Run，避免只发信号就把任务留在后台。

当前服务没有后台写入和数据库连接，因此无需添加空清理函数。未来增加消费者时，应把停止拉取、在途确认与依赖关闭纳入同一生命周期，不能另开无人等待的 goroutine。

### 如何评价是否完成

先验证业务规则，再通过真实本地连接检查两种协议，再用 race 与 vet 检查实际执行和静态风险。生成代码已提交并可按固定工具版本重建，学习者无需手动补全 RPC 桩。

本例验证的是一个明确范围的完整服务，不声称已经验证注册中心、真实数据库、集群 TLS、压测或分布式故障恢复。那些能力应以实际接入和环境证据单独验收。

## 常见误区 / 面试追问

- **加了日志和计数就算完整可观测性吗？** 它们覆盖本例边界，跨服务还需要追踪传播、指标后端和业务告警。
- **如何扩展到订单写入？** 先定义幂等、事务与状态机，再实现真实仓储，不应直接给 map 加一个写方法就当成生产订单系统。
- **框架价值体现在哪里？** 两种传输共享契约与治理，应用生命周期统一；业务正确性仍由清晰用例负责。

## 参考资料

- [Kratos App 生命周期源码](https://github.com/go-kratos/kratos/blob/v2.9.1/app.go)
- [Kratos HTTP Server](https://github.com/go-kratos/kratos/blob/v2.9.1/transport/http/server.go)
- [Kratos gRPC Server](https://github.com/go-kratos/kratos/blob/v2.9.1/transport/grpc/server.go)

[返回目录](../README.md) · [上一题](089-kratos-tests.md) · [下一模块](../10-production-design/091-containers.md)
