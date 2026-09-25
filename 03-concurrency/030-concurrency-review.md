# 030 代码 Review：怎样修复并发聚合中的竞态与取消问题？

> 难度：高级 · 分类：并发编程

## 简短回答

审查并发聚合时，逐项检查任务上限、结果所有权、错误传播、取消响应和返回前等待。常见错误是多个 goroutine 同时 append 同一切片、先返回再留下发送者、只限制下游连接却不限制任务数量。

## 详细解析

### 明确需要保持的行为

本题处理一批整数，返回对应平方；任务取消时返回 context 错误，不返回半成品。固定最多两个 worker，结果按输入索引写入。这个例子用有限计算模拟工作，不包含外部 I/O；替换为 HTTP 查询时必须把 ctx 传给请求。

```go
package main

import (
    "context"
    "fmt"
    "sync"
)

func square(ctx context.Context, input []int) ([]int, error) {
    if err := ctx.Err(); err != nil { return nil, err }
    result := make([]int, len(input))
    jobs := make(chan int)
    var wg sync.WaitGroup
    for i := 0; i < 2; i++ {
        wg.Go(func() {
            for {
                select {
                case <-ctx.Done(): return
                case index, ok := <-jobs:
                    if !ok { return }
                    result[index] = input[index] * input[index]
                }
            }
        })
    }
dispatch:
    for index := range input {
        select {
        case <-ctx.Done(): break dispatch
        case jobs <- index:
        }
    }
    close(jobs)
    wg.Wait()
    if err := ctx.Err(); err != nil { return nil, err }
    return result, nil
}

func main() {
    result, err := square(context.Background(), []int{2, 3, 4})
    fmt.Println(result, err)
    ctx, cancel := context.WithCancel(context.Background())
    cancel()
    _, err = square(ctx, []int{2})
    fmt.Println(err)
}
```
```output
[4 9 16] <nil>
context canceled
```

### 为什么这几处修改有效

结果切片长度一次确定，每个索引只分配给一个 worker，避免共同修改切片头。只有生产者关闭 jobs，worker 只读；返回前 Wait 确保没有后台任务继续访问 result。无缓冲输入把排队压力留在提交方，而不是无限创建任务。

最终检查 ctx.Err 定义了取消优先于返回结果的策略，但取消仍可能发生在最后检查之后。它不是与外部副作用原子提交的协议。本例不会无限等待，因为计算有界；对不响应取消的下游，Wait 仍可能一直等，这是必须在依赖层解决的限制。

输入切片在函数期间由调用者保持不变，整数范围也限制在平方不会溢出的业务域。并发正确性不能替代数据范围校验。空输入能够正常关闭通道并等待，输出为空结果。

## 常见误区 / 面试追问

- **改成加锁 append 可以吗？** 可以避免那一处竞态，但输出顺序变成完成顺序，仍需检查是否符合契约。
- **只跑成功路径能验证取消吗？** 不能，至少覆盖预取消和运行中取消；后者需要可控阻塞任务来确保命中路径。
- **如何处理任意任务返回错误？** 可以采用 errgroup 配合有界投递，或单独定义错误收集协议，不能静默丢弃错误。

## 参考资料

- [Go race detector](https://go.dev/doc/articles/race_detector)
- [sync.WaitGroup](https://pkg.go.dev/sync#WaitGroup)

[返回目录](../README.md) · [上一题](029-leaks.md) · [下一模块](../04-runtime-performance/031-scheduler.md)
