import sys
import os
import numpy as np
import random
import math

import torch
import torch.optim as optim
import torchvision.transforms as transforms
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from torch.nn.parallel import DataParallel
import pickle
import time
import argparse
import pdb
import sys
from torch.utils.tensorboard import SummaryWriter

from baseline.dataset import add_transforms
from baseline.dataset.Dataset import AttDataset
from baseline.model.DeepMAR import DeepMAR_ResNet50
from baseline.model.DeepMAR import DeepMAR_ResNet50_ExtractFeature 
from baseline.utils.evaluate import attribute_evaluate
from baseline.utils.utils import str2bool
from baseline.utils.utils import transfer_optim_state
from baseline.utils.utils import time_str
from baseline.utils.utils import save_ckpt, load_ckpt
from baseline.utils.utils import load_state_dict 
from baseline.utils.utils import ReDirectSTD
from baseline.utils.utils import adjust_lr_staircase
from baseline.utils.utils import adjust_lr
from baseline.utils.utils import set_devices
from baseline.utils.utils import AverageMeter
from baseline.utils.utils import to_scalar 
from baseline.utils.utils import may_set_mode 
from baseline.utils.utils import may_mkdir 
from baseline.utils.utils import set_seed
from baseline.utils.utils import seed_everything

# Apex
import numpy as np
from apex import amp
import torch.npu

from benchmark_log import hwlog
from benchmark_log.basic_utils import get_environment_info
from benchmark_log.basic_utils import get_model_parameter

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

CALCULATE_DEVICE = "npu:7"
PRINT_DEVICE = "cpu"

class Config(object):
    def __init__(self):
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--npu', type=int, default=0, help='NPU id to use.')
        parser.add_argument('--set_seed', type=str2bool, default=False)
        ## dataset parameter
        parser.add_argument('--dataset', type=str, default='peta',
                choices=['peta','rap', 'pa100k', 'rap2'])
        parser.add_argument('--save_dir', type=str, default='/home/zhusiyi/dataset/peta/')
        parser.add_argument('--split', type=str, default='trainval',
                            choices=['trainval', 'train'])
        parser.add_argument('--test_split', type=str, default='test')
        parser.add_argument('--partition_idx', type=int, default=0)
        parser.add_argument('--resize', type=eval, default=(224, 224))
        parser.add_argument('--mirror', type=str2bool, default=True)
        parser.add_argument('--batch_size', type=int, default=32)
        parser.add_argument('--workers', type=int, default=2)
        # model
        parser.add_argument('--num_att', type=int, default=35)
        parser.add_argument('--pretrained', type=str2bool, default=True)
        parser.add_argument('--last_conv_stride', type=int, default=2, choices=[1,2])
        parser.add_argument('--drop_pool5', type=str2bool, default=True)
        parser.add_argument('--drop_pool5_rate', type=float, default=0.5)

        parser.add_argument('--sgd_weight_decay', type=float, default=0.0005)
        parser.add_argument('--sgd_momentum', type=float, default=0.9)
        parser.add_argument('--new_params_lr', type=float, default=0.001)
        parser.add_argument('--finetuned_params_lr', type=float, default=0.001)
        parser.add_argument('--staircase_decay_at_epochs', type=eval,
                            default=(51, ))
        parser.add_argument('--staircase_decay_multiple_factor', type=float,
                            default=0.1)
        parser.add_argument('--total_epochs', type=int, default=150)
        parser.add_argument('--weighted_entropy', type=str2bool, default=True)
        # utils
        parser.add_argument('--resume', type=str2bool, default=False)
        parser.add_argument('--ckpt_file', type=str, default='')
        parser.add_argument('--load_model_weight', type=str2bool, default=False)
        parser.add_argument('--model_weight_file', type=str, default='')
        parser.add_argument('--test_only', type=str2bool, default=False)
        parser.add_argument('--exp_dir', type=str, default='')
        parser.add_argument('--exp_subpath', type=str, default='deepmar_resnet50')
        parser.add_argument('--log_to_file', type=str2bool, default=True)
        parser.add_argument('--steps_per_log', type=int, default=20)
        parser.add_argument('--epochs_per_val', type=int, default=10)
        parser.add_argument('--epochs_per_save', type=int, default=50)
        parser.add_argument('--run', type=int, default=1)
        # apex
        parser.add_argument('--amp', default=False, action='store_true',
                            help='use amp to train the model')
        parser.add_argument('--loss_scale', default=-1., type=float,
                            help='loss scale using in amp, default -1 means dynamic')
        parser.add_argument('--opt_level', default='O1', type=str,
                            help='opt level using in amp, default O1 means FP16')
        args = parser.parse_args()
        
        # gpu ids
        self.npu = args.npu
        # random
        self.set_seed = args.set_seed
        if self.set_seed:
            self.seed = 0
        else: 
            self.seed = None
        # amp
        self.amp = args.amp
        self.loss_scale = args.loss_scale
        self.opt_level = args.opt_level
        # run time index
        self.run = args.run
        # Dataset #
        datasets = dict()
        #datasets['peta'] = '/home/zhusiyi/dataset/peta/peta_dataset.pkl'
        #datasets['peta'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),'dataset/peta/peta_dataset.pkl')
        datasets['peta'] =  args.save_dir + '/peta_dataset.pkl'
        partitions = dict()
        #partitions['peta'] = '/home/zhusiyi/dataset/peta/peta_partition.pkl'
        #partitions['peta'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),'dataset/peta/peta_partition.pkl')
        partitions['peta'] = args.save_dir + '/peta_partition.pkl'
        
        self.dataset_name = args.dataset
        if args.dataset not in datasets  or args.dataset not in partitions:
            print ("Please select the right dataset name.")
            raise ValueError
        else:
            self.dataset = datasets[args.dataset]
            self.partition = partitions[args.dataset]
        self.partition_idx = args.partition_idx
        self.split = args.split
        self.test_split = args.test_split
        self.resize = args.resize
        self.mirror = args.mirror
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        self.batch_size = args.batch_size
        self.workers = args.workers
        # optimization
        self.sgd_momentum = args.sgd_momentum
        self.sgd_weight_decay = args.sgd_weight_decay
        self.new_params_lr = args.new_params_lr
        self.finetuned_params_lr = args.finetuned_params_lr
        self.staircase_decay_at_epochs = args.staircase_decay_at_epochs
        self.staircase_decay_multiple_factor = args.staircase_decay_multiple_factor
        self.total_epochs = args.total_epochs
        self.weighted_entropy = args.weighted_entropy

        # utils
        self.resume = args.resume
        self.ckpt_file = args.ckpt_file
        if self.resume:
            if self.ckpt_file == '':
                print ('Please input the ckpt_file if you want to resume training')
                raise ValueError
        self.load_model_weight = args.load_model_weight
        self.model_weight_file = args.model_weight_file
        if self.load_model_weight:
            if self.model_weight_file == '':
                print ('Please input the model_weight_file if you want to load model weight')
                raise ValueError
        self.test_only = args.test_only
        self.exp_dir = args.exp_dir
        self.exp_subpath = args.exp_subpath
        self.log_to_file = args.log_to_file
        self.steps_per_log = args.steps_per_log
        self.epochs_per_val = args.epochs_per_val
        self.epochs_per_save = args.epochs_per_save
        self.run = args.run
        
        # for model
        model_kwargs = dict()
        model_kwargs['num_att'] = args.num_att
        model_kwargs['last_conv_stride'] = args.last_conv_stride
        model_kwargs['drop_pool5'] = args.drop_pool5
        model_kwargs['drop_pool5_rate'] = args.drop_pool5_rate
        self.model_kwargs = model_kwargs
        # for evaluation
        self.test_kwargs = dict()

        if self.exp_dir == '':
            self.exp_dir = os.path.join('exp',
                '{}'.format(self.exp_subpath),
                '{}'.format(self.dataset_name),
                'partition{}'.format(self.partition_idx),
                'run{}'.format(self.run))
        self.stdout_file = os.path.join(self.exp_dir, \
            'log', 'stdout_{}.txt'.format(time_str()))
        self.stderr_file = os.path.join(self.exp_dir, \
            'log', 'stderr_{}.txt'.format(time_str()))
        may_mkdir(self.stdout_file)

### main function ###
cfg = Config()

# log
if cfg.log_to_file:
    ReDirectSTD(cfg.stdout_file, 'stdout', False)
    ReDirectSTD(cfg.stderr_file, 'stderr', False)

# dump the configuration to log.
import pprint
print('-' * 60)
print('cfg.__dict__')
pprint.pprint(cfg.__dict__)
print('-' * 60)

# set the random seed
print(cfg.seed)
if cfg.set_seed:
    set_seed(cfg.seed)
    seed_everything(cfg.seed)

# init the npu ids
CALCULATE_DEVICE = "npu:{}".format(cfg.npu)
torch.npu.set_device(CALCULATE_DEVICE)

# dataset 
normalize = transforms.Normalize(mean=cfg.mean, std=cfg.std)
transform = transforms.Compose([
        transforms.Resize(cfg.resize),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(), # 3*H*W, [0, 1]
        normalize,]) # normalize with mean/std
# by a subset of attributes 
train_set = AttDataset(
    dataset = cfg.dataset, 
    partition = cfg.partition,
    split = cfg.split,
    partition_idx= cfg.partition_idx,
    transform = transform)

num_att = len(train_set.dataset['selected_attribute'])
cfg.model_kwargs['num_att'] = num_att

train_loader = torch.utils.data.DataLoader(
    dataset = train_set,
    batch_size = cfg.batch_size,
    shuffle = True,
    num_workers = cfg.workers,
    pin_memory = True,
    drop_last = True)

test_transform = transforms.Compose([
        transforms.Resize(cfg.resize),
        transforms.ToTensor(),
        normalize,])

test_set = AttDataset(
    dataset = cfg.dataset,
    partition = cfg.partition,
    split = cfg.test_split,
    partition_idx = cfg.partition_idx,
    transform = test_transform)

### Att model ###
model = DeepMAR_ResNet50(**cfg.model_kwargs)

# Optimizer
finetuned_params = []
new_params = []
for n, p in model.named_parameters():
    if n.find('classifier') >=0:
        new_params.append(p)
    else:
        finetuned_params.append(p)
param_groups = [{'params': finetuned_params, 'lr': cfg.finetuned_params_lr},
                {'params': new_params, 'lr': cfg.new_params_lr}]

optimizer = optim.SGD(
    param_groups,
    momentum = cfg.sgd_momentum,
    weight_decay = cfg.sgd_weight_decay)

model = model.to(CALCULATE_DEVICE)
# apex
if cfg.amp:
    # Initialization
    model, optimizer = amp.initialize(model, optimizer, opt_level=cfg.opt_level, loss_scale=cfg.loss_scale)
    print("=> Using amp mode.")


# using the weighted cross entropy loss
if cfg.weighted_entropy:
    rate = np.array(train_set.partition['weight_' + cfg.split][cfg.partition_idx])
    rate = rate[train_set.dataset['selected_attribute']].tolist()
else:
    rate = None
# compute the weight of positive and negative
if rate is None:
    weight_pos = [1 for i in range(num_att)]
    weight_neg = [1 for i in range(num_att)]
else:
    if len(rate) != num_att:
        print ("the length of rate should be equal to %d" % (num_att))
        raise ValueError
    weight_pos = []
    weight_neg = []
    for idx, v in enumerate(rate):
        weight_pos.append(math.exp(1.0 - v))
        weight_neg.append(math.exp(v))

# bind the model and optimizer
modules_optims = [model, optimizer]

# load model weight if necessary
if cfg.load_model_weight:
    map_location = (lambda storage, loc:storage)
    ckpt = torch.load(cfg.model_weight_file, map_location=map_location)
    model.load_state_dict(ckpt['state_dicts'][0], strict=False)
    # print(ckpt['state_dicts'][0])

### Resume or not ###
if cfg.resume:
    # store the model, optimizer, epoch 
    start_epoch, scores = load_ckpt(modules_optims, cfg.ckpt_file)
else:
    start_epoch = 0

model = torch.nn.DataParallel(model)
# model_w.cuda()
transfer_optim_state(state=optimizer.state, device_id=cfg.npu)

# cudnn.benchmark = True
# for evaluation
feat_func_att = DeepMAR_ResNet50_ExtractFeature(model=model)

def attribute_evaluate_subfunc(feat_func, test_set, device_id, **test_kwargs):
    """ evaluate the attribute recognition precision """
    result = attribute_evaluate(feat_func, test_set, device_id, **test_kwargs)
    print ('-' * 60)
    print ('Evaluation on %s set:' % (cfg.test_split))
    print ('Label-based evaluation: \n mA: %.4f'%(np.mean(result['label_acc'])))
    print ('Instance-based evaluation: \n Acc: %.4f, Prec: %.4f, Rec: %.4f, F1: %.4f' \
        %(result['instance_acc'], result['instance_precision'], result['instance_recall'], result['instance_F1']))
    print ('-' * 60)
    hwlog.remark_print(key=hwlog.ACC, value="{:.4f}".format(result['instance_acc']))
    hwlog.remark_print(key=hwlog.PREC, value="{:.4f}".format(result['instance_precision']))
    hwlog.remark_print(key=hwlog.REC, value="{:.4f}".format(result['instance_recall']))
    hwlog.remark_print(key=hwlog.F1, value="{:.4f}".format(result['instance_recall']))
    return result['instance_acc']


# print the model into log
# test only
if cfg.test_only:
    print ('test with feat_func_att')
    attribute_evaluate_subfunc(feat_func_att, test_set, **cfg.test_kwargs)
    sys.exit(0)


# writer = SummaryWriter(os.path.join('runs/deepmar', str(cfg.npu)))

# training
for epoch in range(start_epoch, cfg.total_epochs):
    if cfg.seed is not None:
        cfg.seed += 1
        seed_everything(cfg.seed)
    # adjust the learning rate
    adjust_lr_staircase(
        optimizer.param_groups,
        [cfg.finetuned_params_lr, cfg.new_params_lr],
        epoch + 1,
        cfg.staircase_decay_at_epochs,
        cfg.staircase_decay_multiple_factor)
    # adjust_lr(optimizer,epoch+1,cfg.finetuned_params_lr)n
    
    may_set_mode(modules_optims, 'train')
    # recording loss
    loss_meter = AverageMeter()
    dataset_L = len(train_loader) # crop batch data
    ep_st = time.time()
    ep_st_mark=ep_st
    # runing every batch data
    for step, (imgs, targets) in enumerate(train_loader):

        step_st = time.time()
        # measure data loading time
        data_time = step_st-ep_st

        imgs_var = Variable(imgs)
        targets_var = Variable(targets)

        # compute the weight
        weights = torch.zeros(targets_var.shape)
        for i in range(targets_var.shape[0]):
            for j in range(targets_var.shape[1]):
                if targets_var.data.cpu()[i, j] == -1:
                    weights[i, j] = weight_neg[j]
                elif targets_var.data.cpu()[i, j] == 1:
                    weights[i, j] = weight_pos[j]
                else:
                    weights[i, j] = 0

        targets_var[targets_var == -1] = 0
        targets_var = targets_var.to(CALCULATE_DEVICE)
        imgs_var = imgs_var.to(CALCULATE_DEVICE)
        weights = weights.to(CALCULATE_DEVICE)
        score = model(imgs_var)

        criterion = torch.nn.BCEWithLogitsLoss(weight=Variable(weights)).to(CALCULATE_DEVICE)
        loss = criterion(score, targets_var) * num_att
        optimizer.zero_grad()
        if cfg.amp:
            with amp.scale_loss(loss, optimizer) as scaled_loss:
                scaled_loss.backward()
        else:
            loss.backward()

        optimizer.step()


        ############
        # step log #
        ############
        loss_meter.update(to_scalar(loss))
        # one batch time using backward calculation
        batch_time = time.time() - ep_st  # include data load time
        ep_st = time.time()
        fps = cfg.batch_size / batch_time
        # do not include data load time

        if (step + 1) % cfg.steps_per_log == 0 or (step + 1) % len(train_loader) == 0:
            log = '{}, Step {}/{} in Ep {}, {:.2f}s, datatime:{:.6f}, batchtime:{:.6f},  FPS:{:.2f}, loss:{:.4f}'.format( \
            time_str(), step + 1, dataset_L, epoch + 1, time.time() - step_st, data_time, batch_time, fps, loss_meter.val)

            print(log)

            hwlog.remark_print(key=hwlog.FPS, value='{:.2f}'.format(fps))

    ##############
    # epoch log  #
    ##############
    epoch_time = time.time() - ep_st_mark
    log = 'Ep{}, {:.2f}s, loss {:.4f}'.format(
        epoch+1, epoch_time, loss_meter.avg)
    print(log)

    # writer.add_scalar('Train/Time', epoch_time, epoch+1)
    # writer.add_scalar('Train/Loss', loss_meter.avg, epoch+1)
    # writer.add_scalar('Train/LR', optimizer.param_groups[0]['lr'], epoch+1)


    # model ckpt
    if (epoch + 1) % cfg.epochs_per_save == 0 or epoch+1 == cfg.total_epochs:
        ckpt_file = os.path.join(cfg.exp_dir, 'model', 'ckpt_epoch%d.pth'%(epoch+1))
        save_ckpt(modules_optims, epoch+1, 0, ckpt_file)

    ##########################
    # test on validation set #
    ##########################
    if (epoch + 1) % cfg.epochs_per_val == 0 or epoch+1 == cfg.total_epochs:
        print ('att test with feat_func_att')
        res = attribute_evaluate_subfunc(feat_func_att, test_set, CALCULATE_DEVICE, **cfg.test_kwargs)

        # writer.add_scalar('Val/Acc', res, epoch)