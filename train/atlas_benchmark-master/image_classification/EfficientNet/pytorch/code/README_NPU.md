# EfficientNet PyTorch

## About EfficientNet

If you're new to EfficientNets, here is an explanation straight from the official TensorFlow implementation: 

EfficientNets are a family of image classification models, which achieve state-of-the-art accuracy, yet being an order-of-magnitude smaller and faster than previous models. We develop EfficientNets based on AutoML and Compound Scaling. In particular, we first use [AutoML Mobile framework](https://ai.googleblog.com/2018/08/mnasnet-towards-automating-design-of.html) to develop a mobile-size baseline network, named as EfficientNet-B0; Then, we use the compound scaling method to scale up this baseline to obtain EfficientNet-B1 to B7.

EfficientNets achieve state-of-the-art accuracy on ImageNet with an order of magnitude better efficiency:


* In high-accuracy regime, our EfficientNet-B7 achieves state-of-the-art 84.4% top-1 / 97.1% top-5 accuracy on ImageNet with 66M parameters and 37B FLOPS, being 8.4x smaller and 6.1x faster on CPU inference than previous best [Gpipe](https://arxiv.org/abs/1811.06965).

* In middle-accuracy regime, our EfficientNet-B1 is 7.6x smaller and 5.7x faster on CPU inference than [ResNet-152](https://arxiv.org/abs/1512.03385), with similar ImageNet accuracy.

* Compared with the widely used [ResNet-50](https://arxiv.org/abs/1512.03385), our EfficientNet-B4 improves the top-1 accuracy from 76.3% of ResNet-50 to 82.6% (+6.3%), under similar FLOPS constraint.

## About EfficientNet PyTorch NPU

The source codes are based on the open source https://github.com/lukemelas/EfficientNet-PyTorch with least modified codes as far as possible.


## Quick Start

### Train  on 1 NPU:

(1) modify the last line in npu_1p.sh  with the particular params:

* fp32: taskset -c 0-64 python3.7 examples/imagenet/main.py --data=/data/imagenet --arch=efficientnet-b0 --batch-size=256 --lr=0.2 --epochs=200 --autoaug --npu=0
* O1: taskset -c 0-64 python3.7 examples/imagenet/main.py --data=/data/imagenet --arch=efficientnet-b0 --batch-size=256 --lr=0.2 --epochs=200 --autoaug --npu=0 --amp --pm=O1 --loss_scale=1024
* O2: taskset -c 0-64 python3.7 examples/imagenet/main.py --data=/data/imagenet --arch=efficientnet-b0 --batch-size=256 --lr=0.2 --epochs=200 --autoaug --npu=0 --amp --pm=O2 --loss_scale=128

(2) Execute run.sh，ALL the train log will be recorded in nohup.out.

## Know issues:

* Distribution train is NOT available.
* top1/top5 accuracy is lower than GPU about 2% in the same setting (dropout).
* O2 Performance is lower than GPU about  50 fps in the same setting (dropout, depthwiseconv2d).
* torch.rand is replaced with numpy implementation due to the lack of AICPU operator (aicpu).
* momentum has to be set to 0 due to logsoftmax precision(logsoftmax) 




