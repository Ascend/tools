import multiprocessing
import os
import re
import time

import core.dataset as dataset
import numpy as np
from PIL import Image


class ImagenetSet(dataset.DataSet):
    def __init__(self, dataset_path, image_list=None, image_size=None, data_format=None,
                    pre_process=None, count=None,cache_path=os.getcwd(), normalize=True, tag=None):
        super(ImagenetSet, self).__init__(cache_path)
        self.dataset_path = dataset_path
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
        if tag is None:
            self.tag = "resnet"
        else:
            self.tag = tag
        self.prepro_bin_path = os.path.join(cache_path, "prepro_bin_result")
        if not os.path.exists(self.prepro_bin_path):
            os.mkdir(self.prepro_bin_path)
        self.model_config = {
            'resnet': {
                'resize': 256,
                'centercrop': 256,
                'mean': [0.485, 0.456, 0.406],
                'std': [0.229, 0.224, 0.225],
            },
            'inception': {
                'resize': 342,
                'centercrop': 299,
                'mean': [0.485, 0.456, 0.406],
                'std': [0.229, 0.224, 0.225],
            }
        }

        not_found = 0
        if image_list is None:
            # by default look for val_map.txt
            image_list = os.path.join(dataset_path, "val_map.txt")
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

        if not self.image_list:
            print("no images in image list found")
            raise ValueError("no images in image list found")
        if not_found > 0:
            print("reduced image list, %d images not found", not_found)
        self.label_list = np.array(self.label_list)

    @staticmethod
    def center_crop(img, output_size):
        if isinstance(output_size, int):
            output_size = (int(output_size), int(output_size))
        image_width, image_height = img.size
        crop_height, crop_width = output_size
        crop_top = int(round((image_height - crop_height) / 2.))
        crop_left = int(round((image_width - crop_width) / 2.))
        return img.crop((crop_left, crop_top, crop_left + crop_width, crop_top + crop_height))

    @staticmethod
    def resize(img, size, interpolation=Image.BILINEAR):
        if isinstance(size, int):
            w, h = img.size
            if (w <= h and w == size) or (h <= w and h == size):
                return img
            if w < h:
                ow = size
                oh = int(size * h / w)
                return img.resize((ow, oh), interpolation)
            else:
                oh = size
                ow = int(size * w / h)
                return img.resize((ow, oh), interpolation)
        else:
            return img.resize(size[::-1], interpolation)

    def gen_input_bin(self, mode_type, file_batches, batch):
        i = 0
        for file in file_batches[batch]:
            i = i + 1
            # RGBA to RGB
            tmp_path = os.path.join(self.dataset_path, file)
            image = Image.open(tmp_path)
            image = image.convert('RGB')
            image = ImagenetSet.resize(image, self.model_config[mode_type]['resize']) # Resize
            image = ImagenetSet.center_crop(image, self.model_config[mode_type]['centercrop']) # CenterCrop
            img = np.array(image, dtype=np.int8)
            img.tofile(os.path.join(self.prepro_bin_path, file.split('.')[0] + ".bin"))

    def pre_proc_func(self, sample_list):
        files = os.listdir(self.dataset_path)
        files.sort()
        if len(sample_list) < 500:
            file_batches = [files[0 : len(sample_list)]]
        else:
            file_batches = [files[i:i + 500] for i in range(0, len(sample_list), 500) if files[i:i + 500] != []]
        thread_pool = multiprocessing.Pool(len(file_batches))
        for batch in range(len(file_batches)):
            thread_pool.apply_async(self.gen_input_bin, args=(self.tag, file_batches, batch))
        thread_pool.close()
        thread_pool.join()
        print("in thread, except will not report! please ensure bin files generated.")
        return 0


    def get_processeddata_item(self, nr):
        """Get image by number in the list."""
        dst = os.path.join(self.prepro_bin_path, self.image_list[nr].split('.')[0]+'.bin')
        with open(dst, 'rb') as fd:
            barray = fd.read()
            ndata = np.frombuffer(barray, dtype=np.int8)
        return ndata

    def get_sample_path(self, nr):
        src = os.path.join(self.dataset_path, self.image_list[nr])
        return src

    def flush_queries(self):
        self.image_list.clear()
        self.label_list.clear()
        self.prediction_items.clear()
        return 0


class PostProcess:
    def __init__(self, offset=0):
        super(PostProcess, self).__init__()
        self.offset = offset
        self.good = 0
        self.total = 0

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        self.good = 0
        self.total = 0
        n = len(sample_list)
        m = len(self.backend.outputs)
        for i in range(n):
            pred = []
            labels = self.datasets.label_list[i:i+1]
            for j in range(m):
                cur_pred = self.datasets.get_predict_result(i, j)
                pred.append(cur_pred)
            self.post_proc(pred, expected=labels)

        # 获取准确率信息并返回
        accuracy = self.get_accuracy()
        print("self.good is ", self.good, "self.total is ", self.total)
        return accuracy

    def post_proc(self, results, expected=None, result_dict=None):
        results = results[0]
        result = np.argsort(-results)
        for idx in range(1):
            if result[0][idx] == expected[0]:
                self.good += 1
                break
        self.total += 1
        return results

    def get_accuracy(self):
        if self.total == 0:
            return 0
        return round(self.good/self.total, 5)

    def set_backend(self, backend):
        self.backend = backend

    def set_datasets(self, datasets):
        self.datasets = datasets
