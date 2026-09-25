# 041 一次 HTTP 请求在 Go 服务中经历哪些阶段？

> 难度：基础 · 分类：后端接口

## 简短回答

服务接受连接、解析请求、匹配路由并调用 handler，handler 完成校验、业务调用和响应编码。请求处理可以并发发生，共享依赖要保证并发安全；handler 返回后不能继续使用 ResponseWriter 写响应。

## 详细解析

### 路由到响应的最短完整链路

下面使用标准库路由和 httptest 验证一次请求，不启动长期后台进程。方法和路径参数写法要求 Go 1.22 及以上，本课程基线满足要求。

```go
package main

import (
    "fmt"
    "net/http"
    "net/http/httptest"
)

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /orders/{id}", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "text/plain; charset=utf-8")
        fmt.Fprint(w, r.PathValue("id"))
    })
    recorder := httptest.NewRecorder()
    mux.ServeHTTP(recorder, httptest.NewRequest("GET", "/orders/A1", nil))
    fmt.Println(recorder.Code, recorder.Body.String())
}
```
```output
200 A1
```

这个验证覆盖路由、handler 和响应，不覆盖真实 TCP、TLS 或代理行为。不同层次需要不同证据，不能把 handler 测试通过写成真实网络部署已经验证。

### 响应提交是重要边界

第一次 Write 通常会隐式提交成功状态；如果之后才发现业务错误，不能随意改写为错误状态。因此应在提交前完成必要校验与可能失败的响应准备。对于流式输出，必须接受部分响应已发送的事实，并通过协议定义中途失败如何表达。

请求体的大小、读取耗时和编码格式都要在边界限制，不能让不可信输入无限占用内存。业务函数应使用请求 context，使客户端离开或期限到达后能停止无效工作。

共享 map、缓存和业务服务不是每个请求自动独享。即使路由注册阶段没有并发，运行时 handler 会同时调用这些对象，需要明确同步和只读发布规则。连接复用、HTTP/2 多路复用等也让“一个连接等于一个请求 goroutine”的简单模型不可靠。

## 常见误区 / 面试追问

- **handler 里再开 goroutine 就更快吗？** 只在独立工作确实可并发时考虑，并且返回前管理其生命周期。
- **ResponseWriter 可以长期保存吗？** 不可以在 handler 返回后继续使用，后台任务结果应通过其他持久或异步通道提供。
- **如何避免到处重复协议处理？** 用中间件处理共性边界，把业务规则留在业务层，参见 [043](043-middleware.md)。

## 参考资料

- [net/http.Handler](https://pkg.go.dev/net/http#Handler)
- [net/http.ServeMux](https://pkg.go.dev/net/http#ServeMux)

[返回目录](../README.md) · [下一题](042-http-timeouts.md)
