# 023 select 如何实现取消？为什么 default 可能造成忙等？

> 难度：中级 · 分类：并发编程

## 简短回答

select 等待多个通道操作中可执行的一个；有多个就绪分支时，不保证按源码顺序或优先取消。没有就绪分支且存在 default 时会立即执行它，因此把 select 加 default 放进无限循环可能持续占用 CPU。

## 详细解析

### 取消是一个可等待事件

下面用已取消的 context 和没有接收者的无缓冲通道，确定性验证发送可以被取消打断。这里没有依赖 Sleep 来猜测调度顺序。

```go
package main

import (
    "context"
    "fmt"
)

func send(ctx context.Context, out chan<- int, n int) error {
    select {
    case out <- n:
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    cancel()
    fmt.Println(send(ctx, make(chan int), 1))
}
```
```output
context canceled
```

如果 out 同时可发送，发送和取消都已就绪，select 可能选择发送。因此这段代码保证等待可以终止，不保证取消后绝对不再产生一次发送。若业务要求“撤销成功后绝不能提交”，需要围绕提交点设计状态同步或事务，单靠 context 不够。

### default 的合理用途

default 可以表达立即拒绝、尝试投递或丢弃非关键遥测，但要明确丢弃策略和指标。它不适合拿来轮询“有没有新消息”，否则没有消息时循环仍不断执行。应该阻塞等待事件，或使用有界定时器驱动周期任务。

当某个输入通道已关闭时，它的接收会持续就绪。多路合并若不处理 ok，就可能不断读零值并饿死其他业务。可在确认关闭后把该通道变量置为 nil，使其分支不再就绪，并在全部输入结束时退出。

超时也是生命周期问题：不要为无界循环的每轮创建长寿命 timer 后直接丢弃；优先复用明确管理的 timer，或者使用一次请求的 context deadline。具体 timer 的 Stop、Reset 语义应核对所用 Go 版本。

## 常见误区 / 面试追问

- **把取消分支放第一行能获得优先级吗？** 不能，源码顺序不提供这种保证。
- **用 default 就是非阻塞高性能吗？** 非阻塞描述等待行为，不代表 CPU 利用合理。
- **如何测试取消？** 构造受控阻塞点，触发取消并等待退出信号；不要仅靠固定 sleep 观察进程结束。

## 参考资料

- [Go 规范：select](https://go.dev/ref/spec#Select_statements)
- [context 文档](https://pkg.go.dev/context)

[返回目录](../README.md) · [上一题](022-channels.md) · [下一题](024-mutex.md)
