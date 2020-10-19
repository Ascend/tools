# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the BSD 3-Clause License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://spdx.org/licenses/BSD-3-Clause.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms
import torchvision.models as models

"""
alexnet | densenet121 |
densenet161 | densenet169 | densenet201 |
resnet101 | resnet152 | resnet18 | resnet34 |
resnet50 | squeezenet1_0 | squeezenet1_1 | vgg11 |
vgg11_bn | vgg13 | vgg13_bn | vgg16 | vgg16_bn | vgg19 |
mobilenet_v2 | shufflenet_v2_x0_5 |
vgg19_bn (default: resnet18)
"""
model_name='densenet121'
model = models.__dict__[model_name]()

img = torch.rand(size=(1,3,224,224))

#print(model(img))

labels = torch.rand(size=(1,))
criterion = nn.CrossEntropyLoss()
with torch.autograd.profiler.profile(record_shapes=True) as prof:
    outputs = model(img)
    loss = criterion(outputs, labels)
    with torch.autograd.profiler.record_function("label-bp"):
        loss.backward()

#print(prof.key_averages().table()) 
print(prof) 
prof.export_chrome_trace(model_name + ".prof")


with SummaryWriter(os.path.join('runs',model_name)) as w:    
    w.add_graph(model, img)

