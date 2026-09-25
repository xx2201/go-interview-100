# 011 数组和切片有什么区别？append 为什么需要接收返回值？

> 难度：基础 · 分类：类型与内存

## 简短回答

数组长度属于类型，赋值会复制数组元素；切片描述底层数组中的一段区域，长度和容量是运行时属性。append 返回更新后的切片，因为长度会变，容量不足时底层数组也可能变；调用者必须接收返回值才能继续使用正确视图。

## 详细解析

### 容量决定能否原地追加

长度表示当前可索引元素数，容量表示从切片起点到底层可用区域末端的范围。不能直接索引长度以外的元素，即使容量更大。下面用完整切片表达式限制容量，让追加一定不能覆盖原数组后面的元素。

```go
package main

import "fmt"

func main() {
    original := []int{1, 2, 3}
    shared := original[:1]
    shared = append(shared, 9)
    isolatedGrowth := original[:1:1]
    isolatedGrowth = append(isolatedGrowth, 8)
    fmt.Println(original, shared, isolatedGrowth)
}
```
```output
[1 9 3] [1 9] [1 8]
```

shared 的追加复用了原数组，所以第二个元素变成 9。isolatedGrowth 的容量被限制为 1，追加需要新数组，因此不会把原数组第二个位置改成 8。但追加之前的 `isolatedGrowth[0]` 仍和原数组共享，限制容量不等于复制。

### 为什么不要背扩容倍率

语言保证 append 的结果能容纳新元素，不承诺容量始终翻倍。具体扩容策略属于运行时实现，还受元素大小和分配器粒度影响。本仓库 Go 1.26.5 源码包含 growslice 与 nextslicecap，阅读这些函数可以解释该版本行为，但业务不能据此推断未来版本的共享关系。

如果已知最终长度，可用 make 预分配，减少多次增长和复制；如果输入长度来自不可信请求，应先校验上限，避免一次预分配就耗尽内存。预分配是性能选择，不应改变 API 的正确性。

数组适合固定大小且长度有语义的值，例如摘要；切片适合变长序列。选择数组指针规避复制时，要额外考虑共享修改。二者不存在放之四海皆准的性能排名。

## 常见误区 / 面试追问

- **append 后旧切片会失效吗？** 不会，它仍描述原来的有效区域；新旧切片是否共享取决于是否重新分配。
- **copy 会自动扩容目标吗？** 不会，它最多复制双方长度的较小值，返回实际复制数量。
- **清空长度就释放数组吗？** 不一定，仍持有底层数组引用，参见 [012](012-slice-retention.md)。

## 参考资料

- [Go 规范：切片表达式](https://go.dev/ref/spec#Slice_expressions)
- [Go 1.26.5 切片实现](https://github.com/golang/go/blob/go1.26.5/src/runtime/slice.go)

[返回目录](../README.md) · [下一题](012-slice-retention.md)
