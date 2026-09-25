# 083 Kratos 如何通过 Protobuf 暴露 HTTP 与 gRPC？

> 难度：中级 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

在 Protobuf 中定义消息与 RPC，再用 HTTP 注解描述映射。不同生成器产生消息代码、gRPC 桩和 Kratos HTTP 适配代码，两种服务端都注册同一个业务适配实现。共享契约减少重复，但两种协议仍有各自的绑定、错误和传输行为。

## 详细解析

### 以已生成文件为证据

[catalog.proto](../examples/catalog/api/catalog.proto) 定义 GetItem，并将其映射为 GET `/v1/items/{id}`。对应生成产物为：

| 文件 | 职责 |
| --- | --- |
| [catalog.pb.go](../examples/catalog/api/catalog.pb.go) | 消息类型、反射与序列化支持 |
| [catalog_grpc.pb.go](../examples/catalog/api/catalog_grpc.pb.go) | gRPC 服务接口、注册与客户端 |
| [catalog_http.pb.go](../examples/catalog/api/catalog_http.pb.go) | HTTP 路由、参数绑定、中间件入口与结果编码 |

HTTP handler 的实际流程是绑定查询参数和路径变量、设置 operation、构造 ctx.Middleware 调用链，再调用 service.GetItem，最后通过 ctx.Result 编码响应。gRPC 桩从 Protobuf 消息调用同一个方法，协议差异停留在边界。

### 生成不能代替业务校验

字段能解码为 string，不等于符合商品 ID 的业务规则。生成代码不会自动知道空 ID、租户授权或库存约束；这些规则仍由明确的校验与业务层完成。HTTP 注解也不会自动给所有路由加认证。

直接注册普通 http.Handler 或手写路由时，不能假设自动走到生成 handler 使用的同一 middleware 调用点。示例的 `/metrics` 使用独立 HandleFunc，刻意不计入业务计数；这项边界由实际注册方式决定。

生成器版本需要固定且记录。本仓库已提交生成代码，普通运行无需 protoc；重新生成使用 [脚本](../scripts/generate_proto.py)，校验所需工具版本并定位锁定模块的官方注解目录。修改生成文件正文会在重新生成时丢失，规则应改在 proto、适配器或配置里。

双协议契约测试验证相同查询结果以及 HTTP 404 与 gRPC NotFound 的对应关系，同时保留协议自己的表示，不强行要求响应字节完全相同。

## 常见误区 / 面试追问

- **Protobuf 定义了服务就会自动监听吗？** 还需构造传输服务、注册实现并启动生命周期。
- **一个 HTTP 路径就是 operation 吗？** 生成代码使用完整 RPC 方法名作为 operation，selector 应按实际值匹配。
- **只测试 service 是否足够？** 还需验证参数绑定、生成代码注册和协议错误映射。

## 参考资料

- [Kratos HTTP 传输源码](https://github.com/go-kratos/kratos/tree/v2.9.1/transport/http)
- [Google API HTTP 注解](https://github.com/googleapis/googleapis/blob/master/google/api/http.proto)

[返回目录](../README.md) · [上一题](082-layers.md) · [下一题](084-dependency-injection.md)
