import os
import sys
from os.path import join

import core.dataset as dataset
import cv2
import numpy as np
from PIL import Image
from sklearn.model_selection import learning_curve
from tqdm import tqdm

from yolo.parse_VOC2007 import parse_info
from yolo.yolo_caffe_preprocess import process


class VOC(dataset.DataSet):
    def __init__(self, dataset_path, image_list=None, name="None", image_size=[416, 416],
                    data_format="NHWC", pre_process=None, count=None, cache_path=None, normalize=True):
        super(VOC, self).__init__(cache_path)
        self.image_list = []
        self.output_dir = "processed_data"
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        self.name_index_map = {}
        self.dataset_path = dataset_path

        self.seg_trainval_txt = os.path.join(self.dataset_path,"ImageSets/Segmentation/val.txt")
        with open(self.seg_trainval_txt,"r") as f:
            lines = f.readlines()
            for i,line in tqdm(enumerate(lines), desc="Preprcess Processing"):
                pic_name = line.replace('\n','')
                pic_path = os.path.join(self.dataset_path,'JPEGImages/{}.jpg'.format(pic_name))
                self.image_list.append(pic_name)
                self.name_index_map[pic_name] = i

    def pre_proc_func(self, sample_list):
        with open(self.seg_trainval_txt,"r") as f:
            lines = f.readlines()
            for line in tqdm(lines, desc="Preprcess Processing"):
                pic_name = line.replace('\n','')
                pic_path = os.path.join(self.dataset_path,'JPEGImages/{}.jpg'.format(pic_name))
                origImg = np.array(Image.open(pic_path).resize((513,513)),np.uint8)
                inputValue = origImg.reshape(1,513,513,3)
                dst = os.path.join(self.output_dir,'{}.npy'.format(pic_name))
                np.save(dst, inputValue)
        return 0

    def get_processeddata_item(self, nr):
        file = f'{self.output_dir}/{self.image_list[nr]}.npy'
        img = np.load(file)
        return img

    def flush_queries(self):
        return 0

    def get_preprocessed_data(self, idx_list):
        data = np.array([self._preprocessed_data[idx] for idx in idx_list])
        # img_info = np.array([[416, 416, self.image_size[idx_list[i]][1], self.image_size[idx_list[i]][0]] for i in range(len(idx_list))], dtype=np.float32)
        return data

# 设标签宽W，长H
def fast_hist(a, b, n):  # a是转化成一维数组的标签，形状(H×W,)；b是转化成一维数组的标签，形状(H×W,)；n是类别数目，实数（在这里为19）
    k = (a >= 0) & (a < n)  # k是一个一维bool数组，形状(H×W,)；目的是找出标签中需要计算的类别（去掉了背景） k=0或1
    hist = np.bincount(n * a[k].astype(int) + b[k], minlength=n ** 2)
    return np.bincount(n * a[k].astype(int) + b[k], minlength=n ** 2).reshape(n,n)  # np.bincount计算了从0到n**2-1这n**2个数中每个数出现的次数，返回值形状(n, n)

def per_class_iu(hist):  # 分别为每个类别（在这里是19类）计算mIoU，hist的形状(n, n)
    return np.diag(hist) / (hist.sum(1) + hist.sum(0) - np.diag(hist))  # 矩阵的对角线上的值组成的一维数组/矩阵的所有元素之和，返回值形状(n,)

def compute_mIoU(gt_dir, pred_dir, devkit_dir, sample_list, name_index_map):  # 计算mIoU的函数
    """
    Compute IoU given the predicted colorized images and
    """
    num_classes = 21
    print('Num classes', num_classes)
    name_classes = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
                    "diningtable", "dog", "horse", "motobike", "person", "pottedplant", "sheep", "sofa", "train",
                    "tvmonitor"]
    hist = np.zeros((num_classes, num_classes))

    image_path_list = join(devkit_dir, 'val.txt')  # 在这里打开记录分割图片名称的txt
    label_path_list = join(devkit_dir, 'val.txt')  # ground truth和自己的分割结果txt一样
    gt_imgs = open(label_path_list, 'r').read().splitlines()  # 获得验证集标签名称列表
    gt_imgs = [join(gt_dir, x) for x in gt_imgs]  # 获得验证集标签路径列表，方便直接读取
    pred_imgs = open(image_path_list, 'r').read().splitlines()  # 获得验证集图像分割结果名称列表
    pred_imgs = [join(pred_dir, 'idx_{}_array_0.npy'.format(name_index_map[x])) for x in pred_imgs]
    for ind in range(len(gt_imgs)):  # 读取每一个（图片-标签）对
        pred = np.load(pred_imgs[ind]).astype(np.uint8).reshape(513, 513)  # 读取一张图像分割结果，转化成numpy数组

        label = np.array(Image.open(gt_imgs[ind] + '.png').resize((513,513)),np.uint8)  # 读取一张对应的标签，转化成numpy数组
        if len(label.flatten()) != len(pred.flatten()):
            lab_shape = label.shape
            pred = cv2.resize(pred, label.shape, interpolation=cv2.INTER_NEAREST)

        hist += fast_hist(label.flatten(), pred.flatten(), num_classes)  # 对一张图片计算19×19的hist矩阵，并累加

    mIoUs = per_class_iu(hist)  # 计算所有验证集图片的逐类别mIoU值
    for ind_class in range(num_classes):  # 逐类别输出一下mIoU值
        print('{: <15}:{}'.format(name_classes[ind_class], round(mIoUs[ind_class] * 100, 2)))
    mIoUs = round(np.nanmean(mIoUs) * 100, 2)
    print('Overall mIoU: ' + str(mIoUs))  # 在所有验证集图像上求所有类别平均的mIoU值，计算时忽略NaN值
    return mIoUs


class PostProcessBase:
    def __init__(self):
        pass

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        root_dir = self.datasets.dataset_path
        gt_dir = join(root_dir,'SegmentationClass')
        list_dir = join(root_dir,'ImageSets/Segmentation/')
        pred_dir = self.datasets.predict_result_path
        result = compute_mIoU(gt_dir,pred_dir,list_dir, sample_list, self.datasets.name_index_map)
        return result

    def set_datasets(self, datasets):
        self.datasets = datasets

    def set_backend(self, backend):
        self.backend = backend

class PostProcessCommon(PostProcessBase):
    def __init__(self, offset=0):
        super(PostProcessCommon, self).__init__()
        self.offset = offset
