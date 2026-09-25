# 036 CPU、堆和阻塞 profile 分别回答什么问题？

> 难度：高级 · 分类：运行时与性能

## 简短回答

CPU profile 观察采样期间 CPU 时间花在哪里，heap profile 观察分配与存活内存，block 和 mutex profile 帮助定位同步等待。应根据问题选择证据：慢请求不一定消耗 CPU，内存大也不一定来自当前分配最多的函数。

## 详细解析

### 先把问题翻译成可观测量

| 问题 | 首选证据 | 容易误读的地方 |
| --- | --- | --- |
| CPU 满了 | CPU profile | 样本比例不是单次请求耗时 |
| 堆持续增长 | inuse_space 与对象引用 | 存活与累计分配不同 |
| GC 太频繁 | alloc_space、分配速率 | 小对象高频分配也可能很贵 |
| 任务互相等锁 | mutex、block profile | 需正确开启采样，注意额外开销 |

假设 CPU profile 中 JSON 编码占 40%，只有先确认采样来自相同负载和有效窗口，才能讨论优化它。若服务主要阻塞在数据库，CPU profile 可能几乎看不到那段墙钟时间，应去看追踪、连接池统计和阻塞证据。

### 采样与比较流程

在受控诊断地址采集 profile，记录实例、版本、时间窗和流量。pprof 端点可能暴露堆栈和运行信息，应绑定诊断网络并限制访问，不直接作为公网业务路由。对已生成的文件，可以离线运行：

```sh
go tool pprof -top cpu.pprof
go tool pprof -sample_index=inuse_space -top heap.pprof
go tool pprof -sample_index=alloc_space -top heap.pprof
```

这些命令需要真实采集文件，本仓库不伪造生产 profile。累计分配值与采样持续时间相关，比较两个版本要对齐工作量和运行阶段；首次预热、初始化缓存与稳定负载应分别考虑。

优化后用同样窗口重新采样，确认热点减少且总吞吐、延迟没有恶化。只看到某个函数占比下降还不够：可能是另一处变慢，分母变大。最终应比较绝对工作量和业务指标。

## 常见误区 / 面试追问

- **火焰图最宽的框就是根因吗？** 它是高占比调用路径，不一定是可以独立消除的成本，需结合调用者和业务工作量解释。
- **profile 没出现某函数就没有问题吗？** 采样可能错过短暂事件，也可能该函数一直等待而不占 CPU。
- **能永久打开所有高精度采样吗？** 先评估开销，按问题选择采样率与时间窗口。

## 参考资料

- [runtime/pprof 文档](https://pkg.go.dev/runtime/pprof)
- [net/http/pprof 文档](https://pkg.go.dev/net/http/pprof)
- [Go 诊断指南](https://go.dev/doc/diagnostics)

[返回目录](../README.md) · [下一题](037-trace.md)
