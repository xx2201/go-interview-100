# 025 原子操作能否替代互斥锁？什么是 happens-before？

> 难度：中级 · 分类：并发编程

## 简短回答

原子操作适合独立计数、状态位或不可变快照发布，不自动保护跨字段业务约束。happens-before 描述内存操作的有序关系：通过锁、通道、原子操作等建立同步后，才能可靠解释跨 goroutine 的可见性。

## 详细解析

### 原子读取两个字段仍可能读到混合状态

设配置包含折扣比例和版本号。分别用两个原子变量存储，读取者可能先读到新版本再读到旧比例。每个读取都原子，不代表两次读取形成一致快照。可把完整配置构造成不可变对象，再通过一个原子指针发布。

```go
package main

import (
    "fmt"
    "sync/atomic"
)

type Config struct { Version int; Limit int }

func main() {
    var current atomic.Pointer[Config]
    current.Store(&Config{Version: 1, Limit: 100})
    current.Store(&Config{Version: 2, Limit: 200})
    snapshot := current.Load()
    fmt.Println(snapshot.Version, snapshot.Limit)
}
```
```output
2 200
```

关键约束是发布后不再修改 Config。原子指针只同步指针本身的发布，不会让其指向的普通字段自动变成原子字段。如果读取者自行修改 Limit，仍可能制造竞态。

### 为什么 sleep 不能代替同步

“写入后等一秒再读取”没有建立内存模型规定的同步关系，也不证明写入任务已经完成。应使用明确完成信号或锁。race-free 程序可以依据同步关系推演结果，而有数据竞争的程序不能靠某个 CPU 上反复运行正常获得保证。

CAS 循环可以实现条件更新，但竞争激烈时可能多次失败重试，并且复杂状态机可能涉及 ABA 等问题。Go 的 GC 降低某些手工内存回收难度，不会自动消除逻辑状态反复变化的风险。没有经过证明的无锁算法，不值得为了少一把锁引入。

选择原子还是锁，应该从不变量数量和可解释性出发。一个统计计数器可能用 atomic.Int64；账户余额与流水必须一致，则更适合事务或明确临界区。

## 常见误区 / 面试追问

- **原子一定更快吗？** 高频共享写仍会产生缓存一致性成本，批量或分片汇总可能更有效。
- **普通读配原子写安全吗？** 对同一被并发访问的位置不能混用未经同步的普通访问。
- **原子对象可以复制吗？** 类型化原子对象使用后不应复制，应通过指针共享同一实例。

## 参考资料

- [Go 内存模型](https://go.dev/ref/mem)
- [sync/atomic](https://pkg.go.dev/sync/atomic)

[返回目录](../README.md) · [上一题](024-mutex.md) · [下一题](026-context.md)
