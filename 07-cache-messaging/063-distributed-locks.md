# 063 Redis 分布式锁为何需要所有权与 fencing token？

> 难度：中级 · 分类：缓存与消息

## 简短回答

锁需要唯一持有者标识和有限租期，释放时原子确认所有权，避免删除别人的锁。但租约过期不会强行停止旧持有者；严格保护外部资源还需要由资源端拒绝过期执行者，例如校验单调递增的 fencing token。

## 详细解析

### 所有权只能防止误删

单 Redis 实例的常见获取方式是 SET key token NX PX ttl，其中 token 为每次获取的唯一随机值。释放必须原子比较值再删除，不能 GET 后另发 DEL，因为两个命令之间可能已经换了持有者。

下面 Lua 表达比较后删除协议，KEYS[1] 是锁键，ARGV[1] 是调用者令牌。它是 Redis 脚本示例，本仓库未连接 Redis 执行。

```lua
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
end
return 0
```

### 过期后的旧执行者才是难点

```text
A 获锁 → 长时间暂停 → 租约到期
B 获锁 → 写入新状态
A 恢复 → 仍以为自己有锁 → 写入旧状态
```

释放脚本不会阻止最后一步。即使 A 定期续租，也可能因暂停或网络故障失去租约却未及时知道。取消本地任务同样不能撤销已发出的远端写请求。

fencing token 是每次成功取得所有权时分配的递增序号。资源服务保存已接受的最高序号，只接受满足协议的新请求，从而拒绝旧持有者。关键在于序号生成与资源校验本身要可靠、持久且原子；一个会在故障恢复后倒退的计数器无法提供这项保证。

如果数据库已经能用条件 UPDATE、唯一约束或事务表达业务规则，优先利用权威存储的能力。分布式锁更适合协作和减少重复工作，不能自动使跨多个系统的副作用形成原子事务。还应分析 Redis 复制与故障切换下锁状态丢失的影响。

## 常见误区 / 面试追问

- **随机 token 和 fencing token 是一回事吗？** 前者识别持有者，后者表达可比较的世代顺序，作用不同。
- **租期设得足够长就安全吗？** 无法覆盖任意暂停，且会延迟故障后恢复。
- **续租失败怎么办？** 停止新的工作并按协议处理已有请求，核心资源仍需防止旧写入。

## 参考资料

- [Redis 官方分布式锁说明](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
- [Redis SET 命令](https://redis.io/docs/latest/commands/set/)
- [etcd 并发与锁 API](https://etcd.io/docs/v3.5/dev-guide/api_concurrency_reference_v3/)

[返回目录](../README.md) · [上一题](062-cache-failures.md) · [下一题](064-cache-levels.md)
