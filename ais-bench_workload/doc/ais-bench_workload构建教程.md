# ais-bench-workload构建教程

## 概述
ais-bench标准化性能测试软件，又称AI Server Benchmark软件，是根据AI标准（IEEE 2937及T/CESA 1169-2021）对AI服务器进行性能测试的工具软件。

ais-bench_workload是ais-bench提供用于构建ais-bench性能测试软件包并进行测试的负载工具。

本文档主要介绍如何**搭建ais-bench_workload构建环境**并在该环境下**构建推理和训练场景的ais-bench性能测试软件包。  **
ais-bench_workload支持快速构建和标准构建。其中快速构建仅支持mindspore框架的bert和resnet两个典型模型的性能测试软件包构建。通过构建脚本扩展，标准构建能支持当前提供的所有模型的性能测试软件包构建。 

## 1. 搭建ais-bench_workload构建环境
### 1.1 环境要求

ais-bench_workload构建支持在Windows和Linux系统下进行，要求如下：

- **Windows系统：**Windows7及以上版本；安装git和winrar，版本不限。

- **Linux系统：**系统版本无限制；安装git和unrar，版本不限。  

  其中git、winrar和unrar的下载与安装，请用户自行完成，本文不详细描述。

### 1.2 源码下载
ais-bench_workload的工作目录保存在ais-bench源码包的tools目录下，可以通过以下两种方式下载ais-bench源码包：  

+ git clone下载[tools](https://github.com/Ascend/tools)仓库代码  
```
    git clone https://github.com/Ascend/tools.git
```
​       该方式直接下载码云tools仓库master分支源码。

+ 在线下载源码压缩包  
  访问tools仓库网页：https://github.com/Ascend/tools  ， 点击“克隆/下载”按钮，在弹出的窗口中点击“下载ZIP”按钮进行下载。

  该方式默认下载的是master分支ais-bench源码包为压缩包tools-master.zip，解压后tools目录默认名字是tools-master 。

### 1.3 工作目录

​     获取ais-bench源码包后，需要在ais-bench_workload工作目录下执行构建操作。ais-bench_workload工作目录为tools目录下的子目录，目录结构如下：

仅展示构建需要部分

```bash
ais-bench_workload
├── build
│   ├── build.sh   # 标准构建脚本
│   └── download_and_build.sh  # 快速构建脚本
├── doc
│   ├── ais-bench_workload_inference推理负载说明文档.md
│   ├── ais-bench_workload_train_modelarts训练说明文档.md
│   ├── ais-bench_workload_train_offline线下训练说明文档.md
│   ├── ais-bench_workload构建教程.md
│   ├── ais-bench_workload推理执行容器环境搭建指导.md
│   └── modelarts_notebook使用入门指导.docx
├── README.md
├── src    # 构建测试软件包的模型保存目录
│   ├── inference # 推理场景
│   │   ├── language
│   │   │   └── bert
│   │   ├── recommendation
│   │   │   └── widedeep
│   │   └── vision
│   │       ├── classification
│   │       └── classification_and_detection
│   └── train  # 训练场景
│       ├── huawei  # 华为模型
│       │   ├── train_mindspore_bert
│       │   ├── train_mindspore_deeplabv3
│       │   ├── train_mindspore_deepspeech2
│       │   ├── train_mindspore_faster_rcnn
│       │   ├── train_mindspore_pangu_alpha
│       │   ├── train_mindspore_resnet
│       │   ├── train_mindspore_widedeep
│       │   ├── train_tensorflow_bert_base
│       │   ├── train_tensorflow_densenet121
│       │   ├── train_tensorflow_mobilenetv2
│       │   ├── train_tensorflow_nezha_large
│       │   ├── train_tensorflow_resnet101
│       │   ├── train_tensorflow_resnet50
│       │   ├── train_tensorflow_resnext50
│       │   ├── train_tensorflow_ssd_resnet34
│       │   ├── train_tensorflow_vgg16
│       │   └── train_tensorflow_yolov3
│       └── nvidia # 英伟达模型
│           ├── train_tensorflow_bert
│           └── train_tensorflow_resnet
```



## 2. 构建ais-bench性能测试软件包
### 2.1 快速构建

#### 2.1.1 简介

快速构建可以一键构建mindspore框架的bert&resnet典型模型分别在aarch64和x86_64平台训练场景的ais-bench性能测试软件包。对于其它模型的训练软件包的构建，需要通过标准构建获取。

快速构建也可以通过扩展快速构建脚本downlaod_and_build.sh，将其它模型加入快速构建中，实现对其它模型测试软件包的快速构建。这要求熟悉Python和Shell语言并对快速构建脚本有一定的了解。

#### 2.1.2 约束

支持构建环境：

- **Windows系统：**git bash--Mircrosoft Windows git命令的模拟终端
- **Linux系统**

要求操作系统处于稳定的联网状态，主要保证能够顺利下载ais-bench stubs基础测试工具包，可以先执行curl http://www.aipubservice.com测试。

不建议多用户同时执行快速构建操作，可能出现依赖下载失败。

#### 2.1.3 构建指令  

指令格式：bash ./download_and_build.sh {version} {type}  
参数说明：

| 参数      | 说明                                                         |
| --------- | ------------------------------------------------------------ |
| {version} | 框架版本号，必选。取值需通过ais-bench_workload工作目录具体模型目录下的版本文件确认支持的版本号。快速构建仅支持bert和resnet模型。故可配置的版本号为：{type}参数为“modelarts”时，可配置为r1.3、r1.5、r1.7；未配置{type}参数时可配置为r1.5、r1.6、r1.7、r1.8、r1.9。 |
| {type}    | 线上或离线环境，可选。取值为“modelarts”，表示构建线上环境的性能测试软件包；不配置本参数时，表示构建离线环境的性能测试软件包。 |

#### 2.1.4 构建操作

示例，构建基于mindspsore 1.7版本线上执行bert和resnet模型的性能测试软件包，指令如下：

```
bash ./download_and_build.sh r1.7 modelarts
```

Windows系统需预先安装git软件。在ais-bench_workload工作目录下鼠标右键上下文菜单中点击"git bash here"，打开Microsoft Windows git命令行模拟终端，执行构建指令。鼠标右键没有git相关菜单命令时，请在windows右下角的搜索窗口输入"git" ，找到git  bash，并点击进入，执行构建指令。 

#### 2.1.5 构建结果  
构建指令成功执行后，在ais-bench_workload目录下生成output子目录，构建的性能测试软件包保存在该子目录中。  
构建结果示例：  

```
.
├── train_huawei_train_mindspore_bert-Ais-Benchmark-Stubs-aarch64-1.0-r1.7_modelarts.tar.gz
├── train_huawei_train_mindspore_bert-Ais-Benchmark-Stubs-x86_64-1.0-r1.7_modelarts.tar.gz
├── train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-aarch64-1.0-r1.7_modelarts.tar.gz
└── train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-x86_64-1.0-r1.7_modelarts.tar.gz
```

分别生成aarch64和x86_64平台下bert和resnet模型共4个软件包。

### 2.2 标准构建

#### 2.2.1 简介

标准构建是通过构建指令指定具体模型执行构建性能测试软件包的操作，相比快速构建，指令更丰富，适用模型更多且涵盖推理和训练场景。

#### 2.2 约束

- 仅支持在Linux系统下执行构建操作。
- 要求操作系统处于稳定的联网状态，主要是保证能够顺利下载ais-bench stubs基础测试工具包。可以先执行curl http://www.aipubservice.com测试网络是否畅通。
- 一次执行只能构建一个模型的性能测试软件包。

#### 2.2.3 构建准备

进行标准构建前，需要先下载ais-bench stubs基础测试工具包并将该工具解压到ais-bench_workload工作目录的build子目录下。

ais-bench stubs基础测试工具包用于选择构建测试软件包适用的aarch64和x86_64平台。

访问[面向人工智能基础技术及应用的检验检测基础服务平台](http://www.aipubservice.com/#/show/compliance/detail/127)， 通过“成果展示”->“标准符合性测试”->“人工智能服务器系统性能测试”， 进入“人工智能服务器系统性能测试”页面，在“测试工具”章节下载Stubs压缩包到本地，将Stubs压缩包解压到ais-bench_workload/build目录下。

执行操作后，ais-bench_workload/build目录结构如下:

```
ais-bench_workload
├── build
    ├── build.sh
    ├── download_and_build.sh
    ├── Ais-Benchmark-Stubs-aarch64-1.0.tar.gz
    └── Ais-Benchmark-Stubs-x86_64-1.0.tar.gz
```

#### 2.2.4 构建指令
指令格式：./build.sh  {$stubs_file} {mode} {secondary-folder-name} {third-folder-name} {version} {type}  
输出路径：在ais-bench_workload\output目录会生成相应程序包。

| 参数                    | 说明                                                         |
| ----------------------- | ------------------------------------------------------------ |
| {stubs_file}            | 选择stubs基础工具包，即选择构建测试软件包使用的aarch64和x86_64平台，必选。取值为Ais-Benchmark-Stubs-aarch64-1.0.tar.gz、Ais-Benchmark-Stubs-x86_64-1.0.tar.gz |
| {mode}                  | 选择构建测试软件包的适用场景，必选。取值为：train(训练场景)、inference(推理场景)。对应ais-bench_workload/src目下以及子目录名称。 |
| {secondary-folder-name} | 二级子目录名称，对应ais-bench_workload/src目录下二级子目录名称，必选。{mode}配置为inference时，表示选择推理模型分类，取值为：language、vision；{mode}配置为train时，表示选择模型品牌，取值为：huawei、nvidia |
| {third-folder-name}     | 三级子目录名称，对应ais-bench_workload/src目录下三级子目录名称，必选。<br> {secondary-folder-name}配置为language时，取值为bert;<br> {secondary-folder-name}配置为vision时，取值为classification_and_detection<br>  {secondary-folder-name}配置为huawei时，取值为：train_mindspore_bert、train_mindspore_deeplabv3、train_mindspore_deepspeech2、train_mindspore_faster_rcnn、train-mindspore_pangu_alpha、train_mindspore_resnet、train_mindspore_widedeep、train_tensorflow_bert_base、train_tensorflow_densenet121、train_tensorflow_mobileneetv2、train_tensorflow_nezha_large、train_tensorflow_resnet50、train_tensorflow_resnet101、train_tensorflow_resnext50、train_tensorflow_ssd_resnet34、train_tensorflow_vgg16、train_tensorflow_yolov3;<br> {secondary-folder-name}配置为nvidia时，取值为train_tensorflow_bert、train_tensorflow_resnet |
| {version}               | 模型框架版本号，仅{mode}配置为train时支持，可选。取值需通过ais-bench_worload工作目录具体模型目录下的版本文件确认支持的模型框架版本号 |
| {type}                  | 线上或离线环境，仅{mode}配置为train时支持，可选。取值为“modelarts"，表示构建线上环境的性能测试软件包；不配置本参数时，表示构建离线环境的性能测试软件包 |



##### 2.2.5 构建操作

**训练场景示例如下：**

+ 构建aarch64架构训练场景huawei mindspore框架r1.7版本resnet模型 离线运行的性能测试软件包  
  ./build.sh  ./Ais-Benchmark-Stubs-aarch64-1.0.tar.gz train huawei train_mindspore_resnet r1.7
+ 构建aarch64架构训练场景huawei mindspore框架r1.7版本resnet模型modelarts线上运行的性能测试软件包  
  ./build.sh  ./Ais-Benchmark-Stubs-aarch64-1.0.tar.gz train huawei train_mindspore_resnet r1.7 modelarts

**推理场景示例如下：**

+ 构建aarch64架构推理场景vision分类classification_and_detection模型的性能测试软件包  
  ./build.sh ../output/Ais-Benchmark-Stubs-aarch64-1.0.tar.gz inference vision classification_and_detection
+ 构建x86_64架构推理场景vision分类classification_and_detection模型的性能测试软件包  
  ./build.sh ../output/Ais-Benchmark-Stubs-x86_64-1.0.tar.gz inference vision classification_and_detection
+ 构建aarch64架构推理场景language分类bert模型的性能测试软件包  
  ./build.sh ../output/Ais-Benchmark-Stubs-aarch64-1.0.tar.gz inference language bert
+ 构建x86_64架构推理场景language分类bert模型的性能测试软件包  
  ./build.sh ../output/Ais-Benchmark-Stubs-x86_64-1.0.tar.gz inference language bert
+ 构建aarch64架构推理场景recommendation分类bert模型的性能测试软件包  
  ./build.sh ../output/Ais-Benchmark-Stubs-aarch64-1.0.tar.gz inference recommendation widedeep
+ 构建x86_64架构推理场景recommendation分类widedeep模型的性能测试软件包  
  ./build.sh ../output/Ais-Benchmark-Stubs-x86_64-1.0.tar.gz inference recommendation widedeep



