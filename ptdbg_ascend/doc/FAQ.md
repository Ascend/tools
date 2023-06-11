## FAQ

### 1. 单机多卡场景dump目录下只生成一个rank目录或pkl文件格式损坏

**故障现象**

dump目录下只生成一个rank目录或dump目录下的pkl文件格式损坏、内容不完整。 

**故障原因**

通常是因为register_hook没有正确配置，带着工具没有获取正确的`rank_id`（从rank参数读取或从模型参数的device_id读取）。

**故障处理**

register_hook需要在set_dump_path之后调用，也需要在每个进程上被调用，建议在搬运模型数据到卡之后调用。识别方法如下：

- 找到训练代码中遍历epoch的for循环或遍历数据集的for循环，把register_hook放到循环开始前即可。
- 找到训练代码中调用DDP或者DistributedDataParallel的代码行，把register_hook放到该代码行所在的代码块之后。
- 若代码中均无以上两种情况，那么尽可能把这行代码往后放，并配置register_hook的rank参数。

### 2. HCCL 报错： error code: EI0006

**故障现象**

使用ptdbg_ascend工具时，报错： error code: EI0006。

**故障原因**

CANN软件版本较低导致不兼容。

**故障处理**

升级新版CANN软件版本。
