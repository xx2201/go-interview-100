# 043 中间件的执行顺序如何影响日志、鉴权和恢复？

> 难度：基础 · 分类：后端接口

## 简短回答

中间件通常把一个 handler 包成另一个 handler，形成进入时由外到内、返回时由内到外的调用链。顺序决定哪些请求被记录、哪些 panic 能被恢复、拒绝请求是否仍计入指标，必须按实际包裹关系验证。

## 详细解析

### 用可执行输出确认顺序

```go
package main

import (
    "fmt"
    "net/http"
    "net/http/httptest"
)

func wrap(name string, next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Println(name, "enter")
        defer fmt.Println(name, "exit")
        next.ServeHTTP(w, r)
    })
}

func main() {
    endpoint := http.HandlerFunc(func(http.ResponseWriter, *http.Request) {
        fmt.Println("handler")
    })
    h := wrap("outer", wrap("inner", endpoint))
    h.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest("GET", "/", nil))
}
```
```output
outer enter
inner enter
handler
inner exit
outer exit
```

日志与指标放在鉴权外侧，可以记录被拒绝的请求；鉴权必须在执行业务副作用之前。恢复边界能捕获它包裹的调用中、同一 goroutine 的 panic，但捕获不到另外启动的 goroutine，也不能修复已经提交的业务状态。

### 指标记录也有协议细节

想记录真实状态码，需要包装 ResponseWriter，正确处理隐式 200、重复 WriteHeader 与已写入字节数。包装还可能影响 Flusher、Hijacker 等可选接口；流式接口因此需要核对能力传递，不能只写一个嵌入字段就认为所有行为保持不变。

恢复中间件若在响应已经开始后才遇到 panic，无法可靠地把已发送成功响应改成完整错误 JSON。应记录失败并按协议终止或发送流内错误，而不是把错误文本直接拼到正常 JSON 后面。

中间件适合追踪、日志、认证等横切能力，不适合隐藏订单状态机和库存扣减。否则业务规则依赖注册顺序，单元测试也很难表达完整前提。

## 常见误区 / 面试追问

- **恢复放最外层一定最佳吗？** 要明确它是否需要覆盖其他中间件的 panic，以及日志如何记录恢复后的结果，再验证具体链路。
- **链式配置的书写顺序就是执行顺序吗？** 取决于框架如何折叠调用链，应读源码或用小测试核对。
- **鉴权失败直接 return 就够了吗？** 还要提交明确的错误状态与响应，并确认没有继续调用 next。

## 参考资料

- [http.Handler](https://pkg.go.dev/net/http#Handler)
- [http.ResponseController](https://pkg.go.dev/net/http#ResponseController)

[返回目录](../README.md) · [上一题](042-http-timeouts.md) · [下一题](044-rest.md)
