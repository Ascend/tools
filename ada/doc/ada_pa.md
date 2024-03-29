# 解析profiling文件

## 打开GE的profiling功能

要打开GE的profiling功能，需要做两件事情

1、环境变量，通过设置如下环境变量，打开Dump到命令行的能力：

```bash
export GE_PROFILING_TO_STD_OUT=1
```

2、打开通用profiling

完成环境变量配置后，使用**资料中profiling的打开方法，来打开profiling即可**，下面是各种场景的举例：

**在PyTorch训练场景**，打开通用profiling的方法为，在脚本中添加如下代码

```python
with torch.npu.profile('./'):
    # 在此scope中的代码会统计profiling，退出此scope时，GE会将profiling数据打印到标准输出中
```

**在TensorFlow训练场景**，在option中加如下配置：

```python
custom_op.parameter_map["profiling_mode"].b = True
custom_op.parameter_map["profiling_options"].s = tf.compat.as_bytes('{"output":"../profiling","storage_limit": "200MB","training_trace":"on","l2":"on","hccl":"on","task_trace":"on","aicpu":"on","fp_point":"","bp_point":"","aic_metrics":"PipeUtilization","msproftx":"on"}')
```

**如果你使用了[msame](https://github.com/Ascend/tools/tree/master/msame) 推理工具**，可以通过指定`--profiler true`打开profiling：

```bash
./msame.x86 ...很多选项... --profiler true
```

TODO: 添加在ACL推理场景下的使用说明

***注意！！！ 一旦设置了第1步中的环境变量，profiling的正常功能会被屏蔽，仅会生效本文档中描述的profiling功能！！
若想使用昇腾官方的profiling功能，请取消第1步中设置的环境变量。***

GE profiling结果会通过标准输出打印：

```bash
...其他输出
Profiler version: 1.0, dump start, records num: 18700
1637680366909118480 122080 [GatherV2] [OpExecute] Start
1637680366909119490 122080 [GatherV2] [ConstPrepare] Start
1637680366909131850 122080 [GatherV2] [ConstPrepare] End
1637680366909132410 122080 UNKNOWN(-1) [UpdateShape] Start
1637680366909134960 122080 UNKNOWN(-1) [UpdateShape] End
1637680366909135210 122080 UNKNOWN(-1) [Tiling] Start
1637680366909155530 122080 UNKNOWN(-1) [Tiling] End
...更多profiling打印
Profiling dump end
...其他输出
```

为了不影响执行效率，GE profiling信息不会实时地打印到标准输出。
profiling开启的过程中，GE会一直在内存中缓存profiling数据。 在**profiling被关闭时**，数据被打印到标准输出。
以PyTorch脚本场景为例，在脚本中每调用一次`with torch.npu.profile('./')`语句，在`with`结束后，都会在标准输出看到一段类似的打印。

## 解析profiling

### profiling解析能力

保存好上一步打印的标准输出内容后，可以使用 `ada-pa` 命令解析。`ada-pa`内置多种解析器，有通用解析器，可以对profiling数据做一般的解析和呈现；
也有适用于PyTorch场景的增强解析器，这一类解析器可以根据PyTorch场景的执行特点，做数据分析并优化呈现。

通过如下命令做`通用解析`：

```shell
$ ada-pa /path/to/out_file.txt
Dump to <result-type> file /path/to/out_file_<result-type>_i.json
Dump to ...
```

通过如下命令**同时**做`通用解析`和`PyTorch场景的单算子解析`（是的，通用解析总是有用的，因此即使选定了特定场景，通用解析也会打开）：

```shell
$ ada-pa /path/to/out_file.txt --reporter=single-op
Dump to <result-type> file /path/to/out_file_<result-type>_i.json
Dump to ...
```

完成解析后，结果文件会默认写到与源文件同目录下。也可以通过`-o`选项指定结果文件的目录。
更多 `ada-pa` 的功能请通过 `ada-pa -h` 查看，此处不过多赘述：

```bash
$ ada-pa -h
usage: ada-pa [-h] [-o OUTPUT] [--reporter REPORTER] input_file

Ascend Debugging Assistant - Profiling Analysis

positional arguments:
  input_file            input file path

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file path
  --reporter REPORTER   Specify one or more reporters, current available reporters: single-op. By default basic reporters will be used.
```

解析结果文件的命名规则为：`file_name_<result-type>_<index>.<ext>`，其中：

* result-type：结果类型，当前支持tracing与summary两种，后续可能添加新的结果类型
* index：第几次dump的结果，对应脚本中的第几次`with`语句，从0开始
* ext：后缀名，不同类型的结果可能后缀不同，不做赘述

### 通用解析结果

通用解析会输出三类文件：trace、statistics、summary

#### trace文件

trace文件名为`file_name_trace_<index>.json`，解析出的tracing文件可以在`chrome://tracing`中打开，效果图如下所示：

![](res/ada_pa_tracing.png)

#### summary文件

trace文件名为`file_name_summary_<index>.csv`，summary文件可以使用excel打开，效果如下所示：

![](res/ada_pa_summary.png)

表头中几个字段的含义为：

* event: 事件类型，不解释
* count：该事件发生了多少次
* avg(us)：该事件的平均耗时，用us表达
* total(us)：该事件的总耗时，用us表达
* w-percent：该事件耗时加权平均后的占比，计算公式为该事件的total耗时除以`OpExecute`或`Execute`事件的total耗时

#### statistics文件

op statistic文件可以使用excel打开，效果如下所示：

![](res/ada_pa_op_stat.png)

表头中几个字段的含义为：

* name: node name
* event: 事件类型
* duration(us): 耗时，用us表达

### 单算子场景解析结果

使能单算子场景后，会按照单算子的下发类型，分类统计每一种下发类型的summary信息，并将其汇总为`file_name_single_op_summary_<index>.csv`。
在这个文件中，会统计本次执行过程中，每一类下发的个数及时间占比，如下图所示：

![](res/ada_pa_single_op_summary.png)

单算子的下发类型中，当前支持解析如下几类：

* aicore_single_op: AICORE单算子类型，即只有一次KernelLaunch
* aicore_atomic_clean: 需要atomic clean的AICORE单算子
* aicpu_single_op: AICPU单算子下发
* aicore_type3: AICORE的第三类算子
* aicpu_type3: AICPU的第三类算子
* subgraph: 子图下发，所谓子图下发，是指该单算子实际下发流程是执行一张子图，子图内包含多个结点。例如前后插入transdata等。
* others: 未识别的分类

上述分类，每一类都会产生一个summary文件，文件名的规则为：`file_name_<分类>_summary_<index>.csv`，
summary文件格式与字段含义与[summary文件](#summary文件)一致。