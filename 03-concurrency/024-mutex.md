# 024 Mutex 和 RWMutex 如何选？为什么不能复制锁？

> 难度：基础 · 分类：并发编程

## 简短回答

Mutex 保护互斥访问，RWMutex 允许多个读者同时进入但写者独占。只有实际读操作足够多且临界区值得并行时，读写锁才可能有收益。锁在首次使用后不能复制；复制会破坏同一份数据由同一个同步对象保护的前提。

## 详细解析

### 锁保护的是不变量

缓存中的 map 与过期时间若必须一起更新，应置于同一临界区。只分别保护字段读写，也可能让调用者看见新值配旧过期时间。设计锁时先写清哪些状态必须共同成立，再决定锁的范围。

```go
package main

import (
    "fmt"
    "sync"
)

type Counter struct { mu sync.Mutex; n int }
func (c *Counter) Add() { c.mu.Lock(); defer c.mu.Unlock(); c.n++ }
func (c *Counter) Value() int { c.mu.Lock(); defer c.mu.Unlock(); return c.n }

func main() {
    var c Counter
    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() { defer wg.Done(); c.Add() }()
    }
    wg.Wait()
    fmt.Println(c.Value())
}
```
```output
100
```

方法使用指针接收者，避免复制锁与计数状态。若结构体中保存 map，复制结构体更危险：可能复制出两把锁，却仍共享同一个 map 的底层存储。

### 读锁不是随意升级的锁

RLock 内不能在未释放读锁的情况下直接 Lock 来升级；这会破坏预期并可能死锁。若先释放再加写锁，中间状态可能已变化，必须重新检查条件。对多把锁需要统一获取顺序，并避免持锁执行网络 I/O 或调用未知回调。

RWMutex 自身有计数和同步开销，写请求还会影响读者推进。对很短的 map 查询，即使读多写少，也可能没有优于 Mutex；应在接近真实访问比例、CPU 数和键分布的基准下选择。

返回受保护数据的指针或切片可能让调用者在锁外继续修改它。解决方式是返回快照、不可变对象或提供在锁内完成的操作，而不是只在 getter 里加锁就宣布线程安全。

## 常见误区 / 面试追问

- **同一 goroutine 能重复 Lock 吗？** Mutex 不提供可重入语义，重复获取会阻塞。
- **TryLock 失败能读共享字段吗？** 失败不建立同步关系，不能因此读取未经保护的状态。
- **锁是越细越好吗？** 细锁增加顺序和生命周期复杂度，应在测得竞争后再拆分。

## 参考资料

- [sync.Mutex](https://pkg.go.dev/sync#Mutex)
- [sync.RWMutex](https://pkg.go.dev/sync#RWMutex)

[返回目录](../README.md) · [上一题](023-select.md) · [下一题](025-atomics.md)
