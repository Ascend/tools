中文|[EN](Readme.md)

# msame工具为模型推理工具
### 说明  
 **适用版本**： 5.0.3.alpha001及以上版本  
5.0.3.alpha001前的版本，请使用[msame.zip](https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/xuyetao/msame.zip)
### 功能
输入.om模型和模型所需要的输入bin文件，输出模型的输出数据文件，支持多次推理（指对同一输入数据进行推理）。

模型必须是通过atc工具转换的om模型，输入bin文件需要符合模型的输入要求（支持模型多输入）。

### 使用环境
已安装开发运行环境的昇腾AI推理设备。  

### 获取
- 命令行方式下载

   **git clone https://github.com/Ascend/tools.git**

- 压缩包方式下载

    1. tools仓右上角选择 **克隆/下载** 下拉框并选择 **下载ZIP**。

    2. 将ZIP包上传到开发环境中的普通用户家目录中，例如 **$HOME/ascend-tools-master.zip**。

    3. 开发环境中，执行以下命令，解压zip包。

        **unzip ascend-tools-master.zip**


### 使用方法
**环境要求：已安装开发运行环境。**   
 
设置环境变量  
(如下为设置环境变量的示例，请将/home/HwHiAiUser/Ascend/ascend-toolkit/latest替换为Ascend 的runtime安装包的实际安装路径。) 
 
**export DDK_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest**  
**export NPU_HOST_LIB=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/runtime/lib64/stub**

**注意**，在配置{NPU_HOST_LIB}环境变量时，需使用的"runtime/lib64/stub"目录下*.so库，确保在编译基于AscendCL接口的应用程序时，不依赖其他组件(例如Driver)的*.so库，编译成功后，运行应用程序时，系统回根据LD_LIBRARY_PATH环境变量查找，"Ascend-cann-toolkit安装目录/runtime/lib64"目录下的*.so库，同时会自动链接到所依赖的其他组件的*.so库。

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
./msame --model "/home/HwHiAiUser/msame/colorization.om"  --output "/home/HwHiAiUser/msame/out/" --outfmt TXT --loop 1
```


 **类型二**  模型是单输入    

a.输入数据为一个bin文件  

```
./msame --model "/home/HwHiAiUser/msame/colorization.om" --input "/home/HwHiAiUser/msame/data/colorization_input.bin" --output "/home/HwHiAiUser/msame/out/" --outfmt TXT --loop 1
```

b.输入为一个包含bin文件的目录，可推理目录下的所有bin文件，此时loop参数无效
```
./msame --model "/home/HwHiAiUser/msame/colorization.om" --input "/home/HwHiAiUser/msame/data" --output "/home/HwHiAiUser/msame/out/" --outfmt TXT
```


 **类型三**  模型是多输入  

a.每个输入的数据为一个bin文件，每个bin文件之间用英文逗号分隔，逗号前后不能有空格

```
./msame --model "/home/HwHiAiUser/msame/colorization.om" --input "/home/HwHiAiUser/msame/data1/a.bin,/home/HwHiAiUser/ljj/data2/a.bin" --output "/home/HwHiAiUser/msame/out/" --outfmt TXT  --loop 1
```

b.每个输入为一个包含bin文件的目录，每个目录中的bin文件名需保持一致，每个目录之间用英文逗号分隔，逗号前后不能有空格，此时loop参数无效
```
./msame --model "/home/HwHiAiUser/msame/colorization.om" --input "/home/HwHiAiUser/msame/data1,/home/HwHiAiUser/msame/data2" --output "/home/HwHiAiUser/msame/out/" --outfmt TXT
```
  
其他参数详情可使用--help查询。


## 注意事项
1. 运行工具的用户在当前目录需要有创建目录以及执行工具的权限，使用前请自行检查。  
2. 当模型里有动态shape，--outfmt参数设置成TXT时，运行可能会报错，可把--outfmt参数设置成BIN。因aclmdlGetCurOutputDims接口对动态shape模型的支持度不够。

## 参数说明

| 参数名   | 说明                            |
| -------- | ------------------------------- |
| --model  | 需要进行推理的om模型            |
| --input  | 模型需要的输入，支持bin文件和目录，若不加该参数，会自动生成都为0的数据                  |
| --output | 推理数据输出路径                |
| --outfmt | 输出数据的格式，TXT或者BIN      |
| --loop   | 推理次数 [1,100]，可选参数，默认1，profiler为true时，推荐为1 |
| --debug  | 调试开关，可打印model的desc信息，true或者false，可选参数，默认false |
| --profiler   | profiler开关，true或者false, 可选参数，默认false。<br>profiler数据在--output参数指定的目录下的profiler文件夹内。不能与--dump同时为true。 |  
| --dump   | dump开关，true或者false, 可选参数，默认false。<br>dump数据在--output参数指定的目录下的dump文件夹内。不能与--profiler同时为true。 |
| --device   | 指定运行设备 [0,255]，可选参数，默认0 |
| --dymBatch  | 动态Batch参数，指定模型输入的实际batch，可选参数。 <br>如atc模型转换时设置 --input_shape="data:-1,600,600,3;img_info:-1,3" --dynamic_batch_size="1,2,4,8" , dymBatch参数可设置为：--dymBatch 2|
| --dymHW  | 动态分辨率参数，指定模型输入的实际H、W，可选参数。 <br>如atc模型转换时设置 --input_shape="data:8,3,-1,-1;img_info:8,4,-1,-1"  --dynamic_image_size="300,500;600,800" , dymHW参数可设置为：--dymHW 300,500|
| --dymDims| 动态维度参数，指定模型输入的实际shape，可选参数。 <br>如atc模型转换时设置 --input_shape="data:1,-1;img_info:1,-1" --dynamic_dims="224,224;600,600" , dymDims参数可设置为：--dymDims "data:1,600;img_info:1,600"|
| --dymShape| 动态shape参数，指定模型输入的实际shape，可选参数。 <br>如atc模型转换时设置 --input_shape_range="input1:\[8\~20,3,5,-1\];input2:\[5,3\~9,10,-1\]" , dymShape参数可设置为：--dymShape "input1:8,3,5,10;input2:5,3,10,10"<br>设置此参数时，必须设置 --input 和 --outputSize。 |
| --outputSize| 指定模型的输出size，有几个输出，就设几个值，可选参数。<br>动态shape场景下，获取模型的输出size可能为0，用户需根据输入的shape预估一个较合适的值去申请内存。<br>如 --outputSize "10000,10000,10000"|
| --help| 工具使用帮助信息                  |
