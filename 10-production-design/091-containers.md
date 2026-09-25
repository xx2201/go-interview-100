# 091 Go 服务如何构建为可重复部署的容器？

> 难度：基础 · 分类：生产与系统设计

## 简短回答

固定源码、模块依赖、工具链和镜像输入，在构建阶段产出目标平台二进制，运行镜像只保留必要文件。多阶段构建减少运行环境体积，但是否能使用极简镜像取决于 cgo、证书、时区与动态库需求；小镜像不自动等于可运行。

## 详细解析

### 一份完整的构建配方

以下 Dockerfile 在仓库根目录作为构建上下文，面向不依赖 cgo 的目录服务。示例标签固定版本，若要固定镜像内容还应记录经过核验的 digest。本文没有把容器构建写成已经执行的验证结果。

```dockerfile
FROM golang:1.26.5 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -o /catalog ./examples/catalog/cmd/server

FROM scratch
COPY --from=build /catalog /catalog
USER 65532:65532
EXPOSE 8000 9000
ENTRYPOINT ["/catalog"]
CMD ["-http", "0.0.0.0:8000", "-grpc", "0.0.0.0:9000"]
```

当前服务只使用本地只读内存数据，不发起 HTTPS，因此此配方未复制证书包。未来增加外部 TLS 客户端、读取时区或动态库时，需要显式补齐运行依赖，不能继续盲用 scratch。容器端口发布还应按部署环境控制访问范围。

### 可重复不只是固定 go.mod

生成代码、构建参数、目标架构、基础镜像和构建时注入的版本信息都会影响产物。不要在构建阶段使用不受控 latest 或自动升级依赖。模块缓存只是加速器，清空缓存后也应能从声明的输入构建。

运行用户不应依赖 root，工作目录和可写路径需要明确。只读文件系统能暴露未声明的写入需求，但临时文件、证书和日志输出应按真实行为验证。应用日志输出到标准流，交给运行平台收集。

部署时还需设 CPU、内存与终止宽限期，并验证信号能到达应用。exec 形式 ENTRYPOINT 避免额外 shell 吞掉信号，但应用自身仍要正确收尾。镜像内能启动不代表 readiness 与依赖已经准备好。

## 常见误区 / 面试追问

- **Go 二进制一定完全静态吗？** 不一定，取决于 cgo、链接方式和依赖，必须检查目标构建。
- **镜像越小越安全吗？** 体积小降低部分暴露面，但不代替漏洞、权限与配置治理。
- **本机 Windows 编译成功能证明 Linux 容器成功吗？** 不能，需要目标平台构建与运行验证。

## 参考资料

- [Docker 多阶段构建](https://docs.docker.com/build/building/multi-stage/)
- [Go 构建命令](https://pkg.go.dev/cmd/go#hdr-Compile_packages_and_dependencies)

[返回目录](../README.md) · [下一题](092-testing.md)
