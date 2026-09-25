# 073 Protobuf 如何演进而不破坏兼容性？

> 难度：中级 · 分类：微服务

## 简短回答

Protobuf 二进制编码主要通过字段编号识别字段，已发布编号不能随意改变或复用。新增字段也需要定义缺省语义，删除字段后保留编号和名称。二进制兼容不等于 JSON、生成代码和业务语义都兼容，应分层验证。

## 详细解析

### 一个明确的消息契约

```proto
syntax = "proto3";
package interview.order.v1;
option go_package = "example.com/interview/api/order/v1;orderv1";

message Order {
  string id = 1;
  optional int64 discount_cents = 2;
  reserved 3;
  reserved "legacy_state";
}
```

discount_cents 使用 optional 表达是否提供，避免把“没有传”与“明确传零折扣”混为一谈。reserved 表明历史编号和名称不能重新用于别的含义。该片段是完整消息定义，可由固定版本生成器处理；不是某个已部署服务的协议。

### 兼容性包含四层

二进制 wire 层关注字段编号和类型编码；JSON 层关注字段名与表示；生成代码层关注调用 API 是否变化；业务层关注旧客户端如何解释新状态。改一个 enum 即使二进制能传输，也可能让旧业务分支落入未知状态处理。

新增字段时先让接收方理解它，再逐步让发送方使用；旧接收方忽略未知字段不代表它会正确执行依赖该字段的新业务约束。关键变更可能需要新方法或新协议版本，并保留迁移窗口。

不要改变字段单位而保留同一名字与编号，例如金额从元改成分；这种变更甚至可能完全不触发编译错误，却产生严重业务错误。时间精度、默认枚举和空值也应在注释与契约测试中说明。

生成器与运行库版本需固定，生成结果应可重建。协议变更评审应检查删除、重编号、类型变更、JSON 名称和旧客户端行为，而不只是看生成代码能否编译。

## 常见误区 / 面试追问

- **字段名可以随便改吗？** 对二进制编号影响有限，但 JSON 和源代码 API 可能受影响，不能只看 wire 兼容。
- **默认零值就是用户没有设置吗？** 不一定，需要存在性语义时使用适合的字段定义。
- **unknown fields 能解决所有升级吗？** 不能，保留字节不等于理解新业务语义，转成其他表示还可能丢失信息。

## 参考资料

- [Protobuf proto3 语言指南](https://protobuf.dev/programming-guides/proto3/)
- [Protobuf 字段存在性](https://protobuf.dev/programming-guides/field_presence/)

[返回目录](../README.md) · [上一题](072-grpc.md) · [下一题](074-discovery.md)
