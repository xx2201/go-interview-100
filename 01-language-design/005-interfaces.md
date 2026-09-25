# 005 接口为什么隐式实现？应该由谁定义？

> 难度：基础 · 分类：语言设计

## 简短回答

一个类型的方法集满足接口要求，就能作为该接口使用，无需声明 implements。接口描述调用者需要的行为。业务中的接口通常放在消费方，保持足够小，让实现能够自然满足它；不要机械地给每个结构体生成一个等大的接口。

## 详细解析

### 让业务决定能力边界

订单结算只需要查询价格，不需要知道价格存放在数据库、内存还是远程服务。消费方声明一个价格查询接口，具体实现只要有匹配方法就能注入。下面的内存实现完整可运行，也说明测试替身不需要继承业务基类。

```go
package main

import (
    "fmt"
    "errors"
)

type PriceReader interface { Price(string) (int, error) }
type Prices map[string]int

func (p Prices) Price(sku string) (int, error) {
    n, ok := p[sku]
    if !ok { return 0, errors.New("unknown sku") }
    return n, nil
}

func total(p PriceReader, sku string, count int) (int, error) {
    if count <= 0 { return 0, errors.New("count must be positive") }
    price, err := p.Price(sku)
    if err != nil { return 0, err }
    return price * count, nil
}

func main() {
    n, err := total(Prices{"book": 30}, "book", 2)
    fmt.Println(n, err)
}
```
```output
60 <nil>
```

### 小接口怎样降低耦合

如果把整个数据库客户端的方法都放进 PriceReader，每个替身都必须实现大量无关行为，业务也更容易越过边界。反过来，过度切成几十个只使用一次的接口会使装配难以理解。是否需要接口，取决于是否存在稳定行为边界、替换需求或隔离副作用的测试需求。

「接受接口、返回具体类型」是常见设计建议，不是语法规则。构造函数返回具体类型能让调用者选择所需接口；工厂确实要隐藏实现或返回多种实现时，返回接口也合理。设计时应写明错误语义和并发约束，方法签名本身无法表达这些契约。

示例用整数表示最小货币单位，避免把浮点误差引入价格计算，但它没有处理任意规模金额溢出；真实金额边界应由业务范围校验确定。这说明接口解耦并不能代替业务正确性。

## 常见误区 / 面试追问

- **接口越多越符合解耦吗？** 不一定。没有稳定边界的接口只是把变更复制到另一份声明中。
- **隐式实现会隐藏错误吗？** 不匹配的方法集在赋值或传参时由编译器检查；可用编译期赋值断言明确实现意图。
- **为什么某类型指针实现了接口而值没有？** 方法集不同，参见 [016](../02-types-memory/016-method-sets.md)。

## 参考资料

- [Go 规范：接口类型](https://go.dev/ref/spec#Interface_types)
- [Go 官方代码评审建议：接口](https://go.dev/wiki/CodeReviewComments#interfaces)

[返回目录](../README.md) · [上一题](004-composition.md) · [下一题](006-generics.md)
