# img2bin

img2bin能够生成模型推理所需的输入数据，以.bin格式保存。  
有两类数据，一类是图片数据，另一类是模型需要的第二个输入数据，如fasterrcnn的第二个输入是图片的shape信息。
图片缩放采用的是等比例缩放，空余的地方用0填充。

## 前提条件  

- 脚本可在Centos和Ubuntu环境下使用,只支持x86架构。  
- 脚本支持python2和python3.7.5(MindStudio依赖python3.7.5)。
- 如未安装opencv-python，第一次使用，脚本会自动安装。

## 获取脚本

1. 下载压缩包方式获取。

   将 https://gitee.com/ascend/tools 仓中的脚本下载至服务器的任意目录。

   例如存放路径为：$HOME/AscendProjects/tools。

2. 命令行使用git命令方式获取。

   在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

   **git clone  https://gitee.com/ascend/tools.git**

## 使用方法
进入脚本所在目录。
```
cd $HOME/AscendProjects/img2bin
```

### 第一类图片：
- 脚本会将 -i 后指定的图片目录下的所有图片按参数设置做相应的预处理，并以"文件名.bin"命名保存在-o指定的输出目录下。

```
python2 img2bin.py -i ./images -w 416 -h 416 -f BGR -a NHWC -t uint8 -m [104,117,123] -c [1,1,1] -o ./out
```
```
python3.7.5 img2bin.py -i ./images -w 416 -h 416 -f BGR -a NHWC -t uint8 -m [104,117,123] -c [1,1,1] -o ./out
```
### 第二类：
- 第二类数据，需要新建一个文件，文件模板为test.txt，"input_node"为数据，"shape"为数据的shape信息。  
- 文件模板的后缀必须是“.txt”。
- 第二类数据只需 -i、-t、-o三个参数。
- 参数 -i 需要指定文件的目录或路径，-t 需要指定数据类型，-o指定输出目录。

```
python2 img2bin.py -i ./test.txt -t uint8 -o ./out
```
```
python3.7.5 img2bin.py -i ./test.txt -t uint8 -o ./out
```

## 参数说明

| 参数名        | 说明   |
| -     | - |
| -i        | 输入目录或路径， <br>**在目录下，不能同时有图片和txt，一次只能转一种数据**       |
| -w        | 输出图片宽      |
| -h        | 输出图片高      |
| -f        | 输出图片色彩格式，支持（BGR/RGB/YUV/GRAY）      |
| -a        | 输出图片格式，支持（NCHW/NHWC）      |
| -t        | 图片或第二个数据的输出数据类型，支持（float32/uint8/int32/uint32）      |
| -m        | 减均值，默认为[0,0,0]，顺序与图片色彩格式保持一致 <br>当色彩格式为yuv时，设置[0,0] <br>当色彩格式为gray时，设置[0]    |
| -c        | 归一化，默认为 [1,1,1]，顺序与图片色彩格式保持一致 <br>当色彩格式为yuv时，设置[1,1] <br>当色彩格式为gray时，设置[1]      |
| -o        | 输出目录      |