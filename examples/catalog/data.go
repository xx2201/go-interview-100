package catalog

import "context"

// MemoryRepo 是示例的只读目录存储；构造时复制输入，发布后不再修改。
type MemoryRepo struct{ items map[string]Item }

func NewMemoryRepo(items []Item) *MemoryRepo {
	values := make(map[string]Item, len(items))
	for _, item := range items {
		values[item.ID] = item
	}
	return &MemoryRepo{items: values}
}

func (r *MemoryRepo) Find(ctx context.Context, id string) (Item, error) {
	if err := ctx.Err(); err != nil {
		return Item{}, err
	}
	item, ok := r.items[id]
	if !ok {
		return Item{}, ErrMissing
	}
	return item, nil
}
