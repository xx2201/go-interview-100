# 056 乐观锁和悲观锁如何防止超卖？

> 难度：中级 · 分类：数据库

## 简短回答

防超卖的核心是让“库存足够”和“扣减库存”在数据库中形成受协调的原子操作。简单扣减优先考虑带条件的 UPDATE；需要多步读取和决策时可用行锁；基于版本号的乐观并发控制则通过条件更新检测冲突。都要检查实际修改结果。

## 详细解析

### 先查后写为什么不可靠

库存为一，两个请求都先读到一，然后分别写入零并创建订单，最终可能生成两笔订单却只扣了一份库存。应用里的 if 判断不保护两个并发请求间的时间窗口。

以下 PostgreSQL 16 示例在一个全新实验表上演示条件扣减。第一次返回零，第二次不返回行；这是依据语句语义的预期，不是本仓库的数据库执行记录。

```sql
CREATE TABLE stock_demo (
    sku text PRIMARY KEY,
    available integer NOT NULL CHECK (available >= 0)
);
INSERT INTO stock_demo VALUES ('book', 1);
UPDATE stock_demo SET available = available - 1
WHERE sku = 'book' AND available >= 1 RETURNING available;
UPDATE stock_demo SET available = available - 1
WHERE sku = 'book' AND available >= 1 RETURNING available;
```

购买数量必须为正并有上限，否则负数扣减会变成增加库存。订单写入与扣减需要同一事务，并以业务请求键防止重试再次扣减。库存不为负只保护一项不变量，不等于订单、支付和库存已经全部一致。

### 锁策略的取舍

悲观方案使用 SELECT FOR UPDATE 锁定目标行，在同一事务内检查并更新，适合确实需要多步决策的场景。代价是等待与长事务竞争，应固定多行锁定顺序并尽快提交。

乐观方案把读取到的 version 放进 UPDATE 条件，成功后 version 加一。影响行数为零说明状态已变化，应重新读取或返回冲突，不可忽略。竞争极高时频繁重试会放大压力，可能不如顺序化或库存分片。

SQL UPDATE 本身也会涉及数据库锁，因此“乐观锁完全无锁”是不准确的。这里的乐观指应用冲突检测策略，不是底层完全不协调写入。

## 常见误区 / 面试追问

- **加 Go Mutex 就能防超卖吗？** 只保护当前进程，多个实例仍会并发写同一数据库。
- **Redis 扣减成功就能立刻发货吗？** 需要定义库存权威来源和可靠落单协议，不能忽略缓存故障与持久化。
- **失败就无限重试吗？** 应限次、退避并受整体期限约束，业务冲突也可能应直接返回。

## 参考资料

- [PostgreSQL 16：UPDATE](https://www.postgresql.org/docs/16/sql-update.html)
- [PostgreSQL 16：行锁](https://www.postgresql.org/docs/16/explicit-locking.html#LOCKING-ROWS)

[返回目录](../README.md) · [下一题](057-migrations.md)
