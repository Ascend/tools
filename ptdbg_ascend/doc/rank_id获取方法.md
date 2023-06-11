# rank_id获取方法

## **通过环境变量获取**

当前进程的rank_id可能保存在环境变量中，比如`LOCAL_RANK`。则可以通过如下示例来检查当前进程的rank_id：

```python
import os
print("Local rank is: ", os.environ.get('LOCAL_RANK'))
```

若打印结果显示该环境变量被配置过，如：

```python
# 以单机8卡为例
Local rank is: 0
Local rank is: 2
Local rank is: 3
Local rank is: 1
Local rank is: 4
Local rank is: 5
Local rank is: 6
Local rank is: 7
```

那么将该环境变量作为rank传参即可自动获取到rank_id，如：

```python
register_hook(model, acc_cmp_dump, rank=os.environ.get('LOCAL_RANK')
```

## **通过命令行参数获取**

若通过命令行参数传入rank_id，比如`--local_rank`。那么可以在代码中找到`args.local_rank` 来作为rank参数值。如：

```bash
register_hook(model, acc_cmp_dump, rank=args.local_rank)
```
