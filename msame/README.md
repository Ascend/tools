中文|[EN](README_EN.md)

# msame工具为模型推理工具

### 功能
输入.om模型和模型所需要的输入bin文件，输出模型的输出数据文件，支持多次推理（指对同一输入数据进行推理）。

模型必须是通过atc工具转换的om模型，输入bin文件需要符合模型的输入要求（支持模型多输入）。

### 使用环境
已安装开发与运行环境的昇腾AI推理设备。  

### 获取
1. 下载压缩包方式获取。

   将 https://gitee.com/ascend/tools 仓中的脚本下载至服务器的任意目录。

   例如存放路径为：$HOME/AscendProjects/tools。

2. 命令行使用git命令方式获取。

   在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

   **git clone https://gitee.com/ascend/tools.git**


### 使用方法
#### a. 使用已编译好的工具直接运行。   

 **环境要求：架构为arm、已安装运行环境。如环境不符，请使用方法b，进行源码编译。**  

进入msame目录
```
cd $HOME/AscendProjects/tools/msame/
```
工具在out目录下,进入out目录
```
cd out
```


#### b. 源码编译运行。
 **环境要求：已安装开发运行环境，分设合设都可以。**   
工具也支持源码编译，或者使用者需要添加或者修改代码，使用者重新编译  

设置环境变量  
(如下为设置环境变量的示例，请将/home/HwHiAiUser/Ascend/ascend-toolkit/latest替换为Ascend 的ACLlib安装包的实际安装路径。) 
 
**export DDK_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest**  
**export NPU_HOST_LIB=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/acllib/lib64/stub**

进入msame目录
```
cd $HOME/AscendProjects/tools/msame/
```
运行编译脚本
```
./build.sh g++ $HOME/AscendProjects/tools/msame/out
```
第一个参数指定编译器，由运行环境决定。  
第二个参数指定工具生成的目录，填相对路径的话，是相对out目录。

## 运行示例
 **类型一**   不加input参数  

会构造全为0的假数据送入模型推理
```
./msame --model /home/HwHiAiUser/msame/colorization.om  --output /home/HwHiAiUser/msame/out/ --outfmt TXT --loop 1
```


 **类型二**  模型是单输入    

a.输入数据为一个bin文件  

```
./msame --model /home/HwHiAiUser/msame/colorization.om --input /home/HwHiAiUser/msame/data/colorization_input.bin --output /home/HwHiAiUser/msame/out/ --outfmt TXT --loop 1
```

b.输入为一个包含bin文件的目录，可推理目录下的所有bin文件，此时loop参数无效
```
./msame --model /home/HwHiAiUser/msame/colorization.om --input /home/HwHiAiUser/msame/data --output /home/HwHiAiUser/msame/out/ --outfmt TXT
```


 **类型三**  模型是多输入  

a.每个输入的数据为一个bin文件，每个bin文件之间用英文逗号分隔，逗号前后不能有空格

```
./msame --model /home/HwHiAiUser/msame/colorization.om --input /home/HwHiAiUser/msame/data1/a.bin,/home/HwHiAiUser/ljj/data2/a.bin --output /home/HwHiAiUser/msame/out/ --outfmt TXT  --loop 1
```

b.每个输入为一个包含bin文件的目录，每个目录中的bin文件名需保持一致，每个目录之间用英文逗号分隔，逗号前后不能有空格，此时loop参数无效
```
./msame --model /home/HwHiAiUser/msame/colorization.om --input /home/HwHiAiUser/msame/data1,/home/HwHiAiUser/msame/data2 --output /home/HwHiAiUser/msame/out/ --outfmt TXT
```
  
其他参数详情可使用--help查询。


## 注意事项
运行工具的用户在当前目录需要有创建目录以及执行工具的权限，使用前请自行检查。  
动态多batch功能暂不支持。

## 参数说明

| 参数名   | 说明                            |
| -------- | ------------------------------- |
| --model  | 需要进行推理的om模型            |
| --input  | 模型需要的输入，支持bin文件和目录，若不加该参数，会自动生成都为0的数据                  |
| --output | 推理数据输出路径                |
| --outfmt | 输出数据的格式，TXT或者BIN      |
| --loop   | 推理次数 [1,100]，可选参数，默认1，profiler为true时，推荐为1 |
| --debug   | 调试开关，可打印model的desc信息，true或者false，可选参数，默认fasle |
| --profiler   | profiler开关，true或者false, 可选参数，默认false。<br>profiler数据在--output参数指定的目录下的profiler文件夹内。不能与--dump同时为true。 |  
| --dump   | dump开关，true或者false, 可选参数，默认false。<br>dump数据在--output参数指定的目录下的dump文件夹内。不能与--profiler同时为true。 |
| --device   | 指定运行设备 [0,255]，可选参数，默认0 |
| --help   | 工具使用帮助信息                  |