# 007 error、panic、recover 分别解决什么问题？

> 难度：基础 · 分类：语言设计

## 简短回答

error 表达调用者可以检查和处理的失败；panic 中断当前正常控制流并执行栈展开；recover 用于同一 goroutine 的延迟函数中接住 panic。预期的参数错误、依赖超时和资源不存在应作为错误返回，不能把 panic 当成业务分支。

## 详细解析

### 错误要同时服务机器和人

错误文字提供上下文，错误身份或类型支持程序判断。给数据库错误增加操作背景时，用 `%w` 保留错误链；判断时用 `errors.Is` 或 `errors.As`，避免依赖不稳定的字符串。是否把底层错误公开到上层，要看它是否应成为 API 契约的一部分。

```go
package main

import (
    "errors"
    "fmt"
)

var ErrMissing = errors.New("order missing")

func findOrder(id string) error {
    return fmt.Errorf("find order %s: %w", id, ErrMissing)
}

func main() {
    err := findOrder("A1")
    fmt.Println(errors.Is(err, ErrMissing))
    fmt.Println(err)
}
```
```output
true
find order A1: order missing
```

### 恢复应放在清晰边界

HTTP 或任务执行边界可以设置恢复逻辑：记录堆栈、将此次操作标记失败、返回适当状态。恢复只能处理当前 goroutine 中正在发生的 panic，父 goroutine 的 recover 无法捕获另一个 goroutine 的 panic。并且不是所有运行时致命故障都能恢复。

恢复也不会撤销已完成的数据库写入或外部调用。假如先扣库存再 panic，简单返回成功会掩盖半完成状态；需要事务、幂等与补偿来维护业务不变量。框架恢复中间件提供进程边界上的隔离能力，不能证明业务状态可继续使用。

日志建议在真正处理错误的边界记录一次，底层返回足够上下文。每一层都打印再返回会制造重复告警。面向客户端则把内部错误映射成稳定错误码，避免把数据库地址、SQL 或凭据拼入公开响应。

## 常见误区 / 面试追问

- **所有错误都应该重试吗？** 不应。参数错误通常不重试；暂时性依赖错误还要满足幂等、剩余时间和重试预算。
- **recover 后函数从 panic 位置继续吗？** 不会。控制流按照恢复和返回语义结束相关调用，不能当作任意跳转点。
- **错误包装越多越好吗？** 只有新增有用上下文才包装。重复“调用失败”没有诊断价值，参见 [085](../09-kratos/085-kratos-errors.md)。

## 参考资料

- [errors 标准库](https://pkg.go.dev/errors)
- [Go 规范：panic 与 recover](https://go.dev/ref/spec#Handling_panics)

[返回目录](../README.md) · [上一题](006-generics.md) · [下一题](008-defer.md)
