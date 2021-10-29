# 工具介绍<a name="ZH-CN_TOPIC_0000001204082883"></a>

## 适用场景<a name="section195211910162419"></a>

在训练或推理作业中遇到拓扑排序判定有环的报错，此工具可以辅助检测路径连接成环的节点集合。

## 环境准备<a name="section070214015252"></a>

使用infershape故障诊断工具前，请确保环境已安装以下模块：

1.  已安装python软件，推荐使用python3版本。

    ubuntu系统下可使用apt-get install python3 命令安装。

2.  已安装onnx的python库。

    已安装好python的前提下，可使用pip3 install onnx命令安装。

## 工具获取途径<a name="section1265610537259"></a>

成环路径查找工具获取路径：

https://github.com/Ascend/tools/tree/master/cycle_search

# 工具使用<a name="ZH-CN_TOPIC_0000001158843020"></a>

**命令行格式：**  python3 ./cycle\_search.py travel --input=ge_onnx_xxxx.pbtxt --node=node_name

**参数说明：**

-   input:  CANN框架执行训练或atc模型转换时生成的dump图数据，可以直接选取报错时生成的最后一张图，名称里带“black\_box”关键字的pbtxt格式dump图传入。**必选 **。

    > **说明：**
    >-   设置环境变量export DUMP\_GE\_GRAPH=2后执行训练或atc模型转换任务，会在执行文件夹下生成dump图数据。

-   node: 图遍历的起始节点。工具将会从开始节点从下向上不断遍历其输入已完成整张图的遍历，若不传此参数，默认将会在图中查找第一个NetOutput类型的节点名称作为起始节点 。**可选。**


### 屏显结果分析<a name="section459963816435"></a>

脚本执行过程中，会有不同的日志输出，主要输出的日志行内容含义如下：

1.  \[FINAL\] found cycle for node : xxxx

    此日志打印表示已经在遍历找到会成环的节点路径，整条路径上所有其他节点将会紧接着逐条打印出来，格式为

    road node_name : xxxxx

    road node_name : xxxxx

2.  \[FINAL\] not found cycle nodes

    此日志表示遍历了所有图未找到成环的节点路径，若确实出现成环问题，可以检测下node参数传递是否正确，是否以最底层节点作为输入传入

