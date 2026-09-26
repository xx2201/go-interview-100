# 验证记录

验证日期：2026-09-26。范围为 100 篇课程、图解、文章示例及 Kratos 示例工程。以下记录实际执行的检查及其适用范围，便于读者复现。

## 课程、图解与提交

| 检查 | 实际结果 |
| --- | --- |
| `python scripts/course.py check --execute` | 100 题通过结构、目录、站内文件链接、占位内容和图解检查；47 个 Go 程序实际运行并逐一比对预期输出 |
| 同一脚本的 Git 历史检查 | 每题各有一个 `docs(course-NNN)` 和 `docs(deepen-NNN)` 提交，共 200 个独立课程提交；每次只包含对应课程文件 |
| `python scripts/render_diagrams.py` | Mermaid CLI 11.12.0 实际渲染 100 张课程图，全部成功；另对代表性流程图、时序图、状态图做目视检查 |
| `python scripts/course.py check 021 022 023 024 025 026 027 028 029 030 --race` | 并发章节 11 个正常 Go 示例通过竞态检测及输出比对 |
| `python scripts/check_bad_examples.py 030` | 1 个明确标注的错误程序检出预期竞态；检查非零退出及 `WARNING: DATA RACE`，不依赖偶然的结果数量 |
| `python scripts/check_references.py` | 142 条去除片段后的唯一 HTTPS 课程参考链接全部返回 HTTP 200；不验证页面锚点或未来可用性 |

47 个程序包含 098 的错误起点复现及修复后程序：前者用本地 `httptest` 展示缺陷输出，不表示错误实现通过了正确性验收。030 的 `go-bad-race` 反例独立检查，不计入这 47 个程序。没有用静态提取或代码块存在代替实际运行。

图解源文件直接保存在各篇 Markdown 中；渲染产物位于被忽略的 `.work/diagrams/all/`。首次渲染需要执行 `npm install --prefix .work/diagram-tools --save-exact @mermaid-js/mermaid-cli@11.12.0`，然后运行上表的渲染脚本。

## 已执行的工程验证

环境为 Go 1.26.5 / Windows amd64、Python 3.13.5。锁定依赖见 [go.mod](../go.mod)。

- `go mod verify`：全部依赖校验通过。
- `go test ./... -count=1`：通过。
- `go test -race ./examples/catalog/... -count=1`：通过。
- `go vet ./...`：通过。
- 仅在构建进程设置 `GOOS=linux`、`GOARCH=amd64`、`CGO_ENABLED=0`，执行 `go build -trimpath -o .work/catalog-linux-amd64 ./examples/catalog/cmd/server`：成功生成 Linux 二进制；未在 Linux 上运行。
- 协议生成校验记录于提交 `3538d9a`：执行 `python scripts/generate_proto.py`，并以 `git diff --exit-code -- examples/catalog/api` 确认生成文件无差异；此后协议和生成代码未变，本次未重复执行。

双协议服务测试使用真实本地 TCP 和内存只读仓储，覆盖 HTTP/gRPC 成功与错误映射、参数边界、预取消与运行中取消、指标计数和应用停止。指标计数断言不等于抓取 `/metrics` 端点的测试；也没有覆盖 panic 注入、带在途请求退出或任意底层错误的脱敏。

## 性能章节的实际实验

本轮执行了 `go test ./examples/bench -run "^$" -bench . -benchmem -benchtime=200ms -count=3`。在 Ryzen 7 8745H、上述 Windows/Go 环境中，`Itoa` 为 9.597–10.54 ns/op、4 B/op、0 allocs/op；`Sprint` 为 39.54–41.51 ns/op、11 B/op、1 allocs/op。短基准只说明本机这个输入和实现，不是生产容量结论。`allocs/op` 的整数显示可能将平均不到一次的分配截为 0，不能由此推断没有分配。

另对 `BenchmarkSprint` 采集并用 `pprof -top` 读取 CPU/heap profile；对 `TestHTTPGRPCAndAppLifecycle` 采集 trace，并导出、读取调度延迟 profile。产物在 `.work/`，没有将浏览器交互分析或真实生产故障作为已完成实验。

## 验证边界

未连接 PostgreSQL、Redis、Kafka、注册中心或 Kubernetes；相关 SQL、Lua、协议时序与容量数字是有明确前提的教学推演。Kratos 部分对照锁定版本源码与仓库真实请求链，不能据此推断外部组件已做集成测试。

未运行容器镜像构建、集群压测、长期 fuzz、govulncheck 或生产故障注入。故障题中的模拟时间线与容量估算均按教学场景标注，使用时需要结合实际环境验证。
