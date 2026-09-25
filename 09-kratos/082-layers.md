# 082 Kratos 的 service、biz、data 层如何分工？

> 难度：基础 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

service 适配协议输入输出，biz 表达用例与业务规则，data 实现存储和外部依赖。业务层声明所需的仓储接口，入口把具体实现注入。分层的价值是约束变更和副作用，不是要求每个字段穿过三次无意义转换。

## 详细解析

### 从 GetItem 的真实代码走一遍

示例的 [service.go](../examples/catalog/service.go) 接收生成的 GetItemRequest，调用 Usecase，并把业务缺失映射为稳定错误。[biz.go](../examples/catalog/biz.go) 检查取消和 ID 规则，依赖 Repo；[data.go](../examples/catalog/data.go) 用只读 map 实现查询。

```go
package main

import (
    "context"
    "fmt"
    "go-interview-100/examples/catalog"
)

func main() {
    repo := catalog.NewMemoryRepo([]catalog.Item{{ID: "book", Name: "Go"}})
    usecase := catalog.NewUsecase(repo)
    item, err := usecase.Get(context.Background(), "book")
    fmt.Println(item.ID, item.Name, err)
}
```
```output
book Go <nil>
```

业务可以脱离 HTTP/gRPC 直接运行，证明核心规则没有依赖传输请求对象。未来换成数据库仓储时，应实现同一个 Repo 契约，并保留错误与取消语义；这不意味着数据库事务性能也能被内存实现验证。

### 防止依赖方向倒置

biz 不应导入生成的 HTTP handler，也不应创建具体 SQL 客户端。否则业务测试必须启动外部系统，协议变化也会扩散到领域规则。data 可以使用业务类型，但不应把数据库行结构直接当成对外协议。

跨仓储事务需要在用例边界明确表达，不要让每个 Repo 方法各自提交，导致一个业务动作被拆成几个不一致的小事务。可以用符合现有项目的事务执行能力，但不要为仅一次查询的示例引入抽象事务框架。

小项目中某层暂时很薄是可以的，只要它承担清楚的边界职责。若一个层长期只有机械转发，又没有需要隔离的协议或规则，应重新评估其必要性。

## 常见误区 / 面试追问

- **所有错误都应该由 data 转成 HTTP 状态吗？** 不应把协议语义塞进存储实现，业务事实与传输映射可以分开。
- **Repo 是否应暴露通用 CRUD？** 优先表达用例所需操作，避免上层绕过领域约束任意修改表。
- **分层就能避免循环依赖吗？** 还需要正确接口归属与入口装配，参见 [009](../01-language-design/009-packages.md)。

## 参考资料

- [Kratos 官方布局示例](https://github.com/go-kratos/kratos-layout)
- [Kratos 官方示例仓库](https://github.com/go-kratos/examples)

[返回目录](../README.md) · [上一题](081-kratos-overview.md) · [下一题](083-transports.md)
