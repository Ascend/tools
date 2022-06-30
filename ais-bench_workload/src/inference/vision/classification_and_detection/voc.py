import os
from random import sample

import core.dataset as dataset
import cv2
import numpy as np
from tqdm import tqdm

from yolo.parse_VOC2007 import parse_info
from yolo.yolo_caffe_preprocess import process


class VOC(dataset.DataSet):
    def __init__(self, dataset_path, image_list=None, name="None", image_size=[416, 416],
                    data_format="NHWC", pre_process=None, count=None, cache_path=None, normalize=True):
        super(VOC, self).__init__(cache_path)
        self.dataset_path = dataset_path

        self.count = count
        self.cur_path = os.getcwd()
        self.image_path = os.path.join(self.dataset_path, "JPEGImages")
        if os.path.exists(self.image_path) == False:
            print('dir:{} not exist'.format(self.image_path))
            raise RuntimeError()

        self.image_list = []
        self.image_size = []

        # write voc_name file
        CLASSES = ('aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car',
                'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
                'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor')
        cls = open(os.path.join(self.cache_path, "voc.names"), 'w')
        for i in CLASSES:
            cls.write(i)
            cls.write('\n')

        ground_turth_path = os.path.join(self.cache_path, "ground-truth")
        if not os.path.exists(ground_turth_path):
            os.makedirs(ground_turth_path)

        infofile = open(os.path.join(self.cache_path, 'VOC2007.info'), 'w')

        index = 0
        for f in os.listdir(self.image_path):
            if f.endswith(".jpg"):
                #self.image_list.append(os.path.join(self.image_path, f))
                self.image_list.append(f[:-4])
                img_cv = cv2.imread(os.path.join(self.image_path, f))
                shape = img_cv.shape
                width, height = shape[1], shape[0]
                self.image_size.append((width, height))
                parse_info(index, f, self.image_path, os.path.join(self.dataset_path, "Annotations"),
                    ground_turth_path, infofile)
                index += 1
                # limit the dataset if requested
                if self.count and len(self.image_list) >= self.count:
                    break
        infofile.close()

        self.pythoncmd = os.getenv("PYTHON_COMMAND")
        print("voc dataset init OK")

    def pre_proc_func(self, sample_list):
        print("pre process begin runing".format(sample_list))
        input_bin_path = os.path.join(self.cache_path, "input_bin")
        if not os.path.exists(input_bin_path):
            os.mkdir(input_bin_path)
        #for index in sample_list:
        for index in tqdm(sample_list, desc='Preprcess Processing'):
            filepath = os.path.join(self.image_path, self.image_list[index] + ".jpg")
            dst = os.path.join(input_bin_path, self.image_list[index] + ".npy")
            if not os.path.exists(dst):
                process(filepath, input_bin_path)

        cmd = "{} -u {}/yolo/get_yolo_info.py {} {} {}".format(
            self.pythoncmd, self.cur_path, input_bin_path, os.path.join(self.cache_path, "VOC2007.info"),
            os.path.join(self.cache_path, "yolov3_caffe.info"))
        print("get info cmd:", cmd)
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("cmd:{} run failed".format(cmd))
        print("pre process run done")
        return 0

    def get_processeddata_item(self, nr):
        binfile = f'{self.cache_path}/input_bin/{self.image_list[nr]}.bin'
        with open(binfile, 'rb') as fd:
            barray = fd.read()
            ndata = np.frombuffer(barray, dtype=np.int8)
        return ndata

    def get_predictresult_name(self, sample_id, index):
        return "{}_{}.bin".format(self.image_list[sample_id], index+1)

    def flush_queries(self):
        return 0

    def get_preprocessed_data(self, idx_list):
        data = np.array([self._preprocessed_data[idx] for idx in idx_list])
        img_info = np.array([[416, 416, self.image_size[idx_list[i]][1], self.image_size[idx_list[i]][0]] for i in range(len(idx_list))], dtype=np.float32)
        return (data, img_info)

class PostProcessBase:
    def __init__(self):
        pass

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        cmd = "{} {}/yolo/bin_to_predict_YOLO_CAFFE.py --bin_data_path {} --test_annotation {} --det_results_path {} \
             --coco_class_names {} --voc_class_names {} --net_input_width 416 --net_input_height 416".format(
            self.datasets.pythoncmd, self.datasets.cur_path, self.datasets.predict_result_path,
            os.path.join(self.datasets.cache_path, "yolov3_caffe.info"),
            os.path.join(self.datasets.cache_path, "detection-results"),
            os.path.join(self.datasets.dataset_path, "coco.names"),
            os.path.join(self.datasets.cache_path, "voc.names"))
        print("post proc cmd:", cmd)
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("cmd:{} run failed".format(cmd))

        cmd = "cd {};{} {}/yolo/map_calculate.py -na -np".format(
            self.datasets.cache_path, self.datasets.pythoncmd, self.datasets.cur_path, self.datasets.cur_path)
        print("map calc cmd:", cmd)
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("cmd:{} run failed".format(cmd))

        mAP = 0.0
        with open(os.path.join(self.datasets.cache_path, "mAP.txt"), 'rb') as fd:
            mAP = float(fd.read())
        return mAP

    def set_datasets(self, datasets):
        self.datasets = datasets

    def set_backend(self, backend):
        self.backend = backend

class PostProcessCommon(PostProcessBase):
    def __init__(self, offset=0):
        super(PostProcessCommon, self).__init__()
        self.offset = offset
