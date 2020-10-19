import argparse
import os
import random
import shutil
import time
import warnings

import torch
import torch.nn as nn
import torch.nn.functional as F
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
from mobilenet import mobilenet_v2
import torch.npu
import torch.cuda

from torch.utils.tensorboard import SummaryWriter

from apex import amp
import numpy as np

from hook import *


# model_names = sorted(name for name in models.__dict__
#     if name.islower() and not name.startswith("__")
#     and callable(models.__dict__[name]))

parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
parser.add_argument('--data', metavar='DIR', default='/dataset/imagenet',
                    help='path to dataset')
# parser.add_argument('-a', '--arch', metavar='ARCH', default='resnet18',
#                     choices=model_names,
#                     help='model architecture: ' +
#                         ' | '.join(model_names) +
#                         ' (default: resnet18)')
parser.add_argument('-j', '--workers', default=4, type=int, metavar='N',
                    help='number of data loading workers (default: 4)')
parser.add_argument('--epochs', default=90, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--start-epoch', default=0, type=int, metavar='N',
                    help='manual epoch number (useful on restarts)')
parser.add_argument('-b', '--batch-size', default=256, type=int,
                    metavar='N',
                    help='mini-batch size (default: 256), this is the total '
                         'batch size of all GPUs on the current node when '
                         'using Data Parallel or Distributed Data Parallel')
parser.add_argument('--lr', '--learning-rate', default=0.1, type=float,
                    metavar='LR', help='initial learning rate', dest='lr')
parser.add_argument('--momentum', default=0.9, type=float, metavar='M',
                    help='momentum')
parser.add_argument('--wd', '--weight-decay', default=1e-4, type=float,
                    metavar='W', help='weight decay (default: 1e-4)',
                    dest='weight_decay')
parser.add_argument('-p', '--print-freq', default=10, type=int,
                    metavar='N', help='print frequency (default: 10)')
parser.add_argument('--resume', default='', type=str, metavar='PATH',
                    help='path to latest checkpoint (default: none)')
parser.add_argument('-e', '--evaluate', dest='evaluate', action='store_true',
                    help='evaluate model on validation set')
parser.add_argument('--pretrained', dest='pretrained', action='store_true',
                    help='use pre-trained model')
# parser.add_argument('--world-size', default=-1, type=int,
#                     help='number of nodes for distributed training')
parser.add_argument('--node-nums', default=1, type=int,
                    help='number of nodes for distributed training')
parser.add_argument('--rank', default=0, type=int,
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

parser.add_argument('--addr', default='10.136.181.115', type=str,
                    help='master addr')
parser.add_argument('--device-id', default=None, type=int,
                    help='GPU id to use.')

parser.add_argument('--amp', default=False, action='store_true',
                    help='use amp to train the model')
parser.add_argument('--opt-level', default=None, type=str, help='apex optimize level')
parser.add_argument('--loss-scale-value', default='1024', type=int, help='static loss scale value')

parser.add_argument('--summary-path', default=None, type=str, help='event file path')
parser.add_argument('--stop-step-num', default=None, type=int, help='after the stop-step, killing the training task')
parser.add_argument('--device', default='npu', type=str, help='device type, cpu or npu:x or cuda')
parser.add_argument('--eval-freq', default=10, type=int, help='test interval')
parser.add_argument('--hook', default=False, action='store_true', help='pytorch hook')

best_acc1 = 0
cur_step = 0


def seed_everything(seed, device):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if 'cuda' in device:
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        cudnn.deterministic = True
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def main():
    args = parser.parse_args()

    if args.seed is not None:
        seed_everything(args.seed, args.device)

        warnings.warn('You have chosen to seed training. '
                      'This will turn on the CUDNN deterministic setting, '
                      'which can slow down your training considerably! '
                      'You may see unexpected behavior when restarting '
                      'from checkpoints.')

    os.environ['MASTER_ADDR'] = args.addr
    os.environ['MASTER_PORT'] = '90000'

    args.distributed = args.node_nums > 1 or args.multiprocessing_distributed
    if not args.distributed:
        print('dist param is not correct!')
        return

    if args.device == 'npu':
        # device_nums_per_node = torch.npu.device_count()
        device_nums_per_node = 2
    elif args.device == 'cuda':
        device_nums_per_node = torch.cuda.device_count()
    else:
        print('unknown device type[npu/cuda]!')
        return

    if args.multiprocessing_distributed:
        args.world_size = device_nums_per_node * args.node_nums  # world_size means nums of all devices or nums of processes
        if args.device == 'npu':
            # main_worker(args.device_id, ngpus_per_node, args)  # 需要外层脚本启多个进程
            mp.spawn(main_worker, nprocs=device_nums_per_node, args=(device_nums_per_node, args))  # 这里起子进程，就不需要外层脚本启多个进程了
        else:
            mp.spawn(main_worker, nprocs=device_nums_per_node, args=(device_nums_per_node, args))
    else:
        print('dist param is not correct!')
        return
        # main_worker(args.device_id, device_nums_per_node, args)


# first param must be the index of PID
def main_worker(pid_idx, device_nums_per_node, args):
    global best_acc1
    global cur_step

    # dist set
    sum_writer = SummaryWriter(args.summary_path)
    global_step = -1

    if args.distributed:
        if args.multiprocessing_distributed:
            # For multiprocessing distributed training, rank needs to be the
            # global rank among all the processes
            args.rank = pid_idx  # args.rank * device_nums_per_node + pid_idx
            args.pid_idx = pid_idx

        if args.device == 'npu':
            dist.init_process_group(backend=args.dist_backend, world_size=args.world_size, rank=args.rank)
        else:
            dist.init_process_group(backend=args.dist_backend, init_method=args.dist_url,
                                    world_size=args.world_size, rank=args.rank)

    if args.distributed:
        # For multiprocessing distributed, DistributedDataParallel constructor
        # should always set the single device scope, otherwise,
        # DistributedDataParallel will use all available devices.
        if args.device == 'npu':
            loc = 'npu:{}'.format(pid_idx)
            torch.npu.set_device(loc)
        else:
            torch.cuda.set_device(pid_idx)

        args.batch_size = int(args.batch_size / device_nums_per_node)
        args.workers = int((args.workers + device_nums_per_node - 1) / device_nums_per_node)

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
        num_workers=args.workers, pin_memory=True, sampler=train_sampler, drop_last=True)

    val_loader = torch.utils.data.DataLoader(
        datasets.ImageFolder(valdir, transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            normalize,
        ])),
        batch_size=args.batch_size, shuffle=False,
        num_workers=args.workers, pin_memory=True, drop_last=True)

    # define model and train
    model = mobilenet_v2()

    criterion = nn.CrossEntropyLoss()

    loc = None
    if 'npu' == args.device:
        loc = 'npu:{}'.format(pid_idx)
    elif 'cuda' == args.device:
        loc = 'cuda:{}'.format(pid_idx)
    model = model.to(loc)

    criterion = criterion.to(loc)

    optimizer = torch.optim.SGD(model.parameters(), args.lr, momentum=args.momentum, weight_decay=args.weight_decay)

    if args.amp:
        model, optimizer = amp.initialize(model, optimizer, opt_level=args.opt_level, loss_scale=args.loss_scale_value)

    model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[pid_idx], broadcast_buffers=False)
    # model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)

    # set hook
    if args.hook:
        modules = model.named_modules()
        for name, module in modules:
            module.register_forward_hook(forward_hook_fn)
            module.register_backward_hook(backward_hook_fn)

    # optionally resume from a checkpoint
    if args.resume:
        if os.path.isfile(args.resume):
            print("=> loading checkpoint '{}'".format(args.resume))
            checkpoint = torch.load(args.resume, map_location=args.device)
            args.start_epoch = checkpoint['epoch']
            best_acc1 = checkpoint['best_acc1']
            model.load_state_dict(checkpoint['state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer'])
            if args.amp:
                amp.load_state_dict(checkpoint['amp'])
            print("=> loaded checkpoint '{}' (epoch {})"
                  .format(args.resume, checkpoint['epoch']))
        else:
            print("=> no checkpoint found at '{}'".format(args.resume))

    if args.evaluate:
        validate(val_loader, model, criterion, args, global_step, sum_writer)
        return

    for epoch in range(args.start_epoch, args.epochs):

        # train for one epoch
        global_step = train(train_loader, model, criterion, optimizer, epoch, args, global_step, sum_writer, device_nums_per_node)

        if (epoch + 1) % args.eval_freq == 0 or epoch == args.epochs - 1:
            # evaluate on validation set
            acc1 = validate(val_loader, model, criterion, args, global_step, sum_writer, device_nums_per_node)

            # remember best acc@1 and save checkpoint
            is_best = acc1 > best_acc1
            best_acc1 = max(acc1, best_acc1)

            # save checkpoint
            if args.amp:
                save_checkpoint({
                    'epoch': epoch + 1,
                    'state_dict': model.state_dict(),
                    'best_acc1': best_acc1,
                    'optimizer': optimizer.state_dict(),
                    'amp': amp.state_dict(),
                }, is_best)
            else:
                save_checkpoint({
                    'epoch': epoch + 1,
                    'state_dict': model.state_dict(),
                    'best_acc1': best_acc1,
                    'optimizer': optimizer.state_dict(),
                }, is_best)

        if args.stop_step_num is not None and cur_step >= args.stop_step_num:
            break

    sum_writer.close()


def train(train_loader, model, criterion, optimizer, epoch, args, global_step, sum_writer, device_nums_per_node):
    global cur_step

    if args.seed is not None:
        seed_everything(args.seed + epoch, args.device)

    batch_time = AverageMeter('Time', ':6.3f')
    data_time = AverageMeter('Data', ':6.3f')
    learning_rate = AverageMeter('LR', ':2.8f')
    losses = AverageMeter('Loss', ':6.8f')
    top1 = AverageMeter('Acc@1', ':6.2f')
    top5 = AverageMeter('Acc@5', ':6.2f')
    progress = ProgressMeter(
        len(train_loader),
        [batch_time, data_time, learning_rate, losses, top1, top5],
        prefix="Epoch: [{}]".format(epoch))

    # switch to train mode
    model.train()

    end = time.time()
    steps_per_epoch = len(train_loader)
    for i, (images, target) in enumerate(train_loader):

        global_step = epoch * steps_per_epoch + i
        cur_step = global_step

        lr = adjust_learning_rate(optimizer, global_step, steps_per_epoch, args)

        learning_rate.update(lr)

        sum_writer.add_scalar('learning rate', lr, global_step)

        # measure data loading time
        data_time.update(time.time() - end)

        if 'npu' in args.device:
            target = target.to(torch.int32)

        loc = None
        if 'npu' in args.device:
            loc = 'npu:{}'.format(args.pid_idx)
        elif 'cuda' in args.device:
            loc = 'cuda:{}'.format(args.pid_idx)
        images = images.to(loc, non_blocking=True)
        target = target.to(loc, non_blocking=True)

        # output = None
        # loss = None
        # with torch.autograd.profiler.profile(record_shapes=True, use_npu=True) as prof:

        # compute output
        output = model(images)
        loss = criterion(output, target)

        # measure accuracy and record loss
        acc1, acc5 = accuracy(output, target, topk=(1, 5))
        losses.update(loss.item(), images.size(0))
        top1.update(acc1[0], images.size(0))
        top5.update(acc5[0], images.size(0))

        # compute gradient and do SGD step
        optimizer.zero_grad()
        if args.amp:
            with amp.scale_loss(loss, optimizer) as scaled_loss:
                scaled_loss.backward()
        else:
            loss.backward()

        sum_writer.add_scalar('Accuary/train/top1', acc1, global_step)
        sum_writer.add_scalar('Accuary/train/top5', acc5, global_step)
        sum_writer.add_scalar('Loss/train/loss', loss, global_step)

        optimizer.step()
        # for name, parms in model.named_parameters():
        #     print('-->name:', name, ' -->grad_value_max:', torch.max(parms.grad), ' -->grad_value_min:', torch.min(parms.grad))

        # print(prof.key_averages().table())
        # prof.export_chrome_trace("mobilenetv2_{}_npu.prof".format(i))

        # measure elapsed time
        batch_time.update(time.time() - end)
        end = time.time()

        if i % args.print_freq == 0:
            if not args.multiprocessing_distributed or \
                    (args.multiprocessing_distributed and args.rank % device_nums_per_node == 0):
                progress.display(i)

        if not args.multiprocessing_distributed or \
                (args.multiprocessing_distributed and args.rank % device_nums_per_node == 0):
            print('FPS@all: {:.3f}'.format(8 * args.batch_size / batch_time.avg))

        if args.stop_step_num is not None and cur_step >= args.stop_step_num:
            break

    return global_step


def validate(val_loader, model, criterion, args, global_step, sum_writer, device_nums_per_node):
    batch_time = AverageMeter('Time', ':6.3f')
    losses = AverageMeter('Loss', ':.4e')
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

            if 'npu' in args.device:
                target = target.to(torch.int32)

            loc = None
            if 'npu' in args.device:
                loc = 'npu:{}'.format(args.pid_idx)
            elif 'cuda' in args.device:
                loc = 'cuda:{}'.format(args.pid_idx)
            images = images.to(loc, non_blocking=True)
            target = target.to(loc, non_blocking=True)

            # compute output
            output = model(images)
            loss = criterion(output, target)

            # measure accuracy and record loss
            acc1, acc5 = accuracy(output, target, topk=(1, 5))
            losses.update(loss.item(), images.size(0))
            top1.update(acc1[0], images.size(0))
            top5.update(acc5[0], images.size(0))

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % args.print_freq == 0:
                if not args.multiprocessing_distributed or \
                        (args.multiprocessing_distributed and args.rank % device_nums_per_node == 0):
                    progress.display(i)

        # TODO: this should also be done with the ProgressMeter
        print(' * Acc@1 {top1.avg:.3f} Acc@5 {top5.avg:.3f}'
              .format(top1=top1, top5=top5))
        if not args.multiprocessing_distributed or \
                (args.multiprocessing_distributed and args.rank % device_nums_per_node == 0):
            print("[device id:", args.gpu, "]", '[AVG-ACC] * Acc@1 {top1.avg:.3f} Acc@5 {top5.avg:.3f}'.format(top1=top1, top5=top5))

        if not args.evaluate:
            # sum_writer.add_scalar('Loss/validation/loss', losses, global_step)
            sum_writer.add_scalar('Accuary/validation/top1', top1.avg, global_step)
            sum_writer.add_scalar('Accuary/validation/top5', top5.avg, global_step)

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

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

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
        print('\t'.join(entries))

    def _get_batch_fmtstr(self, num_batches):
        num_digits = len(str(num_batches // 1))
        fmt = '{:' + str(num_digits) + 'd}'
        return '[' + fmt + '/' + fmt.format(num_batches) + ']'


def adjust_learning_rate(optimizer, global_step, steps_per_epoch, args):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    # lr = args.lr * (0.98 ** (epoch / 2.5))
    lr = args.lr * (0.98 ** (global_step // int(steps_per_epoch * 2.5)))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr


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
    main()
