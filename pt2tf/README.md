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

## 预置条件

pytorch模型pth文件。pytorch的模型文件有两种：

1. 模型保存有网络结构和权重参数。需要在训练时使用如下接口保存模型：

   ```
   torch.save(model_object,'resnet.pth')
   ```

2. 只保存模型权重参数。在训练时使用如下接口保存模型：

   ```
   torch.save(my_resnet.state_dict(),"my_resnet.pth")
   ```

本工具两种模型的转换都支持，但是如果模型只有权重参数，则在转换时还需要完整的模型实现代码

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
    sudo pip3 install -r requirements.txt

### 2. pth模型文件转onnx
pt2tf工具对pytorch的两种模型转onnx都支持。如果是包含完备信息（网络结构和权重参数）的模型，仅仅需要模型文件即可；如果是仅包含权重参数的模型，则还需要模型的实现代码。

#### 2.1 包含网络结构和权重参数的模型转onnx

在pt2tf工具目录下执行pt2onnx.py脚本，例如:

    ```
    python3 pt2onnx.py --model_path="./resnet50_model.pth" --input_shape=1 3 224 224
    ```
参数说明：

--model_path：pytorch模型路径

--input_shape: 模型输入 shape

执行脚本后，会在pytorch模型同一目录下生成onnx文件，文件名和pytorch模型名一致, 后缀为onnx

#### 2.2 权重参数模型文件转onnx

1. 将pytorch模型和实现源码拷贝到pt2tf目录下

2. 使用vim或者文本工具打开pt2onnx.py，修改load_weight_model函数。以resnet50模型为例，修改点如下：

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
   model.load_state_dict(torch.load(model_file))
   ```

   综上，完整的load_weight_model代码：  
   
	    def load_weight_model(model_file):
	        from resnet50.resnet import ResNet50
	    
	        model = ResNet50()
	    
	        model.load_state_dict(torch.load(model_file))
	    
	        return model

3. 执行转换脚本

   ```
   python3 pt2onnx.py --model_type=1 --model_path="./resnet50_model.pth" --input_shape=1 3 224 224
   ```

​       参数说明：

​       --model_type: 模型类别，默认值为0，表示完备信息模型；1: 仅包含权重参数的模型

​       --model_path: pytorch模型存放路径

​       --input_shape: 模型输入 shape

### 3.使用 onnx-tf工具将onnx转为 pb

执行命令

    onnx-tf convert -i ./resnet50/model_resnet.onnx -o ./resnet50/model_resnet.pb

