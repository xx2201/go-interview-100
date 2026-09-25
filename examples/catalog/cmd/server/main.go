package main

import (
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/go-kratos/kratos/v2"
	"github.com/go-kratos/kratos/v2/log"
	"go-interview-100/examples/catalog"
)

func run() error {
	httpAddr := flag.String("http", "127.0.0.1:8000", "HTTP listen address")
	grpcAddr := flag.String("grpc", "127.0.0.1:9000", "gRPC listen address")
	flag.Parse()
	logger := log.NewStdLogger(os.Stdout)
	repo := catalog.NewMemoryRepo([]catalog.Item{{ID: "book", Name: "Go Backend 100"}})
	service := catalog.NewService(catalog.NewUsecase(repo))
	hs, gs := catalog.NewServers(service, &catalog.Metrics{}, logger, *httpAddr, *grpcAddr)
	app := kratos.New(kratos.Name("interview.catalog"), kratos.Version("1.0.0"),
		kratos.Logger(logger), kratos.Server(hs, gs), kratos.StopTimeout(5*time.Second))
	return app.Run()
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
