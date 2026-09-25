# 028 如何设计有界 worker pool 和背压？

> 难度：中级 · 分类：并发编程

## 简短回答

worker pool 用固定数量的工作者处理任务，用有界队列限制积压。背压把处理能力不足的信号传回生产者，使其等待、减速或拒绝；如果只是无限缓存待处理任务，就没有真正控制资源。

## 详细解析

### 同时限制执行和排队

下面使用两个 worker 和容量为二的任务通道，完成有限批次计算。任务位置互不重叠，结果只在所有 worker 完成后读取。生产者负责关闭任务输入，worker 不抢着关闭共享通道。

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    jobs := make(chan int, 2)
    result := make([]int, 5)
    var wg sync.WaitGroup
    for i := 0; i < 2; i++ {
        wg.Go(func() {
            for index := range jobs { result[index] = index * index }
        })
    }
    for index := range result { jobs <- index }
    close(jobs)
    wg.Wait()
    fmt.Println(result)
}
```
```output
[0 1 4 9 16]
```

这是有界批处理程序，任务是确定可终止的短计算。接入网络服务时，提交和执行都要支持取消：投递用 select 同时等待队列与 context.Done，下游调用传递 context。不能把例子的有限循环直接扩展成不受请求生命周期约束的后台系统。

### 队列越大不一定越好

若每个 worker 平均每秒处理 50 个任务，四个 worker 理想吞吐约为 200 个每秒；排队 1000 个任务意味着仅清空队列就可能需要约五秒，还未计新到达任务。若接口期限只有一秒，这个队列很可能只是在保存注定超时的请求。

容量应由允许等待时间和实际服务速率推导，并同时限制任务体积。一个队列元素可能引用几十 MB 数据，因此只限制元素数并不能精确限制内存。队列满时选择等待、拒绝还是丢弃，必须与业务语义相符：付款不能静默丢弃，采样遥测可能允许丢弃并计数。

关停时要定义停止接收、是否处理剩余任务、最长等待时间和结果归属。进程内队列没有天然持久性，不能承诺重启后任务不丢失。

## 常见误区 / 面试追问

- **先开无限 goroutine 再抢 semaphore 算有界吗？** 只限制执行，不限制等待任务和其持有内存。
- **worker 数等于 CPU 核数吗？** CPU 与 I/O 工作不同，还要看下游连接配额和单任务内存。
- **如何判断背压正常？** 同时观察队列长度、排队时间、拒绝率和完成吞吐，而不是只看 CPU。

## 参考资料

- [Go 官方并发流水线](https://go.dev/blog/pipelines)
- [Go channel 规范](https://go.dev/ref/spec#Channel_types)

[返回目录](../README.md) · [上一题](027-task-groups.md) · [下一题](029-leaks.md)
