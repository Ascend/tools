## 工具使用说明与扩展性介绍

### 1.Pytorch有两种模型保存方法

##### 1.1 保存整个神经网络的结构信息

- 该方法保存的模型通过torch.load('.pth')，直接初始化新的神经网络对象;

   ``*#保存模型*` 

  `torch.save(model_object,'resnet.pth')` 

  `*#加载模型*` 

  `model=torch.load('resnet.pth')`

##### 1.1 保存整个神经网络的结构信息

- 该方法保存的方式：首先是导入对应的网络，再通过net.load_state_dict(torch.load(’.pth’))完成模型参数的加载；

   `*#将my_resnet模型存储为my_resnet.pth*` 

  `torch.save(my_resnet.state_dict(),"my_resnet.pth")` 

  `*#加载resnet，模型存放在my_resnet.pth* my_resnet.load_state_dict(torch.load("my_resnet.pth"))`

   `*#其中my_resnet是my_resnet.pth对应的网络结构；*` 

### 2.Pytorch载入只含模型参数pth文件

pth文件只保存网络中的参数，具有速度快，占空间少的优点，网上Pytorch实现的可供下载的预训练模型一般也是这种吗，加载并导出为onnx格式时还需要在继承 nn.Module 实现网络各Layer层，例如，下面的示例中使用Pytorch实现了一个Net。

```
import torch
import torch.nn as nn
import torch.nn.functional as F

class CivilNet(nn.Module):
    def __init__(self):
        super(CivilNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
        self.gemfield = "gemfield.org"
        self.syszux = torch.zeros([1,1])

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
```

##### 2.1 CivilNet模型的保存

 如果我们要保存一个训练好的PyTorch模型的话，会使用下面的API： 

```
cn = CivilNet()
......
torch.save(cn.state_dict(), "your_model_path.pth")
```

##### 2.1 CivilNet模型的加载

而如果我们要load一个pth模型来进行前向的时候，会使用下面的API： 

```
cn = CivilNet()

#参数反序列化为python dict
state_dict = torch.load("your_model_path.pth")
#加载训练好的参数
cn.load_state_dict(state_dict)

#变成测试模式，dropout和BN在训练和测试时不一样
#eval()会把模型中的每个module的self.training设置为False 
cn = cn.cuda().eval()
```

### 3.pt2tf工具的使用简介

#1 建立虚拟环境 $ virtualenv .venv

\#2 激活虚拟环境 $ source .venv/bin/activate

\#3 安装依赖包 pipinstall−rrequirements.txtpipinstall−rrequirements.txt pip install -e onnx-tensorflow

\#4 生成onnx模型 $ python pt2onnx.py

\#5 生成pb模型 $ onnx-tf convert -i efficientnet-b3.onnx -o efficientnet-b3.pb

pth转pb文件的工具源码如下，开发者可以根据自己需要转换的模型进行改造，并将Pytorch中未内置而需自己实现的模型脚本上传到工程目录的models文件夹下

```
import torch
from efficientnet_pytorch import EfficientNet

# Specify which model to use
model_name = 'efficientnet-b3'
image_size = EfficientNet.get_image_size(model_name)
print('Image size: ', image_size)

# Load model
model = EfficientNet.from_pretrained(model_name)
model.set_swish(memory_efficient=False)
model.eval()
print('Model image size: ', model._global_params.image_size)

# Dummy input for ONNX
dummy_input = torch.randn(1, 3, 300, 300)

# Export with ONNX
torch.onnx.export(model, dummy_input, f"{model_name}.onnx", verbose=True)
```

- 第二行导入Pytorch中内置的网络模型EfficientNet(Pytorch内置模型中)
- 若内置模型未实现，我们在models文件夹中继承nn.Module类实现我们的网络模型，可以参考第二章中的CivilNet网络样例
- 通过模型脚本对象的from_pretrained接口来导入pth参数文件，加载模型与参数
- 调用Pytorch的onnx模块将网络模型导出为onnx模型
- 使用onnx-tensorflow模块将onnx模型转换为pb模型

