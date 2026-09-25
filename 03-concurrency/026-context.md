# 026 context 如何传递超时、取消和请求信息？

> 难度：基础 · 分类：并发编程

## 简短回答

context 沿调用链传递截止时间、取消信号和少量请求范围的元数据。取消是协作通知，不会强杀 goroutine，也不撤销已提交的副作用。创建子 context 的一方应及时调用 cancel，使用方要把它继续传给支持取消的阻塞操作。

## 详细解析

### 生命周期从请求一路向下

HTTP handler 使用请求 context，业务函数接收它，数据库查询使用 QueryContext，RPC 客户端同样继承它。若中途换成 Background，请求已离开后下游仍可能继续消耗资源。若某个操作需要更短期限，可以派生子 context，但不能把父级已到期的时间“延长”。

```go
package main

import (
    "context"
    "errors"
    "fmt"
)

func main() {
    parent, cancelParent := context.WithCancelCause(context.Background())
    child, cancelChild := context.WithCancel(parent)
    defer cancelChild()
    cancelParent(errors.New("client left"))
    <-child.Done()
    fmt.Println(child.Err())
    fmt.Println(context.Cause(child))
}
```
```output
context canceled
client left
```

Err 提供标准取消类别，Cause 可以保留更具体的原因，适合内部诊断。不要把内部原因直接作为公开错误响应，里面可能含有不适合暴露的信息。

### 信号发出后还需要收尾

cancel 返回不代表任务已经退出。发起方应等待任务组或完成通道，确保不再使用即将关闭的资源。网络操作是否立即结束还取决于库和协议；自己写的长计算循环要在合适粒度检查取消，不能只在函数入口检查一次。

context.Value 适合请求级追踪信息，不适合放数据库连接、可选业务参数或大型可变对象。用私有键类型避免冲突，核心业务参数保持显式传递，方便理解与测试。共享 context 是安全的，不代表放在 Value 里的对象就自动线程安全。

真正需要脱离请求继续执行的工作，应由应用生命周期管理或持久任务队列承接，明确上限、重试和关停规则。简单把 context 替换为 Background 并启动 goroutine，会失去请求约束，又没有建立新的任务所有者。

## 常见误区 / 面试追问

- **超时是否保证没有扣款？** 不保证，请求可能已在下游提交，需通过幂等键与状态查询确认结果。
- **只要 defer cancel 就够了吗？** 它只负责取消和相关资源释放，仍需要下游响应取消并等待任务结束。
- **是否把 context 存到长期结构体里？** 通常随操作显式传入，避免混淆不同请求的生命周期。

## 参考资料

- [context 标准库](https://pkg.go.dev/context)
- [Go 官方：Contexts and structs](https://go.dev/blog/context-and-structs)

[返回目录](../README.md) · [下一题](027-task-groups.md)
