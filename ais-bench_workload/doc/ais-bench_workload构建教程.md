# ais-bench-workload构建教程

## 简介
本文档是指导用户了解asi-bench_workload搭建构建环境、构建推理和训练测试软件包。  
面向对象是对Windows和linux操作系统有初步了解的人员。需要用户熟悉git命令操作、常见shell指令、联网配置等    
构建方式支持Windows快速构建、标准构建。两者都需要连接公开网络下载，请确保网络畅通  

## 1. 构建准备
Windows系统可以使用Windows7以上版本，Linux无发行版本限制。  
构建环境要求安装git, 无版本限制。 Windows还要求安装Winrar，版本不限。Linux系统要求确认安装unrar，版本不限。

## 2. 源码下载
源码下载有2种方式：  
+ git clone下载[tools](https://github.com/Ascend/tools)仓库代码  
```
    git clone https://github.com/Ascend/tools.git
```
+ 在线下载源码压缩包  
浏览器输入tools仓库网页链接，https://github.com/Ascend/tools  ， 点击“克隆/下载”，在弹出的窗口中点击“下载ZIP”，进行下载。默认下载后的压缩包名字是tools-master.zip。请通过winrar等解压缩工具，解压ZIP包。注意ZIP解压后目录名字是tools-master      

## 3. 构建
工作目录：ais-bench_workload/build  
### 3.1 快速构建
快速构建要求网络通畅，能自动下载相关构建依赖。可以一键构建bert&resnet2个典型模型， aarch64和x86_64平台共4个训练软件包。对于其它模型的训练软件包以及所有模型的推理软件包的构建，请选择标准构建。

通过适配该脚本支持其它模型、其它构建类型（比如线上）, 快速构建脚本也能达到标准构建的强大构建能力。请自行对比build.sh来扩展。      
支持构建环境：

- git bash-- Mircrosoft Windows git命令的模拟终端
- Linux系统

#### 3.1.1 构建指令  

构建指令格式：bash ./download_and_build.sh {version} {type}  
参数说明：

+ version 框架版本号。必选。版本取值，对应模型子目录中的适配版本信息
+ type 线上还是线下环境。可选。默认不取值为线下环境。取值为"modelarts"时，表示云上执行训练

示例，构建基于mindspore 1.7框架云上执行bert&resnet训练软件包指令：

```
bash ./download_and_build.sh r1.7 modelarts
```

#### 3.1.2 Windows构建  

在工作目录中，点击鼠标上下文菜单"git bash here", 进入构建终端环境。鼠标右键没有git相关菜单命令时，请在windows右下角的搜索窗口输入"git" ，找到git  bash，并点击进入，执行构建指令。 

#### 3.1.3 Linux构建

Linux系统中直接在工作目录执行脚本download_and_build.sh

#### 3.1.4 构建结果  
构建指令成功执行后，在ais-bench_workload子目录output中输出构建结果。  
构建结果示例说明：  
构建基于mindspore 1.7框架云上执行bert&resnet训练软件包，构建输出目录为ais-bench_workload/output，有4个测试包生成，aarch64和x86_64平台各2个：

```
root@DESKTOP-L64O580: MINGW64 /d/codes/C++/huawei.com/tools-lhb/ais-bench_workload/output# tree -L 1
.
├── train_huawei_train_mindspore_bert-Ais-Benchmark-Stubs-aarch64-1.0-r1.7_modelarts.tar.gz
├── train_huawei_train_mindspore_bert-Ais-Benchmark-Stubs-x86_64-1.0-r1.7_modelarts.tar.gz
├── train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-aarch64-1.0-r1.7_modelarts.tar.gz
└── train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-x86_64-1.0-r1.7_modelarts.tar.gz
```

### 3.2 标准构建
标准构建要求网络通畅，适用于所有训练和推理模型的测试软件包的构建。相比快速构建，指令更丰富，适用模型更多， 涵盖推理和训练功能    
构建环境：支持Linux或者Windows git bash终端。Linux环境无发行版本限制。   
该构建方式要求熟悉tools工程ais-bench_workload的目录结构，请提前阅读相关模型的doc目录文档   

#### 3.2.1 下载ais-bench stubs测试工具
点击[面向人工智能基础技术及应用的检验检测基础服务平台](http://www.aipubservice.com/#/show/compliance/detail/127)网址, 通过“成果展示”->“标准符合性测试”->“人工智能服务器系统性能测试”， 进入“人工智能服务器系统性能测试”页面，在“测试工具”章节下载Stubs压缩包到本地备用。

#### 3.2.2 解压stubs压缩包，将stubs二进制压缩包拷贝到build目录
目录结构如下：
```
tools
├── ais-bench_workload
    ├── build
        ├── build.sh
        ├── download_and_build.sh
        ├── Ais-Benchmark-Stubs-aarch64-1.0.tar.gz
        └── Ais-Benchmark-Stubs-x86_64-1.0.tar.gz
```

#### 3.2.3 构建测试包

##### 3.2.3.1 构建指令
指令格式：./build.sh  {$stubs_file} {mode} {secondary-folder-name} {third-folder-name} {version} {type}  
输出路径：在ais-bench_workload\output目录会生成相应程序包。  
参数说明： 
+ stubs_file 必选。下载的stubs.rar中适用构建平台要求的stubs二进制压缩包 
+ mode 执行模式。必选。取值：train--训练模式，inference--推理模式。ais-bench_workload\src目录下一级子目录名称，不包含common 
+ secondary-folder-name 二级子目录名称。必选。ais-bench_workload\src目录下二级子目录名称
+ third-folder-name 三级子目录名称。可选。ais-bench_workload\src目录下三级子目录名称
+ version  框架版本号。训练必选。训练模式专用参数。版本取值，对应模型子目录中的适配版本信息
+ type 线上还是线下环境。训练可选。训练模式专用参数。默认不取值为线下环境。取值为"modelarts"时，表示云上执行训练
##### 3.2.3.2 训练构建指令示例
+ 构建mindspore框架resnet模型 r1.7版本 aarch64架构的程序包  
  ./build.sh  ./Ais-Benchmark-Stubs-aarch64-1.0.tar.gz train huawei train_mindspore_resnet r1.7
+ 构建mindspore框架resnet模型 r1.7版本 aarch64架构 modelarts运行的程序包  
  ./build.sh  ./Ais-Benchmark-Stubs-aarch64-1.0.tar.gz train huawei train_mindspore_resnet r1.7 modelarts

##### 3.2.3.3 推理构建指令示例
+ 构建vision分类classification_and_detection类型，aarch64架构的推理程序包  
  ./build.sh ../output/Ais-Benchmark-Stubs-aarch64-1.0.tar.gz inference vision classification_and_detection
+ 构建vision分类classification_and_detection类型，x86_64架构的推理程序包  
  ./build.sh ../output/Ais-Benchmark-Stubs-x86_64-1.0.tar.gz inference vision classification_and_detection
+ 构建language分类bert模型, aarch64架构的推理程序包  
  ./build.sh ../output/Ais-Benchmark-Stubs-aarch64-1.0.tar.gz inference language bert
+ 构建language分类bert模型, x86_64架构的推理程序包  
  ./build.sh ../output/Ais-Benchmark-Stubs-x86_64-1.0.tar.gz inference language bert



