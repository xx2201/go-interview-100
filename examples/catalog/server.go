package catalog

import (
	"context"
	"fmt"
	"net/http"
	"sync/atomic"
	"time"

	"github.com/go-kratos/kratos/v2/log"
	"github.com/go-kratos/kratos/v2/middleware"
	"github.com/go-kratos/kratos/v2/middleware/logging"
	"github.com/go-kratos/kratos/v2/middleware/recovery"
	kg "github.com/go-kratos/kratos/v2/transport/grpc"
	kh "github.com/go-kratos/kratos/v2/transport/http"
	"go-interview-100/examples/catalog/api"
)

type Metrics struct {
	Calls    atomic.Int64
	Failures atomic.Int64
}

func (m *Metrics) observe(next middleware.Handler) middleware.Handler {
	return func(ctx context.Context, req any) (any, error) {
		m.Calls.Add(1)
		reply, err := next(ctx, req)
		if err != nil {
			m.Failures.Add(1)
		}
		return reply, err
	}
}

// 两种协议注册同一个 service；恢复在指标内侧，使恢复后的错误也被计数。
func NewServers(service *Service, metrics *Metrics, logger log.Logger, httpAddr, grpcAddr string) (*kh.Server, *kg.Server) {
	chain := []middleware.Middleware{metrics.observe, logging.Server(logger), recovery.Recovery()}
	hs := kh.NewServer(kh.Address(httpAddr), kh.Timeout(time.Second), kh.Middleware(chain...))
	hs.ReadHeaderTimeout = 2 * time.Second
	hs.ReadTimeout = 5 * time.Second
	hs.WriteTimeout = 5 * time.Second
	hs.IdleTimeout = 30 * time.Second
	gs := kg.NewServer(kg.Address(grpcAddr), kg.Timeout(time.Second), kg.Middleware(chain...))
	api.RegisterCatalogHTTPServer(hs, service)
	api.RegisterCatalogServer(gs, service)
	// 只公开低基数计数，诊断地址使用本地监听；不包含业务 ID。
	hs.HandleFunc("/metrics", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		fmt.Fprintf(w, "# TYPE catalog_requests_total counter\ncatalog_requests_total %d\n# TYPE catalog_failures_total counter\ncatalog_failures_total %d\n", metrics.Calls.Load(), metrics.Failures.Load())
	})
	return hs, gs
}
