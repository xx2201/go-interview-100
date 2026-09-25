# 085 Kratos 的错误模型如何映射业务错误？

> 难度：中级 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

Kratos 错误包含 code、reason、message 和 metadata，并提供 HTTP 与 gRPC 状态转换。code 表达协议类别，reason 表达稳定业务原因，message 面向阅读。业务判断不应依赖可变的错误文字，内部 cause 也不应无筛选地暴露给客户端。

## 详细解析

### 同一业务错误跨两种协议

```go
package main

import (
    "fmt"
    kerrors "github.com/go-kratos/kratos/v2/errors"
    "google.golang.org/grpc/status"
)

func main() {
    err := kerrors.NotFound("ITEM_NOT_FOUND", "item not found")
    fmt.Println(kerrors.Code(err), kerrors.Reason(err))
    fmt.Println(status.Code(err))
}
```
```output
404 ITEM_NOT_FOUND
NotFound
```

本仓库的 service 把领域 ErrMissing 转成这个错误，HTTP 与 gRPC 测试验证各自返回协议类别。领域层保留“商品缺失”的事实，不需要知道 HTTP 数值或 gRPC 枚举。

### 错误字段有不同稳定性

客户端可根据 reason 选择业务分支，message 可以在不破坏逻辑判断的前提下改善描述。metadata 用于约定的附加信息，例如可公开的字段错误；不要把 SQL、内部主机名或凭据塞进去。需要根因时可用 WithCause 保留错误链，日志边界再进行受控记录。

v2.9.1 的 FromError 支持包装错误与 gRPC 状态转换；对于普通 error，会构造未知类别并使用其 Error 文本。因此不能假设框架会自动为所有数据库错误脱敏。对外错误映射是服务边界职责，未知错误应转成稳定公开信息，同时内部保留诊断证据。

超时与取消也要按实际协议语义处理。服务端自行产生的 context 错误、客户端本地 deadline 和远端业务错误可能经历不同路径，应通过真实协议测试确认，而不是只调用一个转换函数就推断所有情况。

## 常见误区 / 面试追问

- **所有业务失败都返回 500 吗？** 应区分参数、权限、缺失、冲突与内部异常，便于客户端和监控正确处理。
- **reason 可以随文案一起改吗？** 若已成为客户端契约，应保持兼容或显式版本化。
- **每层都记录错误是否更安全？** 常导致重复日志，底层加上下文，上层在处理边界记录即可。

## 参考资料

- [Kratos v2.9.1 errors 实现](https://github.com/go-kratos/kratos/blob/v2.9.1/errors/errors.go)
- [Kratos HTTP/gRPC 状态映射](https://github.com/go-kratos/kratos/tree/v2.9.1/transport/http/status)

[返回目录](../README.md) · [上一题](084-dependency-injection.md) · [下一题](086-kratos-middleware.md)
