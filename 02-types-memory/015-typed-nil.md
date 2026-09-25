# 015 接口里的 nil 为什么不等于 nil？

> 难度：中级 · 分类：类型与内存

## 简短回答

接口值可以从语义上理解为动态类型与动态值。只有二者都不存在时，接口才等于 nil。把一个 nil 指针赋给接口后，动态类型已经存在，所以接口不等于 nil；error 返回值尤其容易踩到这个边界。

## 详细解析

### 从错误返回开始推演

下面 fail 返回具体指针类型的 nil，再被装入 error。调用者看到 err 非 nil，是因为接口携带了 `*Failure` 这个类型，而不是因为错误对象真的分配出来了。示例的方法显式允许 nil 接收者，以便安全观察行为。

```go
package main

import "fmt"

type Failure struct{}
func (*Failure) Error() string { return "failure" }
func fail() *Failure { return nil }

func main() {
    var p *Failure = fail()
    var err error = p
    fmt.Println(p == nil, err == nil, err.Error())
}
```
```output
true false failure
```

若 Error 方法访问接收者字段，就可能因解引用 nil 而 panic。接口非 nil 不代表其中对象可用，更不代表它的方法一定能安全执行。

### 修复应在返回边界

声明返回 error 的函数，在成功分支直接 `return nil`，失败时返回具体错误。不要用一个默认 nil 的具体错误指针统一返回所有路径，再期待调用者识别这个实现细节。接口作为配置项时也有类似风险：一个装了 nil 客户端指针的接口可能通过简单的 nil 检查。

不建议在业务中到处用反射实现“万能判空”。反射自身有适用类型边界，而且什么叫空是业务语义：空字符串、空切片、缺失对象不是同一个状态。入口契约和构造函数验证通常能更早、更清楚地解决问题。

接口比较还有另一个边界：如果两个接口的动态类型相同但该类型不可比较，比较可能 panic。例如动态值是切片时，不能把接口当成通用可比较容器。nil 问题与可比较性问题要分别理解。

## 常见误区 / 面试追问

- **接口的“两部分”是固定内存布局吗？** 这里是解释语义的模型，不应据此编写依赖私有布局的 unsafe 代码。
- **nil 指针能调用方法吗？** 可以发生方法调用，是否安全取决于接收者类型、方法集与方法实现，不等于自动安全。
- **如何防止回归？** 为成功返回路径检查 `err == nil`，为失败路径检查错误类型或身份，不只打印错误字符串。

## 参考资料

- [Go FAQ：nil error 为何不等于 nil](https://go.dev/doc/faq#nil_error)
- [Go 规范：比较运算](https://go.dev/ref/spec#Comparison_operators)

[返回目录](../README.md) · [上一题](014-maps.md) · [下一题](016-method-sets.md)
