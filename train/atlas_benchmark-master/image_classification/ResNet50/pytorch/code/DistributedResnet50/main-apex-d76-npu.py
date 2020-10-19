# -*- coding: utf-8 -*-
'''
BSD 3-Clause License

Copyright (c) Soumith Chintala 2016,
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



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
'''

import argparse
import os
import random
import shutil
import time
import warnings

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.distributed as dist
import torch.optim
import torch.multiprocessing as mp
import torch.utils.data
import torch.utils.data.distributed
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models

from apex import amp
from benchmark_log import hwlog
from benchmark_log.basic_utils import get_environment_info
from benchmark_log.basic_utils import get_model_parameter

#########################################################################
#NV 代码移植
#########################################################################
import image_classification.resnet as nvmodels
from image_classification.smoothing import LabelSmoothingGpu
from image_classification.smoothing import CrossEntropy
from image_classification.mixup import NLLMultiLabelSmooth, MixUpWrapper

# import image_classification.resnet as models
import image_classification.logger as log

# from image_classification.smoothing import LabelSmoothing
# from image_classification.mixup import NLLMultiLabelSmooth, MixUpWrapper
# from image_classification.dataloaders import *
from image_classification.training import *
# from image_classification.utils import *
#########################################################################

'''
#######################################
多P命令参考：  
---------------------------------------
GPU 多P命令参考
---------------------------------------
python ./main-apex.py     -p 1 -a resnet50 --dist-url 'tcp://127.0.0.1:50000' --dist-backend 'hccl' --multiprocessing-distributed --world-size 1 --batch_size=256 --rank 0 --seed 49 --device 'npu' --gpu=$i useruserdataimagenet  .logtest.txt 
python ori-resnet50-main-apex.py --addr='10.136.181.51' -j64 -p 1 -a resnet50 --dist-url 'tcp127.0.0.150000' --dist-backend 'hccl' --multiprocessing-distributed --world-size 1 --batch-size=2048 --rank 0 --gpu=$i --seed 49 --device 'npu'  /opt/npu/imagenet > ${logfile} &
python ./main-apex-d76.py -p 1 -a resnet50 --dist-url 'tcp://127.0.0.1:50000' --dist-backend 'nccl' --multiprocessing-distributed --world-size 1 -b 2048 --epochs 90 --rank 0 /user/user/data/imagenet > log-nv-parameter-bs2048-epoch90-ampo2-benchmark0-20200722-0932.txt
---------------------------------------
NPU多P命令参考
---------------------------------------
python ./main-apex-d76-npu.py --addr='10.136.181.51' -j256 --lr 2.048 --warmup 8 --label-smoothing 0.1 --mom 0.875 --wd 3.0517578125e-05 --static-loss-scale 128 -p 1 -a resnet50 --dist-url 'tcp://127.0.0.1:50000' --dist-backend 'hccl' --multiprocessing-distributed --world-size 1 -b 4096 --epochs 90 --rank 0 --benchmark 0 --device 'npu' /data/imagenet >  8p-bs4096.txt

#######################################
单P命令参考：
---------------------------------------
GPU 单P命令参考
---------------------------------------

---------------------------------------
NPU 单P命令参考
---------------------------------------
python ../../../test_py/precision/d76/main-apex-d76-npu.py -p 1 -a resnet50 --benchmark 1 -b 512 --seed 49 --device 'npu' --checkpoint-freq 10 --checkpoint-nameprefix 'checkpoint-npu-1p-benchmark1-bs512' --gpu 5 /data/imagenet  > ./log-npu-nv-pytorch-1p-parameter-benchmark1-bs512-epoch90-ampo2-20200723-1912.txt
python ../../../test_py/precision/d76/main-apex-d76-npu.py -p 1 -a resnet50 --benchmark 0 -b 512 --seed 49 --device 'npu' --checkpoint-freq 10 --checkpoint-nameprefix 'checkpoint-npu-1p-benchmark0-bs512' --gpu 4 /data/imagenet  > ./log-npu-nv-pytorch-1p-parameter-benchmark0-bs512-epoch90-ampo2-20200723-1912.txt
#######################################
'''


BATCH_SIZE = 512
OPTIMIZER_BATCH_SIZE=2048
LOG_STEP = 10

model_names = sorted(name for name in models.__dict__
    if name.islower() and not name.startswith("__")
    and callable(models.__dict__[name]))

parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
parser.add_argument('--data', metavar='DIR',
                    help='path to dataset')
parser.add_argument('-a', '--arch', metavar='ARCH', default='resnet50',
                    choices=model_names,
                    help='model architecture: ' +
                        ' | '.join(model_names) +
                        ' (default: resnet18)')
parser.add_argument('-j', '--workers', default=32, type=int, metavar='N',
                    help='number of data loading workers (default: 4)')
parser.add_argument('--epochs', default=90, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--start-epoch', default=0, type=int, metavar='N',
                    help='manual epoch number (useful on restarts)')
parser.add_argument('-b', '--batch-size', default=BATCH_SIZE, type=int,
                    metavar='N',
                    help='mini-batch size (default: 256), this is the total '
                         'batch size of all GPUs on the current node when '
                         'using Data Parallel or Distributed Data Parallel')


###############################################################################
#参数调节
###############################################################################
#============================================================
# DeepLearningExamples-master\PyTorch\Classification\ConvNets\resnet50v1.5\training\AMP\DGX1_RN50_AMP_90E.sh
#命令参数
#============================================================
# python ./multiproc.py --nproc_per_node 8 
# ./main.py /imagenet 
#           --data-backend dali-cpu 
#           --raport-file raport.json 
#           -j5 
#           -p 100 
#      （✔）--lr 2.048  
#           --optimizer-batch-size 2048   
#      （✔）--warmup 8 
#           --arch resnet50 
#      （卍）-c fanin ---------------------------('--model-config')
#      （✔）--label-smoothing 0.1 
#      （✔）--lr-schedule cosine 
#      （✔）--mom 0.875 ------------------------(标准动量优化算法)
#      （✔）--wd 3.0517578125e-05 
#      （D）--bn_weight_decay,default:false
#      （D）--nesterov,default:false
#           --workspace ${1:-./} 
#           -b 2048,8P
#      （✔）--amp 
#      （卍）--static-loss-scale 128 
#           --epochs 90
#============================================================

########################################
#'--lr', '--learning-rate', 
########################################
#----------------------------------------
# NV set 
#----------------------------------------
#待补充
#----------------------------------------
# Pytorch set 
#----------------------------------------
# def adjust_learning_rate(optimizer, epoch, args):
#     """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
#     lr = args.lr * (0.1 ** (epoch // 30))
#     for param_group in optimizer.param_groups:
#         param_group['lr'] = lr
#----------------------------------------
parser.add_argument('--lr', '--learning-rate', 
                    #default=0.1, #pytorch
                    default=2.048, #nvidia
                    type=float,
                    metavar='LR', help='initial learning rate', dest='lr')

parser.add_argument('--momentum', 
                    #default=0.9, #pytorch
                    default=0.875, #nvidia
                    type=float, metavar='M',
                    help='momentum')    #标准动量优化算法
parser.add_argument('--wd', '--weight-decay', 
                    #default=1e-4, #pytorch
                    default=3.0517578125e-05, #nvidia
                    type=float,
                    metavar='W', help='weight decay (default: 1e-4)',
                    dest='weight_decay')

# parser.add_argument('--momentum',
#                     default=0.9,
#                     type=float,
#                     metavar='M',
#                     help='momentum')
# parser.add_argument('--weight-decay',
#                     '--wd',
#                     default=1e-4,
#                     type=float,
#                     metavar='W',
#                     help='weight decay (default: 1e-4)')
###############################################################
#nv cmd parameter
###############################################################

model_configs = nvmodels.resnet_configs.keys()
parser.add_argument('--model-config',
                    '-c',
                    metavar='CONF',
                    default='classic',
                    choices=model_configs,
                    help='model configs: ' + ' | '.join(model_configs) +
                    '(default: classic)')


    # parser.add_argument('--lr',
    #                     '--learning-rate',
    #                     default=0.1,
    #                     type=float,
    #                     metavar='LR',
    #                     help='initial learning rate')
    
#-----------------------------------------------------
# https://pytorch.org/docs/master/optim.html#how-to-adjust-learning-rate
# torch.optim.lr_scheduler.LambdaLr
# torch.optim.lr_scheduler.StepLR
# torch.optim.lr_scheduler.MultiStepLR
# torch.optim.lr_scheduler.ExponentialLR
# torch.optim.lr_sheduler.CosineAnneaingLR
# torch.optim.lr_scheduler.ReduceLROnPlateau
#-----------------------------------------------------
parser.add_argument('--lr-schedule',
                    default='cosine',
                    type=str,
                    metavar='SCHEDULE',
                    choices=['step', 'linear', 'cosine'],
                    help='Type of LR schedule: {}, {}, {}'.format(
                        'step', 'linear', 'cosine'))
parser.add_argument('--warmup',
                    default=8,
                    type=int,
                    metavar='E',
                    help='number of warmup epochs')

parser.add_argument('--label-smoothing',
                    default=0.0,
                    type=float,
                    metavar='S',
                    help='label smoothing')
#------------------------------------
#数据增广方式
#------------------------------------
parser.add_argument('--mixup',
                    default=0.0,
                    type=float,
                    metavar='ALPHA',
                    help='mixup alpha')


parser.add_argument(
    '--bn-weight-decay',
    action='store_true',
    help=
    'use weight_decay on batch normalization learnable parameters, (default: false)'
)

parser.add_argument(
    '--static-loss-scale',
    type=float,
    default=128,
    help=
    'Static loss scale, positive power of 2 values can improve fp16 convergence.'
)
parser.add_argument(
    '--dynamic-loss-scale',
    action='store_true',
    help='Use dynamic loss scaling.  If supplied, this argument supersedes '
    + '--static-loss-scale.')

parser.add_argument('--nesterov',
                    action='store_true',
                    help='use nesterov momentum, (default: false)')
parser.add_argument('--amp',
                    action='store_true',
                    help='Run model AMP (automatic mixed precision) mode.')
parser.add_argument('--fp16',
                    action='store_true',
                    help='Run model fp16 mode.')
parser.add_argument(
    '--workspace',
    type=str,
    default='./',
    metavar='DIR',
    help='path to directory where checkpoints will be stored')
parser.add_argument('--raport-file',
                    default='experiment_raport.json',
                    type=str,
                    help='file in which to store JSON experiment raport')
###############################################################

parser.add_argument('-p', '--print-freq', default=10, type=int,
                    metavar='N', help='print frequency (default: 10)')
parser.add_argument('--resume', default='', type=str, metavar='PATH',
                    help='path to latest checkpoint (default: none)')
parser.add_argument('-e', '--evaluate', dest='evaluate', action='store_true',
                    help='evaluate model on validation set')
parser.add_argument('--pretrained', dest='pretrained', action='store_true',
                    help='use pre-trained model')
parser.add_argument('--world-size', default=-1, type=int,
                    help='number of nodes for distributed training')
parser.add_argument('--rank', default=-1, type=int,
                    help='node rank for distributed training')
parser.add_argument('--dist-url', default='tcp://224.66.41.62:23456', type=str,
                    help='url used to set up distributed training')
parser.add_argument('--dist-backend', default='nccl', type=str,
                    help='distributed backend')
parser.add_argument('--seed', default=None, type=int,
                    help='seed for initializing training. ')
parser.add_argument('--gpu', default=None, type=int,
                    help='GPU id to use.')
parser.add_argument('--multiprocessing-distributed', action='store_true',
                    help='Use multi-processing distributed training to launch '
                         'N processes per node, which has N GPUs. This is the '
                         'fastest way to use PyTorch for either single node or '
                         'multi node data parallel training')

parser.add_argument('-bm', '--benchmark', default=0, type=int,
                    metavar='N', help='set benchmark status (default: 1,run benchmark)')
parser.add_argument('--device', default='npu', type=str,
                        help='npu or gpu')
parser.add_argument('--device_num', default=-1, type=int,
                        help='device num')
parser.add_argument('--addr', default='10.136.181.115', type=str,
                        help='master addr')
parser.add_argument('--checkpoint-nameprefix', default='checkpoint', type=str,
                        help='checkpoint-nameprefix')
parser.add_argument('--checkpoint-freq', default=10, type=int,
                    metavar='N', help='checkpoint frequency (default: 0)'
                                      '0: save only one file whitch per epoch;'
                                      'n: save diff file per n epoch'
                                      '-1:no checkpoint,not support')
best_acc1 = 0

#-c,--model-config fanin                    
######################################################################
#PyTorch\Classification\ConvNets\main-org.py:352
# model_and_loss = ModelAndLoss((args.arch, args.model_config),
#                               loss,
#                               pretrained_weights=pretrained_weights,
#                               cuda=True,
#                               fp16=args.fp16)
######################################################################
            #
            #
         #  #  #
          # # #
            #
######################################################################
#image_classification\training.py  -----> ModelAndLoss.__init__
#model = models.build_resnet(arch[0], arch[1])
######################################################################
            #
            #
         #  #  #
          # # #
            #
######################################################################
# image_classification\resnet.py:build_resnet
# def build_resnet(version, config, verbose=True):
#     version = resnet_versions[version]
#     config = resnet_configs[config]

#     builder = ResNetBuilder(version, config)
#     if verbose:
#         print("Version: {}".format(version))
#         print("Config: {}".format(config))
#     model = version['net'](builder,
#                            version['block'],
#                            version['expansion'],
#                            version['layers'],
#                            version['widths'],
#                            version['num_classes'])
#     return model
######################################################################
# fanin
#  'resnet50' : {
# 'net' : ResNet,
# 'block' : Bottleneck,
# 'layers' : [3, 4, 6, 3],
# 'widths' : [64, 128, 256, 512],
# 'expansion' : 4,
# 'num_classes' : 1000,
# },
def nvidia_model_config(args):
    model = ResNet(builder,              #    builder,
                    Bottleneck,           #    version['block'],
                    4,                    #    version['expansion'],
                    [3, 4, 6, 3],         #    version['layers'],
                    [64, 128, 256, 512],  #    version['widths'],
                    1000)                 #    version['num_classes'])
    return model

def nvidia_logger_init(args):
    #if not torch.distributed.is_initialized() or torch.distributed.get_rank() == 0:
    if False:
        logger = log.Logger(args.print_freq, [
            dllogger.StdOutBackend(dllogger.Verbosity.DEFAULT,
                               step_format=log.format_step),
            dllogger.JSONStreamBackend(
                dllogger.Verbosity.VERBOSE,
                os.path.join(args.workspace, args.raport_file))
        ])

    else:
        logger = log.Logger(args.print_freq, [])
    logger.log_parameter(args.__dict__, verbosity=dllogger.Verbosity.DEFAULT)
    args.logger = logger
#--label-smoothing 0.1 命令参数中用到，需调测
def nvidia_mixup_and_label_smoothing_getlossfunction(args):
    #PyTorch\Classification\ConvNets\main-org.py:346    获取loss接口
    loss = nn.CrossEntropyLoss
    if args.mixup > 0.0: #mixup命令参数中未用到，暂不调测
        loss = lambda: NLLMultiLabelSmooth(args.label_smoothing)
    elif args.label_smoothing > 0.0: #--label-smoothing 0.1 命令参数中用到，需调测
        if args.device == 'npu':
           loss = lambda: CrossEntropy(args.label_smoothing)
        if args.device == 'gpu':
           loss = lambda: LabelSmoothingGpu(args.label_smoothing)
    #criterion = loss()   
    
    if args.gpu is not None:
        if args.device == 'npu':
            loc = 'npu:{}'.format(args.gpu)
            criterion = loss().to(loc)
        else:
            criterion = loss().cuda(args.gpu) 
    print("nvidia_mixup_and_label_smoothing_getlossfunction return")
    return criterion
    # model_and_loss = ModelAndLoss((args.arch, args.model_config),
    #                               loss,
    #                               pretrained_weights=pretrained_weights,
    #                               cuda=True,
    #                               fp16=args.fp16)
    # #============================================================


#mixup命令参数中未用到，暂不调测
def nvidia_mixup_get_train_loader_iter(args):
    #PyTorch\Classification\ConvNets\main-org.py:378 获取训练loader
    #mixup命令参数中未用到，暂不调测
    # train_loader, train_loader_len = get_train_loader(args.data,
    #                                                   args.batch_size,
    #                                                   1000,
    #                                                   args.mixup > 0.0,
    #                                                   workers=args.workers,
    #                                                   fp16=args.fp16)
    if args.mixup != 0.0: #mixup命令参数中未用到，暂不调测
        train_loader = MixUpWrapper(args.mixup, 1000, train_loader)

    #PyTorch\Classification\ConvNets\main-org.py:403
    # optimizer = get_optimizer(list(model_and_loss.model.named_parameters()),
    #                           args.fp16,
    #                           args.lr,
    #                           args.momentum,
    #                           args.weight_decay,
    #                           nesterov=args.nesterov,
    #                           bn_weight_decay=args.bn_weight_decay,
    #                           state=optimizer_state,
    #                           static_loss_scale=args.static_loss_scale,
    #                           dynamic_loss_scale=args.dynamic_loss_scale)

#input:
#       --warmup 8     
#       --lr-schedule cosine                    
#output:
#
#
def nvidia_lr_policy(args):
    #PyTorch\Classification\ConvNets\main-org.py:414
    logger=args.logger
    if args.lr_schedule == 'step':
        lr_policy = lr_step_policy(args.lr, [30, 60, 80],
                                0.1,
                                args.warmup,
                                logger=logger)
    elif args.lr_schedule == 'cosine':
        lr_policy = lr_cosine_policy(args.lr,
                                    args.warmup,
                                    args.epochs,
                                    logger=logger)
    elif args.lr_schedule == 'linear':
        lr_policy = lr_linear_policy(args.lr,
                                    args.warmup,
                                    args.epochs,
                                    logger=logger)
    return lr_policy
    # criterion = lr_policy
    # return criterion

def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    cudnn.deterministic = True
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def main():
    args = parser.parse_args()
    print("===============main()=================")
    print(args)
    print("===============main()=================")
    #print("+++++++++++++++++++++++++++ before set KERNEL_NAME_ID：",os.environ['KERNEL_NAME_ID'])

    os.environ['KERNEL_NAME_ID'] = str(0)

    print("+++++++++++++++++++++++++++KERNEL_NAME_ID:",os.environ['KERNEL_NAME_ID'])

    if args.seed is not None:
        random.seed(args.seed)
        torch.manual_seed(args.seed)
        cudnn.deterministic = True
        warnings.warn('You have chosen to seed training. '
                      'This will turn on the CUDNN deterministic setting, '
                      'which can slow down your training considerably! '
                      'You may see unexpected behavior when restarting '
                      'from checkpoints.')

    os.environ['MASTER_ADDR'] = args.addr  # '10.136.181.51'
    os.environ['MASTER_PORT'] = '29501'

    if args.gpu is not None:
        warnings.warn('You have chosen a specific GPU. This will completely '
                      'disable data parallelism.')

    if args.dist_url == "env://" and args.world_size == -1:
        args.world_size = int(os.environ["WORLD_SIZE"])

    args.distributed = args.world_size > 1 or args.multiprocessing_distributed

    if args.device_num != -1:
        ngpus_per_node = args.device_num
    elif args.device == 'npu':
        ngpus_per_node = torch.npu.device_count()
    else:
        ngpus_per_node = torch.cuda.device_count()
    if args.multiprocessing_distributed:
        # Since we have ngpus_per_node processes per node, the total world_size
        # needs to be adjusted accordingly
        args.world_size = ngpus_per_node * args.world_size
        # Use torch.multiprocessing.spawn to launch distributed processes: the
        # main_worker process function
        # The child process uses the environment variables of the parent process,
        # we have to set KERNEL_NAME_ID for every proc
        if args.device == 'npu':
            main_worker(args.gpu, ngpus_per_node, args)
            #mp.spawn(main_worker, nprocs=ngpus_per_node, args=(ngpus_per_node, args))
        else:
            mp.spawn(main_worker, nprocs=ngpus_per_node, args=(ngpus_per_node, args))
    else:
        # Simply call main_worker function
        main_worker(args.gpu, ngpus_per_node, args)


def main_worker(gpu, ngpus_per_node, args):
    global best_acc1
    args.gpu = gpu

    print("[gpu id:",args.gpu,"]","+++++++++++++++++++++++++++ before set KERNEL_NAME_ID:",os.environ['KERNEL_NAME_ID'])
    os.environ['KERNEL_NAME_ID'] = str(gpu)
    print("[gpu id:",args.gpu,"]","+++++++++++++++++++++++++++KERNEL_NAME_ID:",os.environ['KERNEL_NAME_ID'])

    if args.gpu is not None:
        print("[gpu id:",args.gpu,"]","Use GPU: {} for training".format(args.gpu))

    if args.distributed:
        if args.dist_url == "env://" and args.rank == -1:
            args.rank = int(os.environ["RANK"])
        if args.multiprocessing_distributed:
            # For multiprocessing distributed training, rank needs to be the
            # global rank among all the processes
            args.rank = args.rank# * ngpus_per_node + gpu

        if args.device == 'npu':
            dist.init_process_group(backend=args.dist_backend, #init_method=args.dist_url,
                                    world_size=args.world_size, rank=args.rank)
        else:
            dist.init_process_group(backend=args.dist_backend, init_method=args.dist_url,
                                    world_size=args.world_size, rank=args.rank)
    # create model
    if args.pretrained:
        print("[gpu id:",args.gpu,"]","=> using pre-trained model '{}'".format(args.arch))
        model = models.__dict__[args.arch](pretrained=True)
    else:
        print("[gpu id:",args.gpu,"]","=> creating model '{}'".format(args.arch))
        model = models.__dict__[args.arch]()

    print("[gpu id:",args.gpu,"]","===============main_worker()=================")
    print("[gpu id:",args.gpu,"]",args)
    print("[gpu id:",args.gpu,"]","===============main_worker()=================")
    nvidia_logger_init(args)
    #lr_scheduler = 0
    if args.distributed:
        # For multiprocessing distributed, DistributedDataParallel constructor
        # should always set the single device scope, otherwise,
        # DistributedDataParallel will use all available devices.
        if args.gpu is not None:
            if args.device == 'npu':
                loc = 'npu:{}'.format(args.gpu)
                torch.npu.set_device(loc)
                model = model.to(loc)
            else:
                torch.cuda.set_device(args.gpu)
                model.cuda(args.gpu)

            
            # When using a single GPU per process and per
            # DistributedDataParallel, we need to divide the batch size
            # ourselves based on the total number of GPUs we have
            args.batch_size = int(args.batch_size / ngpus_per_node)
            args.workers = int((args.workers + ngpus_per_node - 1) / ngpus_per_node)
            
            
            #model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[args.gpu])
        else:
            if args.device == 'npu':
                loc = 'npu:{}'.format(args.gpu)
                model = model.to(loc)
            else:
                model.cuda()
            # DistributedDataParallel will divide and allocate batch_size to all
            # available GPUs if device_ids are not set
            print("[gpu id:",args.gpu,"]","============================test   args.gpu is not None   else==========================")
            #model = torch.nn.parallel.DistributedDataParallel(model)
    elif args.gpu is not None:
        print("[gpu id:",args.gpu,"]","============================test   elif args.gpu is not None:==========================")
        if args.device == 'npu':
            loc = 'npu:{}'.format(args.gpu)
            torch.npu.set_device(args.gpu)
            model = model.to(loc)
        else:
            torch.cuda.set_device(args.gpu)
            model = model.cuda(args.gpu)

    else:
        # DataParallel will divide and allocate batch_size to all available GPUs
        print("[gpu id:",args.gpu,"]","============================test   1==========================")
        if args.arch.startswith('alexnet') or args.arch.startswith('vgg'):
            print("[gpu id:",args.gpu,"]","============================test   2==========================")
            #model.features = torch.nn.DataParallel(model.features)
            #model.cuda()
        else:
            print("[gpu id:",args.gpu,"]","============================test   3==========================")
            if args.device == 'npu':
                loc = 'npu:{}'.format(args.gpu)
                #model = torch.nn.DataParallel(model).to(loc)
            else:
                #model = torch.nn.DataParallel(model).cuda()
                print("before : model = torch.nn.DataParallel(model).cuda()")
            
    # optimizer = torch.optim.SGD(model.parameters(), args.lr,
    #                             momentum=args.momentum,
    #                             weight_decay=args.weight_decay)
    model_state = None
    optimizer_state = None
    optimizer = get_optimizer(list(model.named_parameters()),
                            args.fp16,
                            args.lr,
                            args.momentum,
                            args.weight_decay,
                            nesterov=args.nesterov,
                            bn_weight_decay=args.bn_weight_decay,
                            state=optimizer_state,
                            static_loss_scale=args.static_loss_scale,
                            dynamic_loss_scale=args.dynamic_loss_scale)
    lr_scheduler = nvidia_lr_policy(args)
    ###############################
    #混合精度
    #model, optimizer = amp.initialize(model, optimizer, opt_level="O1",loss_scale = 2.0,verbosity=1)
    model, optimizer = amp.initialize(model, optimizer, opt_level="O2",loss_scale = 1024,verbosity=1)
    #model, optimizer = amp.initialize(model, optimizer, opt_level="O1",verbosity=1)
    ###############################

    if args.distributed:
        # For multiprocessing distributed, DistributedDataParallel constructor
        # should always set the single device scope, otherwise,
        # DistributedDataParallel will use all available devices.
        if args.gpu is not None:
            # if args.device == 'npu':
            #     loc = 'npu:{}'.format(args.gpu)
            #     torch.npu.set_device(loc)
            #     model = model.to(loc)
            # else:
            #     torch.cuda.set_device(args.gpu)
            #     model.cuda(args.gpu)

            
            # When using a single GPU per process and per
            # DistributedDataParallel, we need to divide the batch size
            # ourselves based on the total number of GPUs we have
            # args.batch_size = int(args.batch_size / ngpus_per_node)
            # args.workers = int((args.workers + ngpus_per_node - 1) / ngpus_per_node)

            #model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[args.gpu])
            model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[args.gpu], broadcast_buffers=False)
            
        else:
            # if args.device == 'npu':
            #    loc = 'npu:{}'.format(args.gpu)
            #    model = model.to(loc)
            # else:
            #    model.cuda()
            # DistributedDataParallel will divide and allocate batch_size to all
            # available GPUs if device_ids are not set
            print("[gpu id:",args.gpu,"]","============================test   args.gpu is not None   else==========================")
            model = torch.nn.parallel.DistributedDataParallel(model)
    elif args.gpu is not None:
        print("[gpu id:",args.gpu,"]","============================test   elif args.gpu is not None:==========================")
        # if args.device == 'npu':
        #     loc = 'npu:{}'.format(args.gpu)
        #     torch.npu.set_device(args.gpu)
        #     model = model.to(loc)
        # else:
        #     torch.cuda.set_device(args.gpu)
        #     model = model.cuda(args.gpu)

    else:
        # DataParallel will divide and allocate batch_size to all available GPUs
        print("[gpu id:",args.gpu,"]","============================test   1==========================")
        if args.arch.startswith('alexnet') or args.arch.startswith('vgg'):
            print("[gpu id:",args.gpu,"]","============================test   2==========================")
            model.features = torch.nn.DataParallel(model.features)
            model.cuda()
        else:
            print("[gpu id:",args.gpu,"]","============================test   3==========================")
            if args.device == 'npu':
                loc = 'npu:{}'.format(args.gpu)
                model = torch.nn.DataParallel(model).to(loc)
            else:
                model = torch.nn.DataParallel(model).cuda()

    # define loss function (criterion) and optimizer
    if args.device == 'npu':
        loc = 'npu:{}'.format(args.gpu)
        criterion = nn.CrossEntropyLoss().to(loc)
    else:
        criterion = nn.CrossEntropyLoss().cuda(args.gpu)
    criterion = nvidia_mixup_and_label_smoothing_getlossfunction(args)#需增加设备类型参数(npu/gpu)
    print("criterion = nvidia_mixup_and_label_smoothing_getlossfunction(args)")
    # optionally resume from a checkpoint
    if args.resume:
        if os.path.isfile(args.resume):
            print("[gpu id:",args.gpu,"]","=> loading checkpoint '{}'".format(args.resume))
            if args.gpu is None:
                checkpoint = torch.load(args.resume)
            else:
                # Map model to be loaded to specified single gpu.
                if args.device == 'npu':
                    loc = 'npu:{}'.format(args.gpu)
                else:
                    loc = 'cuda:{}'.format(args.gpu)
                checkpoint = torch.load(args.resume, map_location=loc)
            args.start_epoch = checkpoint['epoch']
            best_acc1 = checkpoint['best_acc1']
            if args.gpu is not None:
                # best_acc1 may be from a checkpoint from a different GPU
                best_acc1 = best_acc1.to(args.gpu)
            model.load_state_dict(checkpoint['state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer'])
            print("[gpu id:",args.gpu,"]","=> loaded checkpoint '{}' (epoch {})"
                  .format(args.resume, checkpoint['epoch']))
        else:
            print("[gpu id:",args.gpu,"]","=> no checkpoint found at '{}'".format(args.resume))

    cudnn.benchmark = True

    # Data loading code
    traindir = os.path.join(args.data, 'train')
    valdir = os.path.join(args.data, 'val')
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    train_dataset = datasets.ImageFolder(
        traindir,
        transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ]))

    if args.distributed:
        train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset)
    else:
        train_sampler = None

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=(train_sampler is None),
        num_workers=args.workers, pin_memory=False, sampler=train_sampler, drop_last=True)

    val_loader = torch.utils.data.DataLoader(
        datasets.ImageFolder(valdir, transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            normalize,
        ])),
        batch_size=args.batch_size, shuffle=True,
        num_workers=args.workers, pin_memory=False, drop_last=True)

    if args.evaluate:
        validate(val_loader, model, criterion, args)
        return

    #if not args.multiprocessing_distributed or (args.multiprocessing_distributed
    #        and args.rank % ngpus_per_node == 0):
    #    pstxtpath = 'echo "=================================" >> "./ps/ps-before-epoch-0-`date \"+%Y%m%d-%H%M%S\"`.txt"'
    #    os.system(pstxtpath)
    #    pstxtpath = 'ps -aux |grep python >> "./ps/ps-before-epoch-0-`date \"+%Y%m%d-%H%M%S\"`.txt"'
    #    os.system(pstxtpath)
    #    print(pstxtpath)
    #    pstxtpath = 'echo "=================================" >> "./ps/ps-before-epoch-0-`date \"+%Y%m%d-%H%M%S\"`.txt"'
    #    os.system(pstxtpath)
    for epoch in range(args.start_epoch, args.epochs):
        if args.distributed:
            train_sampler.set_epoch(epoch)
        #adjust_learning_rate(optimizer, epoch, args)

        # train for one epoch
        #train(train_loader, model, criterion, optimizer, epoch, args,ngpus_per_node,
        acc1 = train(train_loader, model, criterion, optimizer, epoch, args,ngpus_per_node,
          lr_scheduler)
        #if not args.multiprocessing_distributed or (args.multiprocessing_distributed
        #        and args.rank % ngpus_per_node == 0):
            #os.system(' ps -aux |grep python > "ps-`date \"+%Y%m%d-%H%M%S\"`.txt"')
        #    pstxtpath = ' ps -aux |grep python >> "./ps/ps-epoch-'+str(epoch)+'-`date \"+%Y%m%d-%H%M%S\"`.txt"'
        #    os.system(pstxtpath)
        #    pstxtpath = ' echo "==============================" >> "./ps/ps-epoch-'+str(epoch)+'-`date \"+%Y%m%d-%H%M%S\"`.txt"'
        #    os.system(pstxtpath)
            #break
            
        # evaluate on validation set
        acc1 = validate(val_loader, model, criterion, args,ngpus_per_node)

        # remember best acc@1 and save checkpoint
        is_best = acc1 > best_acc1
        best_acc1 = max(acc1, best_acc1)
        
        if args.device == 'gpu':
            if not args.multiprocessing_distributed or (args.multiprocessing_distributed
                    and args.rank % ngpus_per_node == 0):
                save_checkpoint({
                    'epoch': epoch + 1,
                    'arch': args.arch,
                    'state_dict': model.state_dict(),
                    'best_acc1': best_acc1,
                    'optimizer' : optimizer.state_dict(),
                }, is_best)
        elif args.device == 'npu':
            #保存恢复点
            if (not args.multiprocessing_distributed or (args.multiprocessing_distributed
                   and args.rank % ngpus_per_node == 0 and epoch == args.epochs - 1) ):
                #单P情况，每个epoch均保存checkpoint文件
                #多P情况，仅最后一个epoch，保存rank 0的checkpoint文件 

                filename = args.checkpoint_nameprefix + ".pth.tar"

                #print("=================begin save checkpoint======================")
                #modeltmp = model
                #modeltmp = modeltmp.to("cpu")
                modeltmp = model.cpu()
                #保留最后一个epoch的checkpoint，防止异常退出
                save_checkpoint({
                    'epoch': epoch + 1,
                    'arch': args.arch,
                    'state_dict': modeltmp.state_dict(),
                    #'state_dict': model,
                    'best_acc1': best_acc1.to("cpu"),
                    #'optimizer' : optimizer.state_dict(),
                }, is_best.to("cpu"),filename=filename)                
                
                if (epoch == (args.epochs - 1)) or ((args.checkpoint_freq > 0) and (((epoch+1) % args.checkpoint_freq) == 0)):
                    #保留每个freq的checkpoint，共epochs/freq个checkpoint文件
                    #最后一个epoch保存独立的checkpoint文件
                    #每隔freq个epoch保存一个checkpoint文件
                    filename=args.checkpoint_nameprefix + "-epoch"+str(epoch) + ".pth.tar"
                    save_checkpoint({
                        'epoch': epoch + 1,
                        'arch': args.arch,
                        'state_dict': modeltmp.state_dict(),
                        #'state_dict': model,
                        'best_acc1': best_acc1.to("cpu"),
                        #'optimizer' : optimizer.state_dict(),
                    }, is_best.to("cpu"),filename=filename)


                loc = 'npu:{}'.format(args.gpu)
                modeltmp.to(loc)
                #print("=================end save checkpoint======================")
        

def train(train_loader, model, criterion, optimizer, epoch, args,ngpus_per_node,
          lr_scheduler):
    batch_time = AverageMeter('Time', ':6.3f')
    data_time = AverageMeter('Data', ':6.3f')
    losses = AverageMeter('Loss', ':6.4f')
    top1 = AverageMeter('Acc@1', ':6.2f')
    top5 = AverageMeter('Acc@5', ':6.2f')
    progress = ProgressMeter(
        len(train_loader),
        [batch_time, data_time, losses, top1, top5],
        prefix="Epoch: [{}]".format(epoch))

    # switch to train mode
    model.train()

    end = time.time()
    
    if args.benchmark == 1 :
        optimizer.zero_grad()
    for i, (images, target) in enumerate(train_loader):
        # measure data loading time
        data_time.update(time.time() - end)

        lr_scheduler(optimizer, i, epoch)

        if args.device == 'npu':
            loc = 'npu:{}'.format(args.gpu)
            target = target.to(torch.int32).to(loc, non_blocking=False)
            images = images.to(loc, non_blocking=False)
        else:
            images = images.cuda(args.gpu, non_blocking=False)
            target = target.cuda(args.gpu, non_blocking=False)

        # compute output
        output = model(images)

        #if not args.multiprocessing_distributed or (args.multiprocessing_distributed
        #            and args.rank % ngpus_per_node == 0):
        #    print("before:loss = criterion(output, target)")

        loss = criterion(output, target)

        #if not args.multiprocessing_distributed or (args.multiprocessing_distributed
        #            and args.rank % ngpus_per_node == 0):
        #    print("behind:loss = criterion(output, target)")

        # measure accuracy and record loss
        acc1, acc5 = accuracy(output, target, topk=(1, 5))
        losses.update(loss.item(), images.size(0))
        top1.update(acc1[0], images.size(0))
        top5.update(acc5[0], images.size(0))

        # compute gradient and do SGD step
        if args.benchmark == 0 :
            optimizer.zero_grad()

        with amp.scale_loss(loss, optimizer) as scaled_loss:
            scaled_loss.backward()

        if args.benchmark == 0 :
            optimizer.step()
        elif args.benchmark == 1 :
            BATCH_SIZE_multiplier = int(OPTIMIZER_BATCH_SIZE / args.batch_size)
            BM_optimizer_step = ((i + 1) % BATCH_SIZE_multiplier) == 0
            if BM_optimizer_step:
                #print("==================exec step & zero_grad===================")
                for param_group in optimizer.param_groups:
                    for param in param_group['params']:
                        param.grad /= BATCH_SIZE_multiplier
                optimizer.step()
                optimizer.zero_grad()
        
        # torch.npu.synchronize()
        # measure elapsed time
        batch_time.update(time.time() - end)
        end = time.time()

        if i % args.print_freq == 0:
            if not args.multiprocessing_distributed or (args.multiprocessing_distributed
                    and args.rank % ngpus_per_node == 0):
                    progress.display(i)

    if not args.multiprocessing_distributed or (args.multiprocessing_distributed
            and args.rank % ngpus_per_node == 0):
        print("[npu id:",args.gpu,"]", "batch_size:", ngpus_per_node*args.batch_size, 'Time: {:.3f}'.format(batch_time.avg), '* FPS@all {:.3f}'.format(
                ngpus_per_node*args.batch_size/batch_time.avg))
        hwlog.remark_print(key=hwlog.FPS, value=' * FPS@all {:.3f}'.format(ngpus_per_node * args.batch_size / batch_time.avg))
    return top1.avg


def validate(val_loader, model, criterion, args,ngpus_per_node):
    batch_time = AverageMeter('Time', ':6.3f')
    losses = AverageMeter('Loss', ':6.4f')
    top1 = AverageMeter('Acc@1', ':6.2f')
    top5 = AverageMeter('Acc@5', ':6.2f')
    progress = ProgressMeter(
        len(val_loader),
        [batch_time, losses, top1, top5],
        prefix='Test: ')

    # switch to evaluate mode
    model.eval()

    with torch.no_grad():
        end = time.time()
        for i, (images, target) in enumerate(val_loader):
            if args.gpu is not None:
                if args.device == 'npu':
                    loc = 'npu:{}'.format(args.gpu)
                    images = images.to(loc)
                else:
                    images = images.cuda(args.gpu, non_blocking=True)
            if args.device == 'npu':
                loc = 'npu:{}'.format(args.gpu)
                target = target.to(torch.int32).to(loc, non_blocking=True)
            else:
                target = target.cuda(args.gpu, non_blocking=True)

            # compute output
            output = model(images)
            loss = criterion(output, target)
            target = target.to(torch.int32).to(loc, non_blocking=True)
            # measure accuracy and record loss
            acc1, acc5 = accuracy(output, target, topk=(1, 5))
            losses.update(loss.item(), images.size(0))
            top1.update(acc1[0], images.size(0))
            top5.update(acc5[0], images.size(0))

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % args.print_freq == 0:
                if not args.multiprocessing_distributed or (args.multiprocessing_distributed
                        and args.rank % ngpus_per_node == 0):
                        progress.display(i)

        # TODO: this should also be done with the ProgressMeter
        if i % args.print_freq == 0:
            if not args.multiprocessing_distributed or (args.multiprocessing_distributed
                    and args.rank % ngpus_per_node == 0):
                print("[gpu id:",args.gpu,"]",'[AVG-ACC] * Acc@1 {top1.avg:.3f} Acc@5 {top5.avg:.3f}'
                        .format(top1=top1, top5=top5))
                hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP1, value="{top1.avg:.3f}".format(top1=top1))
                hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP5, value="{top5.avg:.3f}".format(top5=top5))

    return top1.avg


def save_checkpoint(state, is_best, filename='checkpoint.pth.tar'):
    torch.save(state, filename)
    if is_best:
        shutil.copyfile(filename, 'model_best.pth.tar')


class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self, name, fmt=':f'):
        self.name = name
        self.fmt = fmt
        self.reset()
        self.start_count_index = 10

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.count += n
        if self.count > (self.start_count_index * n):
            self.sum += val * n
            self.avg = self.sum / (self.count - self.start_count_index * n)

    def __str__(self):
        fmtstr = '{name} {val' + self.fmt + '} ({avg' + self.fmt + '})'
        return fmtstr.format(**self.__dict__)


class ProgressMeter(object):
    def __init__(self, num_batches, meters, prefix=""):
        self.batch_fmtstr = self._get_batch_fmtstr(num_batches)
        self.meters = meters
        self.prefix = prefix

    def display(self, batch):
        entries = [self.prefix + self.batch_fmtstr.format(batch)]
        entries += [str(meter) for meter in self.meters]
        print("[gpu id:",os.environ['KERNEL_NAME_ID'],"]",'\t'.join(entries))

    def _get_batch_fmtstr(self, num_batches):
        num_digits = len(str(num_batches // 1))
        fmt = '{:' + str(num_digits) + 'd}'
        return '[' + fmt + '/' + fmt.format(num_batches) + ']'


def adjust_learning_rate(optimizer, epoch, args):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    lr = args.lr * (0.1 ** (epoch // 30))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


def accuracy(output, target, topk=(1,)):
    """Computes the accuracy over the k top predictions for the specified values of k"""
    with torch.no_grad():
        maxk = max(topk)
        batch_size = target.size(0)

        _, pred = output.topk(maxk, 1, True, True)
        pred = pred.t()
        correct = pred.eq(target.view(1, -1).expand_as(pred))

        res = []
        for k in topk:
            correct_k = correct[:k].view(-1).float().sum(0, keepdim=True)
            res.append(correct_k.mul_(100.0 / batch_size))
        return res


if __name__ == '__main__':
    hwlog.ROOT_DIR = os.path.split(os.path.abspath(__file__))[0]
    cpu_info, npu_info, framework_info, os_info, benchmark_version = get_environment_info("pytorch")
    config_info = get_model_parameter("pytorch_config")
    initinal_data = {"base_lr": 0.1, "dataset": "imagenet", "optimizer": "SGD", "loss_scale": 1024}
    hwlog.remark_print(key=hwlog.CPU_INFO, value=cpu_info)
    hwlog.remark_print(key=hwlog.NPU_INFO, value=npu_info)
    hwlog.remark_print(key=hwlog.OS_INFO, value=os_info)
    hwlog.remark_print(key=hwlog.FRAMEWORK_INFO, value=framework_info)
    hwlog.remark_print(key=hwlog.BENCHMARK_VERSION, value=benchmark_version)
    hwlog.remark_print(key=hwlog.CONFIG_INFO, value=config_info)
    hwlog.remark_print(key=hwlog.BASE_LR, value=initinal_data.get("base_lr"))
    hwlog.remark_print(key=hwlog.DATASET, value=initinal_data.get("dataset"))
    hwlog.remark_print(key=hwlog.OPT_NAME, value=initinal_data.get("optimizer"))
    hwlog.remark_print(key=hwlog.LOSS_SCALE, value=initinal_data.get("loss_scale"))
    main()

