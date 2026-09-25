# 027 WaitGroup 与 errgroup 如何管理一组并发任务？

> 难度：中级 · 分类：并发编程

## 简短回答

WaitGroup 负责等待任务完成，不自动传递错误或取消其他任务。errgroup 可以聚合首个非 nil 错误，并在使用 WithContext 时取消关联工作。两者都不能强行终止不响应取消的函数，也不能替代并发资源预算。

## 详细解析

### 先登记任务再等待

使用 Add/Done 时，正向计数应在启动 goroutine 之前完成，避免 Wait 先看到零而提前返回。任务中 defer Done，确保正常返回路径扣减计数；计数为负会 panic，使用后复制 WaitGroup 也会破坏同步语义。

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    values := make([]int, 2)
    var group sync.WaitGroup
    group.Go(func() { values[0] = 10 })
    group.Go(func() { values[1] = 20 })
    group.Wait()
    fmt.Println(values[0] + values[1])
}
```
```output
30
```

WaitGroup.Go 在 Go 1.25 引入，本课程基线 Go 1.26 可以使用。它减少登记与启动分离造成的错误，但传入函数不得 panic，且不返回业务错误；旧版本项目需要使用正确的 Add/Done 模式。

### 错误传播改变任务协议

商品页面并行读取价格与库存，如果任一项失败就不能返回完整页面，可用 errgroup.WithContext。每个任务返回 error，并使用派生 context 调用下游。Wait 等待全部任务结束，返回捕获到的首个错误；它不是收集所有错误的容器。

派生 context 在首个任务失败或 Wait 返回时会取消，因此不要在 Wait 成功后继续拿它发起一个新的独立查询。需要继续工作时使用正确的父 context，且仍遵守请求整体时间预算。

SetLimit 限制活跃任务数，达到上限时 Go 可能阻塞。调用方必须理解提交阻塞的生命周期，也不能在任务正在执行时随意改变限制。对于队列拒绝、优先级、持久化等要求，应使用明确任务调度设计，不能靠任务组附带解决。

## 常见误区 / 面试追问

- **Wait 之后一定没有数据竞争吗？** 它解决完成时序，但任务执行期间仍可能同时修改同一 map 或切片头。
- **errgroup 会恢复 panic 吗？** 不应把它当作 panic 恢复边界，任务错误应按约定返回。
- **部分结果可以接受时怎么办？** 明确定义每项状态及汇总策略，不要让首个错误取消掉本来有价值的独立工作。

## 参考资料

- [sync.WaitGroup](https://pkg.go.dev/sync#WaitGroup)
- [errgroup 官方文档](https://pkg.go.dev/golang.org/x/sync/errgroup)

[返回目录](../README.md) · [上一题](026-context.md) · [下一题](028-worker-pool.md)
