中文|[EN](README_EN.md)

# pytorch模型转onnx工具

## 功能
当前ATC工具只支持pb和caffe模型转om模型。如果需要使用pytorch模型转om模型，可以将pytorch模型转为onnx格式，再转为pb。本工具提供pytorch模型转onnx，以及onnx转pb功能。

## 使用环境
1. 安装Ubuntu18.04的服务器或者虚拟机；

2. 服务器或者虚拟机内存大于等于4G；

3. 已经安装pip3。如未安装，可以执行如下命令安装：

   ```
   sudo apt-get install python3-pip
   sudo pip3 install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
   ```

4. 已经安装tensorflow、keras和pytorch

   当前昇腾平台支持tensorflow 1.15，考虑后继pb模型转om，tensorflow版本推荐1.15及之前版本。tensorflow 1.15版本需要源码编译安装；使用pip命令直接安装时可以1.15之前的版本，以1.14为例：

   ```
   sudo pip3 install tensorflow==1.14.0 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
   ```

   对应的keras版本为2.2.5，安装命令：

   ```
   sudo pip3 install keras==2.2.5 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
   ```

   pytorch版本只要适配待转换的pytorch模型即可。pytorch的安装可以参考官网：https://pytorch.org/get-started/locally/

## 预置条件

1.pytorch模型文件。pytorch模型保存有两种，一种是保存有权重参数和网络结构，另外一种是指保存权重参数。本工具只支持保存权重参数的模型文件，模型保存接口示例：

   ```
torch.save(my_resnet.state_dict(),"my_resnet.pth")
   ```

2.模型实现代码。权重参数模型加载时，需要使用模型创建接口创建模型，作为模型加载的参数，所以需要模型实现代码。

## 工具获取

**方法1. 下载压缩包方式获取**

将 https://gitee.com/ascend/tools 仓中的脚本下载至服务器的任意目录。

例如存放路径为：$HOME/AscendProjects/tools。

**方法2. 命令行使用git命令方式获取**

在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

    git clone https://gitee.com/ascend/tools.git



## 使用方法

### 1. 安装工具依赖包   

    cd $HOME/AscendProjects/tools/pt2tf/
    sudo pip3 install -e onnx-tensorflow

### 2. pth模型文件转onnx
1. 将pytorch模型和实现源码拷贝到pt2tf目录下

2. 使用vim或者文本工具打开pt2onnx.py，修改load_model函数。以resnet50模型为例，修改点如下：

   （1）导入模型实现文件：

   ```
   #修改点1:导入模型代码.
   #例如:模型实现代码目录为./resnet50,网络实现在resnet.py的class ResNet50类
   from resnet50.resnet import ResNet50
   ```

   （2） 使用pytorch实例化模型对象

   ```
   #修改点2:创建模型对象
   model = ResNet50()
   ```

   （3）加载训练好的模型

   ```
   #修改点3:训练好的模型路径
   model.load_state_dict(torch.load(model_path))
   ```

   综上，完整的load_weight_model代码：  

       def load_model(model_path, input_shape):
           if not os.path.exists(model_path):
               print("The pytorch model is not exist")
               return None
           from resnet50.resnet import ResNet50
       
           model = ResNet50()
       
           model.load_state_dict(torch.load(model_path))
       
           return model

3. 执行转换脚本

   ```
   python3 pt2onnx.py --model_path="./resnet50/models/resnet50_best.pth" --input_shape 1 3 224 224
   ```

​       参数说明：

​       --model_type: 模型类别，默认值为0，表示完备信息模型；1: 仅包含权重参数的模型

​       --model_path: pytorch模型存放路径

​       --input_shape: 模型输入 shape

如果执行成功，将在pytorch目录下生成onnx文件，文件名和pytorch模型文件名一致，例如./resnet50/models/resnet50_best.onnx

### 3.使用 onnx-tf工具将onnx转为 pb

执行命令

    onnx-tf convert -i ./resnet50/models/resnet50_best.onnx -o ./resnet50/resnet50_best.pb

参数说明：

-i：onnx文件路径

-o: 输出的pb模型文件

onnx-tf convert的参数说明详见帮助：

```
onnx-tf convert --help
```

