# img2bin

img2bin能够生成模型推理所需的输入数据，以.bin格式保存。  
有两类数据，一类是图片数据，另一类是模型需要的第二个输入数据，如fasterrcnn的第二个输入是图片的shape信息。

## 环境准备

执行此脚本需要安装python3的opencv，**如已安装可跳过环境准备**。

1. 在root用户下更换源。
   ```
   vim /etc/apt/sources.list
   ```
   把原有的源更换为国内可用的源，arm源可参考 https://bbs.huaweicloud.com/forum/thread-61366-1-1.html 。
   
   
   源更新后，执行以下命令更新软件列表。
   
   ```
   apt-get update 
   ```
   
   
   
2. 安装python3的依赖。

   ```
   apt-get install python3-setuptools python3-dev build-essential python3-pip
   ```
   ```
   pip3 install enum34==1.1.6 future==0.17.1 funcsigs==1.0.2 unique protobuf numpy
   ```

   >**说明：**   
   >
   > pip3 install安装有报错“SSLError”时，请使用：pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy==1.11.2 enum34==1.1.6 future==0.17.1 funcsigs==1.0.2 unique protobuf 安装依赖，表示可信赖的主机解决问题。   

3. 安装opencv。

   ```
   pip3 install opencv_python
   ```

## 获取脚本

1. 下载压缩包方式获取。

   将 https://gitee.com/atlasdevelop/c7x_samples 仓中的脚本下载至服务器的任意目录。

   例如存放路径为：$HOME/AscendProjects/img2bin。

2. 命令行使用git命令方式获取。

   在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

   **git clone  https://gitee.com/atlasdevelop/c7x_samples.git**

## 使用方法
进入脚本所在目录。
```
cd $HOME/AscendProjects/img2bin
```

### 第一类图片：
- -i后跟**目录**表示转换图片。
- 脚本会将 -i 后指定的图片目录下的所有图片按参数设置做相应的预处理，并以"文件名.bin"命名保存在-o指定的输出目录下。

```
python3 img2bin.py -i ./images -w 416 -h 416 -f BGR -a NHWC -t uint8 -m [104,117,123] -c [1,1,1] -o ./out
```

### 第二类：
- -i后跟**文件路径**表示转换第二类数据。
- 第二类数据，需要新建一个文件，文件模板为test.txt，"input_node"为数据，"shape"为数据的shape信息。
- 第二类数据只需 -i、-t、-o三个参数。
- 参数 -i 需要指定文件的路径，-t 需要指定数据类型，-o指定输出目录。

```
python3 img2bin.py -i ./test.txt -t uint8 -o ./out
```

## 参数说明

| 参数名        | 说明   |
| -     | - |
| -i        | 图片的输入目录或第二个输入的文件路径      |
| -w        | 输出图片宽      |
| -h        | 输出图片高      |
| -f        | 输出图片色彩格式，支持（BGR/RGB/YUV/GRAY）      |
| -a        | 输出图片格式，支持（NCHW/NHWC）      |
| -t        | 图片或第二个数据的输出数据类型，支持（float32/uint8/int32/uint32）      |
| -m        | 减均值，默认为[0,0,0]，顺序与图片色彩格式保持一致 <br>当色彩格式为yuv时，设置[0,0] <br>当色彩格式为gray时，设置[0]    |
| -c        | 归一化，默认为 [1,1,1]，顺序与图片色彩格式保持一致 <br>当色彩格式为yuv时，设置[1,1] <br>当色彩格式为gray时，设置[1]      |
| -o        | 输出目录      |