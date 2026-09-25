package catalog

import (
	"context"
	"errors"

	kerrors "github.com/go-kratos/kratos/v2/errors"
	"go-interview-100/examples/catalog/api"
)

type Service struct {
	api.UnimplementedCatalogServer
	usecase *Usecase
}

func NewService(usecase *Usecase) *Service { return &Service{usecase: usecase} }

func (s *Service) GetItem(ctx context.Context, req *api.GetItemRequest) (*api.GetItemReply, error) {
	item, err := s.usecase.Get(ctx, req.GetId())
	switch {
	case errors.Is(err, ErrInvalidID):
		return nil, kerrors.BadRequest("INVALID_ID", "item id is required")
	case errors.Is(err, ErrMissing):
		return nil, kerrors.NotFound("ITEM_NOT_FOUND", "item not found")
	case err != nil:
		return nil, err
	default:
		return &api.GetItemReply{Id: item.ID, Name: item.Name}, nil
	}
}
