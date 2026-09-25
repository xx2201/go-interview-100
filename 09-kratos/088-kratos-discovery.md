# 088 Kratos 如何接入注册发现与客户端治理？

> 难度：中级 · 分类：Kratos 工程 · 版本：v2.9.1

## 简短回答

Kratos 通过 Registrar 发布和注销实例，通过 Discovery 获取并观察服务实例；客户端结合逻辑 endpoint、resolver 与均衡器调用后端。接入注册中心只是建立地址发现链路，超时、身份、重试和容量仍需分别配置与验证。

## 详细解析

### 注册的信息从哪里来

v2.9.1 的 ServiceInstance 包含 ID、Name、Version、Metadata 和 Endpoints。App 可从传输服务获得 endpoint，并使用注入的 Registrar 注册；客户端通过 Discovery 查询或 Watch 实例变化。不同注册中心适配器的租约和故障行为不完全相同。

```text
HTTP/gRPC Server → endpoint
应用名称、实例 ID、版本 → ServiceInstance → Registrar
                                                   ↓
客户端逻辑服务名 → Discovery/Watcher → 地址更新 → 调用
```

gRPC 客户端接入常涉及 WithEndpoint 和 WithDiscovery，逻辑地址形如 `discovery:///interview.catalog`。其中服务名要与注册名称一致，不能把 HTTP 路由当成服务名；实际连接仍要满足地址可达和 TLS 身份要求。

### 注册成功不等于服务完整就绪

框架生命周期负责启动和注册协调，但不能替代应用的数据库连通、缓存预热和业务 readiness 校验。应在对外接流前完成必需准备；注册到错误网卡、容器内部地址或不可达端口，也会出现“列表里有实例但无法调用”。

关闭时先注销和停止新增流量，再等待在途请求。注销失败、客户端列表缓存和长连接都会影响实际摘流速度，需要通过故障演练观察，不能只看 App.Stop 被调用。

客户端治理要避免层层叠加重试。框架 middleware、gRPC 配置和服务网格都可能施加策略，应建立一份实际调用预算。注册中心暂时不可达时，是否保留旧地址取决于适配器和客户端行为，需按实际版本验证。

本仓库双协议测试使用本地直连，未启动 etcd、Consul 或其他注册中心。因此它验证传输与业务链路，不提供注册中心故障切换的运行证据。

## 常见误区 / 面试追问

- **一个服务的所有实例能共用同一 ID 吗？** 可能导致注册覆盖或身份冲突，实例身份应按适配器要求唯一。
- **元数据里的版本会自动实现灰度吗？** 还需要发现、选择和流量规则显式使用它。
- **发现列表更新就完成切流了吗？** 已有连接和在途请求还可能继续，需要结合连接与关停策略。

## 参考资料

- [Kratos registry 接口](https://github.com/go-kratos/kratos/blob/v2.9.1/registry/registry.go)
- [Kratos gRPC 客户端](https://github.com/go-kratos/kratos/blob/v2.9.1/transport/grpc/client.go)

[返回目录](../README.md) · [上一题](087-kratos-config.md) · [下一题](089-kratos-tests.md)
