package catalog

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"testing"
	"time"

	"github.com/go-kratos/kratos/v2"
	"github.com/go-kratos/kratos/v2/log"
	"go-interview-100/examples/catalog/api"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
)

type repoFunc func(context.Context, string) (Item, error)

func (f repoFunc) Find(ctx context.Context, id string) (Item, error) { return f(ctx, id) }

func TestUsecaseBoundaries(t *testing.T) {
	u := NewUsecase(repoFunc(func(context.Context, string) (Item, error) {
		t.Fatal("invalid or canceled requests must not reach storage")
		return Item{}, nil
	}))
	if _, err := u.Get(context.Background(), " "); !errors.Is(err, ErrInvalidID) {
		t.Fatalf("invalid ID: %v", err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := u.Get(ctx, "book"); !errors.Is(err, context.Canceled) {
		t.Fatalf("canceled: %v", err)
	}
}

func TestRunningTaskCancellation(t *testing.T) {
	entered := make(chan struct{})
	u := NewUsecase(repoFunc(func(ctx context.Context, _ string) (Item, error) {
		close(entered)
		<-ctx.Done()
		return Item{}, ctx.Err()
	}))
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	done := make(chan error, 1)
	go func() { _, err := u.Get(ctx, "book"); done <- err }()
	select {
	case <-entered:
	case <-time.After(2 * time.Second):
		t.Fatal("storage was not entered")
	}
	cancel()
	select {
	case err := <-done:
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("cancel: %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("task did not exit after cancellation")
	}
}

func TestHTTPGRPCAndAppLifecycle(t *testing.T) {
	logger := log.NewStdLogger(io.Discard)
	m := &Metrics{}
	svc := NewService(NewUsecase(NewMemoryRepo([]Item{{ID: "book", Name: "Go Backend 100"}})))
	hs, gs := NewServers(svc, m, logger, "127.0.0.1:0", "127.0.0.1:0")
	hEndpoint, err := hs.Endpoint()
	if err != nil {
		t.Fatal(err)
	}
	gEndpoint, err := gs.Endpoint()
	if err != nil {
		t.Fatal(err)
	}
	app := kratos.New(kratos.Name("catalog-test"), kratos.Server(hs, gs), kratos.StopTimeout(time.Second))
	done := make(chan error, 1)
	go func() { done <- app.Run() }()
	t.Cleanup(func() {
		if err := app.Stop(); err != nil {
			t.Error(err)
		}
		select {
		case err := <-done:
			if err != nil {
				t.Error(err)
			}
		case <-time.After(3 * time.Second):
			t.Error("application did not stop")
		}
	})
	client := &http.Client{Timeout: 2 * time.Second}
	t.Cleanup(client.CloseIdleConnections)
	for _, tc := range []struct {
		id   string
		code int
	}{{"book", 200}, {"missing", 404}} {
		resp, err := client.Get(hEndpoint.String() + "/v1/items/" + tc.id)
		if err != nil {
			t.Fatal(err)
		}
		body, readErr := io.ReadAll(resp.Body)
		closeErr := resp.Body.Close()
		if readErr != nil || closeErr != nil {
			t.Fatalf("body: %v %v", readErr, closeErr)
		}
		if resp.StatusCode != tc.code {
			t.Fatalf("HTTP %s: %d %s", tc.id, resp.StatusCode, body)
		}
		if tc.code == 200 {
			var reply struct{ ID, Name string }
			if err := json.Unmarshal(body, &reply); err != nil {
				t.Fatal(err)
			}
			if reply.ID != "book" || reply.Name != "Go Backend 100" {
				t.Fatalf("reply: %+v", reply)
			}
		}
	}
	conn, err := grpc.NewClient(gEndpoint.Host, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		if err := conn.Close(); err != nil {
			t.Error(err)
		}
	})
	rpc := api.NewCatalogClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	reply, err := rpc.GetItem(ctx, &api.GetItemRequest{Id: "book"})
	if err != nil || reply.GetName() != "Go Backend 100" {
		t.Fatalf("gRPC: %v %v", reply, err)
	}
	_, err = rpc.GetItem(ctx, &api.GetItemRequest{Id: "missing"})
	if status.Code(err) != codes.NotFound {
		t.Fatalf("missing: %v", err)
	}
	_, err = rpc.GetItem(ctx, &api.GetItemRequest{})
	if status.Code(err) != codes.InvalidArgument {
		t.Fatalf("invalid: %v", err)
	}
	if m.Calls.Load() != 5 || m.Failures.Load() != 3 {
		t.Fatalf("metrics: calls=%d failures=%d", m.Calls.Load(), m.Failures.Load())
	}
}
