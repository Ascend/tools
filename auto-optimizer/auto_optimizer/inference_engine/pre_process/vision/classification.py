# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from abc import ABC
from dataclasses import dataclass

import numpy as np
from PIL import Image
from ..pre_process_base import PreProcessBase
from ...data_process_factory import PreProcessFactory

logging = logging.getLogger("auto-optimizer")


@dataclass
class ImageParam:
    mean: list
    std: list
    center_crop: int
    resize: int
    dtype: str


@PreProcessFactory.register("classification")
class ImageNetPreProcess(PreProcessBase, ABC):
    def __call__(self, loop, cfg, in_queue, out_queue):
        """
        和基类的参数顺序和个数需要一致
        """
        logging.debug("pre_process start")
        try:
            image_param = ImageNetPreProcess._get_params(cfg)

            output = []
            for i in range(loop):
                in_data = in_queue.get()
                if len(in_data) < 2:  # include lable and data
                    raise RuntimeError("input params error len={}".format(len(in_data)))

                label, datas = in_data[0], in_data[1]
                for data in datas:
                    img = ImageNetPreProcess.image_process(data, image_param)
                    output.append(img)

                out_queue.put([label, output])
                output.clear()
        except Exception as err:
            logging.error("pre_process failed error={}".format(err))

        logging.debug("pre_process end")

    @staticmethod
    def image_process(file_path, image_param):
        # RGBA to RGB
        image = Image.open(file_path).convert('RGB')
        image = ImageNetPreProcess.resize(image, image_param.resize)
        image = ImageNetPreProcess.center_crop(image, image_param.center_crop)
        if image_param.dtype == "fp32":
            img = np.array(image, dtype=np.float32)
            img = img.transpose(2, 0, 1)  # HWC -> CHW
            img = img / 255.    # ToTensor: div 255
            img -= np.array(image_param.mean, dtype=np.float32)[:, None, None]
            img /= np.array(image_param.std, dtype=np.float32)[:, None, None]
        elif image_param.dtype == "int8":
            img = np.array(image, dtype=np.int8)
        else:
            raise RuntimeError("dtype is not support")

        return img

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
    def resize(img, size, interpolation=Image.Resampling.BILINEAR):
        if isinstance(size, int):
            w, h = img.size
            if (w <= h and w == size) or (h <= w and h == size):
                return img
            if w < h:
                o_w = size
                o_h = int(size * h / w)
                return img.resize((o_w, o_h), interpolation)
            else:
                o_h = size
                o_w = int(size * w / h)
                return img.resize((o_w, o_h), interpolation)
        else:
            return img.resize(size[::-1], interpolation)

    @staticmethod
    def _check_params(image_param):
        if all(i > 1 for i in image_param.std) or all(i < 0 for i in image_param.std):
            raise RuntimeError("the parameter does not meet the requirements std={}".format(image_param.std))

        if all(i > 1 for i in image_param.mean) or all(i < 0 for i in image_param.mean):
            raise RuntimeError("the parameter does not meet the requirements mean={}".format(image_param.mean))

        if image_param.dtype not in ["fp32", "fp16", "int8"]:
            raise RuntimeError("the parameter does not meet the requirements dtype={}".format(image_param.dtype))

    @staticmethod
    def _get_params(cfg):
        try:
            mean = cfg["mean"]
            std = cfg["std"]
            center_crop = cfg["center_crop"]
            resize = cfg["resize"]
            dtype = cfg["dtype"]

            image_param = ImageParam(mean, std, center_crop, resize, dtype)
            ImageNetPreProcess._check_params(image_param)

            return image_param
        except Exception as err:
            raise RuntimeError("get params failed error={}".format(err))
