# 013 string、byte、rune 如何选择？怎样正确截取中文？

> 难度：基础 · 分类：类型与内存

## 简短回答

string 是不可变的字节序列，byte 是 uint8 的别名，rune 是 int32 的别名，常用于表示 Unicode 码点。字符串长度和下标按字节计算，range 按 UTF-8 解码码点；用户看到的一个字符还可能包含多个码点。

## 详细解析

### 三种长度不能混为一谈

网络包长度、文件偏移通常按字节计算；按码点遍历适合部分文本处理；界面截断则可能需要按字素簇处理。例如组合音标和家庭 emoji 可能由多个码点组成，转成 `[]rune` 仍可能切断用户看到的一个字符。

```go
package main

import (
    "fmt"
    "unicode/utf8"
)

func main() {
    s := "Go语言"
    fmt.Println(len(s), utf8.RuneCountInString(s))
    fmt.Println(string([]rune(s)[:3]))
    for i, r := range s { fmt.Printf("%d:%c ", i, r) }
    fmt.Println()
}
```
```output
8 4
Go语
0:G 1:o 2:语 5:言
```

range 返回的下标是码点在原字符串中的字节位置，不能拿它当成“第几个字”。上例按码点取前三项是安全的，因为已知内容与长度；处理外部输入还需先校验长度，避免越界。

### 文本与二进制边界

string 可以包含任意字节，并不天然保证有效 UTF-8。需要拒绝无效输入时使用 `utf8.ValidString`；遍历无效编码会得到替代码点，若静默接受可能改变签名、标识符或审计内容。是否规范化 Unicode 则属于协议约定，应在比较、存储和签名前保持一致。

修改内容时可以构建新的字节切片或使用 Builder。把字符串转为可修改字节序列具有独立可修改的语义，编译器可能优化特定只读场景的分配，但业务不能依赖某次优化来设计所有权。大量拼接先看分配 profile，再考虑预估容量，避免为了节省一次分配引入 unsafe。

## 常见误区 / 面试追问

- **一个中文字符总占三个字节吗？** 不是所有 Unicode 字符都如此，UTF-8 编码长度取决于码点，不能按固定字节宽度切分文本。
- **rune 就是字符吗？** 它能表示码点数值，但用户感知字符可能由多个码点构成。
- **密码长度应该按哪种长度算？** 由产品与安全策略定义，并明确编码和规范化规则；不能让 len 的实现偶然决定规则。

## 参考资料

- [Go 官方：字符串、字节与 rune](https://go.dev/blog/strings)
- [unicode/utf8 文档](https://pkg.go.dev/unicode/utf8)

[返回目录](../README.md) · [上一题](012-slice-retention.md) · [下一题](014-maps.md)
