# 050 优雅关闭如何处理在途请求与后台任务？

> 难度：中级 · 分类：后端接口

## 简短回答

优雅关闭先停止接收新工作，再给在途工作有限时间完成，最后关闭依赖。HTTP Shutdown 会关闭监听器并等待适用的活跃连接收尾，但不自动管理所有后台任务和 hijacked 连接；主流程必须等待关停结束后再退出。

## 详细解析

### 顺序决定是否丢请求

先关闭数据库再等待 handler，会让仍在处理的请求突然失去依赖。合理顺序是让实例不再被分配新流量，停止入口，等待请求与后台任务，最后释放连接、刷出必要遥测。流量摘除有传播时间，应与部署平台的终止宽限期协调。

下面在本地真实监听一个空闲 HTTP 服务，执行关闭并确认 Serve 正常以 ErrServerClosed 结束。它验证空闲关停路径，带在途请求的验证还需控制请求阻塞与完成信号。

```go
package main

import (
    "context"
    "errors"
    "fmt"
    "net"
    "net/http"
    "time"
)

func main() {
    listener, err := net.Listen("tcp", "127.0.0.1:0")
    if err != nil { panic(err) }
    server := &http.Server{Handler: http.NewServeMux(), ReadHeaderTimeout: time.Second}
    done := make(chan error, 1)
    go func() { done <- server.Serve(listener) }()
    ctx, cancel := context.WithTimeout(context.Background(), time.Second)
    defer cancel()
    if err := server.Shutdown(ctx); err != nil { panic(err) }
    fmt.Println(errors.Is(<-done, http.ErrServerClosed))
}
```
```output
true
```

### 关停超时不是自动完成

调用 Shutdown 时应使用独立且有期限的 context；若直接使用已因退出信号取消的 context，会立即失去等待机会。期限耗尽后如何处理剩余连接和任务，要有明确策略，并记录未完成工作。即使强制关闭，也不能假设已经撤销外部副作用。

WebSocket 等被劫持连接需要自行通知和等待，队列消费者要停止拉取并处理未确认消息，周期任务要取消并等待结束。注册关闭回调不一定等于所有回调都已完成，应核对框架实际等待语义。

测试应覆盖空闲、正常在途、超时请求、长期连接和后台任务。每次部署都出现少量错误，可能是退出顺序有问题，不应自然归因于“发布总有抖动”。

## 常见误区 / 面试追问

- **收到信号直接 os.Exit 可以吗？** 会绕过正常清理，主流程应协调退出。
- **Shutdown 会取消所有 handler 吗？** 不应这样理解，它等待适用请求收尾，业务取消需要自己的生命周期设计。
- **宽限期越长越好吗？** 太长拖慢故障替换，太短打断正常请求，应结合请求期限和任务恢复能力选择。

## 参考资料

- [http.Server.Shutdown](https://pkg.go.dev/net/http#Server.Shutdown)
- [signal.NotifyContext](https://pkg.go.dev/os/signal#NotifyContext)

[返回目录](../README.md) · [上一题](049-streaming.md) · [下一模块](../06-database/051-connection-pool.md)
