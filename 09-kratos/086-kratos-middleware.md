# 086 Kratos 中间件与 selector 应该怎样组织？

> 难度：中级 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

Kratos middleware 把 `Handler(context.Context, any) (any, error)` 包装成新的 Handler，可以统一处理 HTTP/gRPC 方法调用。selector 根据 operation 等信息选择是否应用中间件。必须核对匹配值、包裹顺序与未匹配路径，避免鉴权因匹配错误被绕开。

## 详细解析

### Chain 的实际执行顺序

v2.9.1 的 Chain 从末尾向前包装，因此传入列表中的第一个中间件处于最外层。下面用完整程序验证进入与返回顺序。

```go
package main

import (
    "context"
    "fmt"
    "github.com/go-kratos/kratos/v2/middleware"
)

func mark(name string) middleware.Middleware {
    return func(next middleware.Handler) middleware.Handler {
        return func(ctx context.Context, req any) (any, error) {
            fmt.Println(name, "in")
            defer fmt.Println(name, "out")
            return next(ctx, req)
        }
    }
}

func main() {
    h := middleware.Chain(mark("A"), mark("B"))(func(context.Context, any) (any, error) {
        fmt.Println("call")
        return nil, nil
    })
    if _, err := h(context.Background(), nil); err != nil { panic(err) }
}
```
```output
A in
B in
call
B out
A out
```

示例服务将计数放在日志与 recovery 外侧，因此业务 panic 被恢复成错误后，计数中间件可以观察到失败。若 recovery 在最外侧，内层没有完成的普通返回代码不一定执行，指标记录方式需要重新审视。

### selector 匹配的是哪条名字

生成的 GetItem operation 是 `/interview.catalog.v1.Catalog/GetItem`，不是 HTTP URL `/v1/items/book`。配置 Path、Prefix 或 Match 时应针对实际 operation，并为受保护与放行路径分别测试。没有 transport 信息时的匹配结果也要核对，单元测试直接用 Background 可能与真实请求不同。

认证更适合默认覆盖业务入口，再明确列出健康检查等例外；仅给少数方法名单加保护，新增方法时容易遗漏。手写 HTTP HandleFunc 不会自动经过生成 handler 的 ctx.Middleware，这也是为什么不能只检查一份 middleware 配置就宣布所有入口受保护。

中间件里不要保存每请求可变状态到共享字段，应放在局部变量或 context 中。读写请求对象也要遵守类型与所有权契约，不能假设 HTTP 与 gRPC 之外的调用永远提供同一种类型。

## 常见误区 / 面试追问

- **selector 没匹配会报错吗？** 通常会直接继续处理，错误匹配可能静默跳过能力，所以需要覆盖测试。
- **recovery 能捕获新 goroutine 的 panic 吗？** 不能，仍受同一 goroutine 的恢复规则限制。
- **指标为何与访问日志数量不一致？** 检查绑定失败、手写路由和中间件覆盖范围，而不是先怀疑计数器。

## 参考资料

- [Kratos Chain 实现](https://github.com/go-kratos/kratos/blob/v2.9.1/middleware/middleware.go)
- [Kratos selector 实现](https://github.com/go-kratos/kratos/blob/v2.9.1/middleware/selector/selector.go)

[返回目录](../README.md) · [下一题](087-kratos-config.md)
