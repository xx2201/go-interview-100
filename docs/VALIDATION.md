# 验收记录

验收日期：2026-09-25。首次验收范围为本地 Git 仓库。

后续按用户指定地址发布到 [xx2201/go-interview-100](https://github.com/xx2201/go-interview-100)，`main` 分支保留全部课程提交。首次推送后已用 `git ls-remote` 确认远程与本地提交 `3538d9a` 一致。与参考项目的写法核查及差距见 [行文思路核查](STYLE_REVIEW.md)。

## 课程与提交验收

- `python scripts/course.py check --execute`：通过。题号连续 001–100，共 100 篇完整正文；检查四段式结构、目录标题、占位内容和站内文件链接；实际运行 38 个 Go 示例并逐一比对预期输出。
- 同一检查核对 Git 历史：每题恰有一个 `docs(course-NNN)` 首次提交，且该提交只包含对应课程文件。目录、示例工程、进度和验收另行提交。
- `python scripts/course.py check 021 022 023 024 025 026 027 028 029 030 --race`：10 篇并发课程的 9 个 Go 示例通过竞态检测及输出比对。
- `python scripts/check_references.py`：138 条去除片段后的唯一 HTTPS 课程参考链接全部返回 HTTP 200。已修正 OWASP JWT 和 Vitess 文档迁移后的地址；链接可访问不代表内容永远不变，也不验证页面锚点。
- `git diff --check`：通过。

## 已执行的服务验证

- Go 1.26.5，Windows amd64；课程检查使用 Python 3.13.5。
- `go mod verify`：全部依赖校验通过。
- `go test ./... -count=1`：通过。
- `go test -race ./examples/catalog/... -count=1`：通过。
- `go vet ./...`：通过。
- `python scripts/generate_proto.py`：按声明版本完成协议生成；`git diff --exit-code -- examples/catalog/api` 确认生成文件无差异。

## 验证边界

双协议服务使用真实本地 TCP、内存只读仓储，验证 HTTP/gRPC 成功与错误映射、参数边界、预取消与运行中取消、指标计数和应用停止。未连接 PostgreSQL、Redis、Kafka 或注册中心；SQL、Lua、Dockerfile 与架构时序是有明确前提的教学方案，没有宣称已经在这些外部环境执行。

未运行容器镜像构建、集群压测、长期 fuzz、govulncheck 或生产故障注入。普通运行不需要协议生成工具，生成代码已提交。
