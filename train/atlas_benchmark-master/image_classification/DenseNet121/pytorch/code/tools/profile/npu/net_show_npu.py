import os

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms
import torchvision.models as models

CALCULATE_DEVICE = "npu:0"
torch.npu.set_device(CALCULATE_DEVICE)

"""
alexnet | densenet121 |
densenet161 | densenet169 | densenet201 |
resnet101 | resnet152 | resnet18 | resnet34 |
resnet50 | squeezenet1_0 | squeezenet1_1 | vgg11 |
vgg11_bn | vgg13 | vgg13_bn | vgg16 | vgg16_bn | vgg19 |
mobilenet_v2 | shufflenet_v2_x0_5 |
vgg19_bn (default: resnet18)
"""

img = torch.rand(size=(1,3,224,224),dtype=torch.float32).to(CALCULATE_DEVICE, non_blocking=True)
print("img prepared")

model_name='densenet121'
model = models.__dict__[model_name]().to(CALCULATE_DEVICE)
model.train()
print("model prepared")

outputs = model(img)
print("cal done, results is {}".format(outputs))

labels=torch.rand(size=(1,)).to(torch.int32).to(CALCULATE_DEVICE, non_blocking=True)
criterion = nn.CrossEntropyLoss().to(CALCULATE_DEVICE)
with torch.autograd.profiler.profile(record_shapes=True,use_npu=True) as prof:
    outputs = model(img)
    print("output ok")
    loss = criterion(outputs, labels)
    print("loss ok")
    with torch.autograd.profiler.record_function("label-bp"):
        loss.backward()

#print(prof.key_averages().table()) 
print(prof) 
prof.export_chrome_trace(model_name + ".prof")


# with SummaryWriter(os.path.join('runs',model_name)) as w:    
#     w.add_graph(model, img)
# print("tenorboard add graph ok")

