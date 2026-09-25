# 081 Kratos 解决哪些工程问题？何时值得引入？

> 难度：基础 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

Kratos 提供服务生命周期、HTTP/gRPC 传输、中间件、错误与配置等工程组件，帮助团队形成一致的服务开发方式。它不替代业务边界、事务与容量设计。已有简单标准库服务若不需要这些统一能力，没有必要仅为“微服务”名义增加框架。

## 详细解析

### 用本仓库的服务理解能力范围

[目录服务示例](../examples/catalog/README.md) 用同一个业务实现提供 HTTP 和 gRPC，使用统一日志、恢复与请求计数，由 App 管理启动与停止。它没有依赖真实数据库和注册中心，因此可以直接运行并测试，把学习重点放在请求和生命周期链路。

```go
package main

import (
    "fmt"
    "github.com/go-kratos/kratos/v2"
)

func main() {
    app := kratos.New(kratos.Name("interview.catalog"), kratos.Version("1.0.0"))
    fmt.Println(app.Name(), app.Version())
}
```
```output
interview.catalog 1.0.0
```

这段代码只构造应用元信息，不启动服务；真正双协议启动见示例入口。App 是组件生命周期管理器，不会因为调用 New 就自动加载业务、创建数据库或配置注册中心。

### 引入框架的判断标准

如果团队同时维护多种服务协议，希望统一错误码、中间件和装配习惯，Kratos 能减少每个服务重复建立基础设施的成本。代价是学习抽象、维护代码生成链和理解框架版本行为。调试时依然需要知道标准库、gRPC 和底层驱动发生了什么。

框架模板中的 service、biz、data 是常见职责组织方式，不是编译器强制层级。小例子可以按文件分工，大项目再按包和团队边界拆分，避免为了目录形状创建没有业务意义的转发层。

本模块明确使用 v2.9.1，并将 gRPC、Protobuf 与生成器版本记录在示例说明中。这里的选择服务于可重复学习与验证，不声称是最新版本或适合所有生产项目的版本组合。

## 常见误区 / 面试追问

- **使用 Kratos 就获得微服务治理了吗？** 组件需要正确配置与接入，注册发现、TLS 和观测后端不会凭空存在。
- **框架是不是越全越好？** 应按实际需求启用能力，避免无用依赖与难以解释的默认行为。
- **如何快速理解一个 Kratos 项目？** 从入口装配、生成 handler、service、biz、data 沿一次请求走完，再看退出路径。

## 参考资料

- [Kratos v2.9.1 官方源码](https://github.com/go-kratos/kratos/tree/v2.9.1)
- [Kratos App API](https://pkg.go.dev/github.com/go-kratos/kratos/v2@v2.9.1#App)

[返回目录](../README.md) · [下一题](082-layers.md)
