# 一键收集故障信息<a name="ZH-CN_TOPIC_0000001103715860"></a>

## 工具介绍<a name="section182635125168"></a>

为提高系统故障维测效率，提供一键式故障信息收集脚本工具：一次性收集进程故障现场信息、为故障定位效率提升提供有效输入。工具可以收集以下信息：

-   Host侧CANN软件桟日志
-   Host侧驱动日志（需root权限）
-   Host coredump文件
-   黑匣子、Device侧日志、Stackcore文件（需root权限）
-   训练打屏日志
-   包安装日志（需包安装账号与用例执行账号一致才可收集）
-   GE dump图
-   TFAdatper dump图
-   算子编译.o文件
-   机器环境信息，包括执行用例前机器的内存状态、硬盘状态、进程状态，机器的操作系统信息，内核版本信息。

本工具会使用环境变量NPU_COLLECT_PATH来控制dump图以及算子.o的生成路径

## 使用约束<a name="section1872274617296"></a>

1.  不支持原有执行脚本内部直接后台执行的方式。

    如：原有用例通过命令行执行 sh cmd.sh来拉起用例，而cmd.sh的实现里执行python3 test.py &，用后台的方式执行，此种用例由于无法感知结束点，暂不支持使用。

2.  相同用户、相同时间段内，同机器同时作业时，收集到的数据会有交叉。
3.  非root用户，获取到的数据范围会受限，具体限制参见[工具介绍](#section182635125168)中权限要求。
4.  日志收集能力仅服务于 C76之后的版本；dump与算子.o的收集仅支持4.xx日之后发布的社区版本。
5.  core文件的收集会对硬盘空间有较大要求，建议非coredump场景关闭core文件的收集。关闭方式如下：

    在npucollect.sh脚本开头的modules数组里，删除core的模块名，即不包括core。

    示例：modules=\(ge log ops environment\)


## 工具使用<a name="section171791224131610"></a>

请从码云tools仓（[https://github.com/Ascend/tools/tree/master/npucollector](https://github.com/Ascend/tools/tree/master/npucollector)）获取脚本工具，然后将脚本工具存放到发生故障的环境上，例如存放到/home/npucollector目录下，接着在**原用例执行目录下**执行命令，命令行格式如下：

**bash /home/npucollector/npucollect.sh** _"sh app\_run.sh" /home/npucollector/target.tar.gz_

>**说明：** 
>命令行中，第一个参数字段为发生故障时执行的任务，填写完整的命令；第二个参数字段为收集的目标压缩文件名称，目前必须以.tar.gz结尾。

执行完命令后，生成本次收集的故障维测所需信息，\*_.tar.gz_文件解压后内容如下：

```
├── extra-info         保存非日志数据
│   ├── bbox          保存device侧的黑匣子信息，分device存储
│   │   ├── device-0
│   │   ├── device-1
│   │   ├── device-2
│   │   ├── device-3
│   │   ├── device-4
│   │   ├── device-5
│   │   ├── device-6
│   │   └── device-7
│   ├── environment   保存机器环境信息
│   │   ├── cache_memory_status    保存用例执行前，机器内存占用情况
│   │   ├── disk_memory_status     保存用例执行前，机器硬盘占用情况
│   │   ├── kernel_info            保存机器内核版本信息
│   │   ├── os_info                保存机器操作系统信息
│   │   └── process_status         保存用例执行前，机器进程使用情况
│   ├── graph         保存用例执行时，生成的dump图信息，包含GE与TF Adapter的dump图
│   │   └── 250204_0    文件夹名称以进程号_DeviceId号生成
│   ├── ops              保存用例执行是，生成的算子.o，.json文件信息
│   │   └── 250204_0    文件夹名称以进程号_DeviceId号生成
│   └── stackcore        报错触发coredump时的core文件信息
│       ├── device       存储device进程coredump时的core文件信息，分device-os存储
│       │   ├── dev-os-3
│       │   └── dev-os-7
│       └── host          存储host进程coredump时的core文件信息
└── log                    保存日志数据
    ├── device             保存device侧生成的日志数据
    │   ├── aicpu         保存aicpu进程生成的日志数据，分device存储
    │   │   └── device-0
    │   ├── driver        保存驱动生成的日志数据，分device-os存储
    │   │   ├── dev-os-3
    │   │   └── dev-os-7
    │   ├── firmware      保存固件生成的日志，分device存储，包含TSCH日志
    │   │   ├── device-0
    │   │   ├── device-1
    │   │   ├── device-2
    │   │   ├── device-3
    │   │   ├── device-4
    │   │   ├── device-5
    │   │   ├── device-6
    │   │   └── device-7
    │   └── system        保存常驻进程（如TSD、slogd）生成的日志数据，分device-os存储
    │       ├── dev-os-3
    │       └── dev-os-7
    └── host               保存host侧生成的日志数据
        ├── cann           保存cann框架生成的日志数据
        ├── driver         保存驱动生成的日志数据
        ├── install        保存包历史安装情况的日志
        ├── screen.txt     保存打屏日志
        └── user_cmd       保存用户用例执行的命令
```

## 进阶功能-集成自定义数据收集<a name="section63821348291"></a>

在某些场景下，用户可能会有额外数据一起收集的诉求，一键式收集脚本支持自定义数据收集模块的集成。

使用方式如下：

1.  复制一份ops.sh文件，命名成自己模块的名字，如plugin.sh。
2.  在复制的文件中，自定义实现pre\_process、running\_process\_once、post\_process方法。

    -   pre\_process：执行用例任务之前进行的操作。
    -   running\_process\_once：执行用例任务过程中，循环进行的操作（对循环周期有诉求可以修改running\_process方法里的sleep 时长）。
    -   post\_process：执行用例任务结束后进行的操作。

    脚本内容示例：

    ```
    #!/bin/bash
    ops_path=/extra-info/ops         // 此处可以定义脚本全局可以用的到的常量
    
    pre_process()                    // 此函数，用例脚本执行前会被调用一次
    {
    base_path=$1                     // $1变量里存储的是用户指定的数据收集存储的根目录，自定义的数据收集可以基于此目录选择相对路径存储
    mkdir -p $base_path$ops_path     // 此处可以实现用户自定义的预处理行为
    }
    
    running_process_once()           // 此函数，用例脚本执行过程中会被循环调用
    {
    base_path=$1                     // $1变量里存储的是用户指定的数据收集存储的根目录，自定义的数据收集可以基于此目录选择相对路径存储
    return                           // 此处可以实现用户自定义的，用例执行中的数据收集行为
    }
    
    running_process()                // 此函数，用例脚本执行前会触发后台执行，用于循环调用running_process_once函数
    {
    while true
    do
    running_process_once $1
    sleep 60                        // 循环周期可在这里控制
    done
    }
    
    post_process()                  // 此函数，用例脚本执行结束后会被调用一次
    {
    base_path=$1                    // $1变量里存储的是用户指定的数据收集存储的根目录，自定义的数据收集可以基于此目录选择相对路径存储
    return                          // 此处可以实现用户自定义的后处理行为
    }
    
    $1 $2                          // 外部调用时，用于拉起不同函数，保留即可，不用动
    ```

3.  在npucollect.sh脚本开头的modules数组里，增加自定义的sh脚本模块名称。

    示例：modules=\(core ge log ops environment plugin\)


