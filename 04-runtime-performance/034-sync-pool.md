# 034 sync.Pool 为什么不能用作连接池或持久缓存？

> 难度：中级 · 分类：运行时与性能

## 简短回答

sync.Pool 用来复用可丢弃的临时对象，运行时允许随时移除其中对象，Get 也不保证得到之前 Put 的对象。它不提供容量、借用期限、可靠保留和关闭协议，因此不适合数据库连接池或必须命中的缓存。

## 详细解析

### 临时缓冲区的借还协议

每次 Get 后初始化状态，用完后确保没有其他持有者再 Put。下面复用 Buffer，但只依赖“得到一个可用对象”，不依赖它的身份或一定来自上次归还。

```go
package main

import (
    "bytes"
    "fmt"
    "sync"
)

func main() {
    pool := sync.Pool{New: func() any { return new(bytes.Buffer) }}
    b := pool.Get().(*bytes.Buffer)
    b.Reset()
    b.WriteString("ready")
    result := b.String()
    b.Reset()
    pool.Put(b)
    fmt.Println(result)
}
```
```output
ready
```

Buffer.String 返回的字符串在此安全保留；若返回的是 Buffer.Bytes 提供的切片视图，再把 Buffer 归还池，下一使用者就可能覆盖仍被调用者读取的数据。必须在归还前结束所有借用，或显式复制交付的数据。

### 控制大对象滞留

某次请求把缓冲区增长到数十 MB，Reset 只重置逻辑长度，不一定释放底层容量。可以根据明确阈值决定大对象不归还，让其失去引用后由 GC 回收。阈值来自负载和内存预算，不应随意照搬别的服务。

对象池也可能增加维护成本：清理不彻底会泄露上一请求的数据，跨 goroutine 重复使用会造成竞态，频繁小对象如果本来不逃逸，则池化甚至可能增加分配与接口开销。应比较池化前后的实际分配率和吞吐，而不是默认复用就更快。

连接需要最大数量、健康检查、等待超时和主动 Close，这些是资源管理协议。数据库应使用 database/sql 提供的连接池能力，不能把连接塞进可被静默丢弃的 sync.Pool 后期待自动正确释放。

## 常见误区 / 面试追问

- **每次 GC 都一定清空 Pool 吗？** 不应依赖具体清理周期，API 只允许对象随时被移除。
- **Put 后还能读对象吗？** 除非有额外且可靠的所有权保证，否则视为已交还，不能继续访问可变内容。
- **Pool 自身线程安全等于对象线程安全吗？** 不等于，Get 后对象的并发使用仍由调用者负责。

## 参考资料

- [sync.Pool](https://pkg.go.dev/sync#Pool)
- [bytes.Buffer.Bytes](https://pkg.go.dev/bytes#Buffer.Bytes)

[返回目录](../README.md) · [上一题](033-gc-tuning.md) · [下一题](035-benchmarks.md)
