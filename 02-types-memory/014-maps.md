# 014 map 的零值、遍历和并发使用有哪些边界？

> 难度：基础 · 分类：类型与内存

## 简短回答

map 提供键到值的映射，键必须支持比较。nil map 可读、可查询长度和删除，但写入会 panic；遍历顺序没有保证。多个 goroutine 共享 map 时，只要存在未同步的冲突访问就要设计同步，运行时偶尔报错不是并发安全机制。

## 详细解析

### 缺失与零值需要区分

订单状态 map 中，数值零既可能是合法状态，也可能表示键不存在。使用两返回值查询才能区分。如果要稳定输出、生成签名或编写测试，应显式排序键，不能依赖某次运行恰好稳定的遍历顺序。

```go
package main

import (
    "fmt"
    "slices"
)

func main() {
    m := map[string]int{"b": 0, "a": 2}
    v, ok := m["b"]
    fmt.Println(v, ok)
    v, ok = m["missing"]
    fmt.Println(v, ok)
    keys := make([]string, 0, len(m))
    for k := range m { keys = append(keys, k) }
    slices.Sort(keys)
    fmt.Println(keys)
}
```
```output
0 true
0 false
[a b]
```

### 并发安全要覆盖整个操作

给每次查询和写入单独加锁，仍可能没有保护「读余额—计算—写余额」这个复合操作。锁应覆盖需要保持原子的业务步骤，或使用数据库等提供的条件更新机制。只有完成安全发布且不再修改的 map 才适合无锁并发读取。

map 的元素不可直接取地址。对结构体值通常需要取出、修改、写回；改为保存指针虽然方便修改，但又引入共享对象的同步责任。`sync.Map` 适合其文档描述的使用形态，不是对任意业务 map 的性能升级。

Go 1.26.5 的实现位于 internal/runtime/maps，采用基于 Swiss Table 的设计。旧面试材料中的桶布局和迁移细节不能直接当作当前实现，更不能当作语言规则。理解哈希冲突、负载与查找成本，比背固定桶常数更有迁移价值。

## 常见误区 / 面试追问

- **只写不同键可以不加锁吗？** 普通 map 的内部结构仍被共同修改，不可以据此判断安全。
- **没有 fatal 就没有竞态吗？** 没有报错不能证明安全，应审查同步关系并运行 race detector。
- **删除键后内存马上缩小吗？** 语言不保证底层存储立即收缩，应根据实际实现和 profile 判断。

## 参考资料

- [Go 规范：map](https://go.dev/ref/spec#Map_types)
- [Go 1.26.5 map 实现](https://github.com/golang/go/blob/go1.26.5/src/internal/runtime/maps/map.go)
- [sync.Map 适用范围](https://pkg.go.dev/sync#Map)

[返回目录](../README.md) · [上一题](013-strings.md) · [下一题](015-typed-nil.md)
