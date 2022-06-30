import os
import re
import time
from concurrent.futures import process

import core.dataset as dataset
import numpy as np
from tqdm import tqdm


class Imagenet(dataset.DataSet):
    def __init__(self, dataset_path, image_list=None, image_size=None, data_format=None,
                    pre_process=None, count=None,cache_path=os.getcwd(), normalize=True, tag=None):
        super(Imagenet, self).__init__(cache_path)
        self.dataset_path = dataset_path
        self.tag = tag
        if image_size is None:
            self.image_size = [224, 224]
        else:
            self.image_size = image_size
        if data_format is None:
            self.data_format = "NHWC"
        else:
            self.data_format = data_format
        self.pre_process = pre_process
        self.count = count
        self.normalize = normalize

        not_found = 0
        if image_list is None:
            # by default look for val_map.txt
            image_list = os.path.join(dataset_path, "val_map.txt")
        start = time.time()
        with open(image_list, 'r') as f:
            for s in f:
                image_name, label = re.split(r"\s+", s.strip())
                src = os.path.join(dataset_path, image_name)
                if not os.path.exists(src):
                    # if the image does not exists ignore it
                    not_found += 1
                    continue
                self.image_list.append(image_name)
                self.label_list.append(int(label))

                # limit the dataset if requested
                if self.count and len(self.image_list) >= self.count:
                    break

        time_taken = time.time() - start
        if not self.image_list:
            print("no images in image list found")
            raise ValueError("no images in image list found")
        if not_found > 0:
            print("reduced image list, %d images not found", not_found)

        self.label_list = np.array(self.label_list)

    def pre_proc_func(self, sample_list):
        #for index in sample_list:
        for index in tqdm(sample_list, desc='Preprcess Processing'):
            filepath = os.path.join(self.dataset_path, self.image_list[index])
            dst = os.path.join(self.cache_path, self.image_list[index] + ".npy")
            if not os.path.exists(dst):
                with open(filepath, 'rb') as fd:
                    img = fd.read()
                    processed_img = self.pre_process(img, output_image_size=self.image_size, target_format=self.data_format,
                                                normalize=self.normalize)
                    np.save(dst, processed_img)
        return 0

    def get_processeddata_item(self, nr):
        """Get image by number in the list."""
        dst = os.path.join(self.cache_path, self.image_list[nr])
        img = np.load(dst + ".npy")
        return img

    def get_sample_path(self, nr):
        src = os.path.join(self.dataset_path, self.image_list[nr])
        return src

    def flush_queries(self):
        self.image_list.clear()
        self.label_list.clear()
        self.prediction_items.clear()
        return 0

class PostProcessBase:
    def __init__(self):
        self.good = 0
        self.total = 0

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        self.good = 0
        self.total = 0
        n = len(sample_list)
        m = len(self.backend.outputs)
        for i in tqdm(range(n), desc="Postprocessing"):
            pred = []
            labels = self.datasets.label_list[i:i+1]
            for j in range(m):
                cur_pred = self.datasets.get_predict_result(i, j)
                pred.append(cur_pred)
            self.post_proc(pred, expected=labels)

        # 获取准确率信息并返回
        accuracy = self.get_accuracy()
        return accuracy

    def get_accuracy(self):
        if self.total == 0:
            return 0
        return round(self.good/self.total, 2)

    def set_backend(self, backend):
        self.backend = backend

    def set_datasets(self, datasets):
        self.datasets = datasets

class PostProcessCommon(PostProcessBase):
    def __init__(self, offset=0):
        super(PostProcessCommon, self).__init__()
        self.offset = offset

    def post_proc(self, results, expected=None, result_dict=None):
        results = results[0]
        processed_results = []
        n = len(results)
        for idx in range(0, n):
            result = results[idx] + self.offset
            processed_results.append([result])
            # print("post proc idx:{}/{} result:{} expect:{}".format(idx, n, result, expected[idx]))
            if result == expected[idx]:
                self.good += 1
        self.total += n
        return processed_results

class PostProcessArgMax(PostProcessBase):
    def __init__(self, offset=0):
        super(PostProcessArgMax, self).__init__()
        self.offset = offset

    def post_proc(self, results, expected=None):
        results = results[0] # ndarray (N, 1000)
        results = np.argmax(results, axis=1)  # ndarray (N, )
        processed_results = []
        n = len(results)
        for idx in range(n):
            result = results[idx] + self.offset
            processed_results.append([result])
            if result == expected[idx]:
                self.good += 1
            # print("post proc idx:{}/{} result:{} expect:{}".format(idx, n, result, expected[idx]))
        self.total += n
        return processed_results
