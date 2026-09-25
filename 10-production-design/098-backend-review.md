# 098 代码 Review：一个能运行的 HTTP 服务还缺什么？

> 难度：中级 · 分类：生产与系统设计

## 简短回答

Review 应沿输入、业务副作用、响应与资源退出检查，而不只看能否编译。常见缺口包括无界请求体、宽松或不完整解码、零值误用、未传 context、重复副作用、错误泄露和缺少优雅关闭。每项问题都要说明具体触发条件与影响。

## 详细解析

### 先缩小一个可验证边界

假设入口读取 JSON 数量后直接返回接收结果。若只 Decode 一次，可能接受后面还有第二个 JSON 的请求；若不限制 body，会被大请求消耗资源；若不验证数量，缺失字段与负数也可能进入业务。

下面完整程序验证输入边界，接口只确认合法输入，不执行订单持久化，因此不会把缺少幂等与事务的代码冒充下单实现。

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/http/httptest"
    "strings"
)

func validate(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        w.Header().Set("Allow", "POST")
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }
    r.Body = http.MaxBytesReader(w, r.Body, 1024)
    defer r.Body.Close()
    dec := json.NewDecoder(r.Body)
    dec.DisallowUnknownFields()
    var input struct { Quantity int `json:"quantity"` }
    if err := dec.Decode(&input); err != nil {
        http.Error(w, "invalid JSON", http.StatusBadRequest)
        return
    }
    var extra any
    if err := dec.Decode(&extra); err != io.EOF {
        http.Error(w, "single JSON value required", http.StatusBadRequest)
        return
    }
    if input.Quantity < 1 || input.Quantity > 100 {
        http.Error(w, "quantity out of range", http.StatusBadRequest)
        return
    }
    w.WriteHeader(http.StatusNoContent)
}

func main() {
    for _, body := range []string{`{"quantity":2}`, `{}`, `{"quantity":2}{}`} {
        req := httptest.NewRequest("POST", "/validate", strings.NewReader(body))
        rec := httptest.NewRecorder()
        validate(rec, req)
        fmt.Println(rec.Code)
    }
}
```
```output
204
400
400
```

### 这份修复证明了什么

示例核对单一 JSON 值、数量范围和方法，且限制读取体积。它还没有定义 Content-Type 策略或拒绝重复 JSON 键；若协议需要这些严格性，应补充对应解析规则与测试。公开错误使用稳定文本，没有把内部解析详情直接暴露出去。

接入业务后继续审查权限是否针对目标资源、幂等键是否持久、数据库操作是否共享正确事务、取消是否贯穿依赖，以及成功响应是否只在提交后产生。性能方面关注连接复用、结果关闭和共享状态，而不是一上来微调格式化。

服务外壳还要明确读写期限、日志指标和关停流程，可参考 [目录服务](../examples/catalog/README.md)。输入校验通过只证明入口边界，不能代替完整业务与部署验证。

## 常见误区 / 面试追问

- **返回 400 就不需要限制 body 吗？** 解析到失败前可能已消耗大量资源，限制要在读取前建立。
- **错误都包装成成功响应方便前端吗？** 会破坏通用客户端和监控对协议结果的理解。
- **Review 意见如何避免泛泛而谈？** 用具体输入、执行路径和可验证的后果说明问题，并给出最小充分修改。

## 参考资料

- [http.MaxBytesReader](https://pkg.go.dev/net/http#MaxBytesReader)
- [json.Decoder](https://pkg.go.dev/encoding/json#Decoder)

[返回目录](../README.md) · [上一题](097-job-platform.md) · [下一题](099-incident.md)
