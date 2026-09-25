# 045 JSON 的零值、缺省与 null 如何表达？

> 难度：中级 · 分类：后端接口

## 简短回答

普通数值字段无法区分“未提供”与“提供零”；指针可以区分零与 nil，但对新建目标对象，字段缺失与显式 null 都可能得到 nil。若协议需要三态，使用显式存在标记或 RawMessage 检查，避免把更新请求误解为全量覆盖。

## 详细解析

### 先写业务语义，再选 Go 类型

更新限额时，缺失可以表示保持原值，零表示禁止使用，null 可以表示恢复默认。三者含义不同，单个 int 或 *int 都不足以完整表达。下面通过映射检查键是否存在，展示三态信息如何保留。

```go
package main

import (
    "encoding/json"
    "fmt"
)

func main() {
    for _, input := range []string{`{}`, `{"limit":null}`, `{"limit":0}`} {
        var fields map[string]json.RawMessage
        if err := json.Unmarshal([]byte(input), &fields); err != nil { panic(err) }
        raw, exists := fields["limit"]
        fmt.Printf("%t %s\n", exists, raw)
    }
}
```
```output
false 
true null
true 0
```

实际更新入口应进一步验证允许的键、null 是否被协议允许、数值范围和授权，不能因为 RawMessage 可容纳任意内容就把它直接传进数据库。

### 解码严格性也是契约

对请求体先限制大小，再决定是否 DisallowUnknownFields。严格拒绝未知字段能发现拼写错误，但滚动升级与不同版本客户端可能需要兼容策略。Decoder.Decode 成功读取一个值后，还要确认后面没有第二个 JSON 值或额外垃圾，不能把“第一次解码成功”等同于整个请求合法。

动态解码到 any 时，数字默认可能变成 float64，大整数精度可能丢失；可以使用 UseNumber，再按业务类型解析并检查范围。标识符若在多语言客户端间传递，也应明确整数与字符串的协议选择。

omitempty 是编码规则，不是“字段有没有被用户提供”的历史记录。不要复用已有对象反复解码不同更新请求，否则未出现的字段可能保留旧值，引入跨请求污染。

## 常见误区 / 面试追问

- **指针能完整解决三态吗？** 对新对象，缺失和 null 常都成为 nil，需要额外存在信息。
- **JSON 能保证金额精确吗？** 编码形式不替代数据模型，建议明确最小货币单位或精确十进制表示。
- **重复字段如何处理？** 标准库行为未必符合严格协议，应在需要防歧义的边界明确拒绝或采用一致解析规则。

## 参考资料

- [encoding/json](https://pkg.go.dev/encoding/json)
- [json.Decoder.UseNumber](https://pkg.go.dev/encoding/json#Decoder.UseNumber)

[返回目录](../README.md) · [上一题](044-rest.md) · [下一题](046-auth.md)
