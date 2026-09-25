package catalog

import (
	"context"
	"errors"
	"strings"
)

var ErrMissing = errors.New("item missing")
var ErrInvalidID = errors.New("item id is required")

type Item struct{ ID, Name string }

// Repo 由使用数据的业务层声明，业务不依赖协议或存储实现。
type Repo interface {
	Find(context.Context, string) (Item, error)
}

type Usecase struct{ repo Repo }

func NewUsecase(repo Repo) *Usecase { return &Usecase{repo: repo} }

func (u *Usecase) Get(ctx context.Context, id string) (Item, error) {
	if err := ctx.Err(); err != nil {
		return Item{}, err
	}
	if strings.TrimSpace(id) == "" {
		return Item{}, ErrInvalidID
	}
	return u.repo.Find(ctx, id)
}
