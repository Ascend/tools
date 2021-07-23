"""
    Copyright 2020 Huawei Technologies Co., Ltd

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    Typical usage example:
"""

import os
import sys
import numpy as np
import cv2


def preprocess_mobilenet(input_path, output_path, precision):
    """
    @description: mobilenet preprocess
    @param input_path
    @param output_path
    @param precision
    @return
    """
    height = 224
    width = 224
    mean = [103.94, 116.78, 126.68]
    std = [0.017, 0.017, 0.017]
    img = cv2.imread(input_path)
    h, w, _ = img.shape
    if h < w:
        off = (w - h) // 2
        img = img[:, off:off + h]
    else:
        off = (h - w) // 2
        img = img[off:off + h, :]
    res = cv2.resize(img, (height, width), interpolation=cv2.INTER_LINEAR)
    img = np.array(res)
    if precision == "fp32":
        img = img.astype("float32")
    elif precision == "fp16":
        img = img.astype("float16")
    img -= mean
    img *= std
    img = img.reshape([1] + list(img.shape))  # NHWC
    result = img.transpose([0, 3, 1, 2])  # NCHW
    img_name = input_path.split('/')[-1]
    bin_name = img_name.split('.')[0] + ".bin"
    output_file = os.path.join(output_path, bin_name)
    result.tofile(output_file)


if __name__ == "__main__":
    image_folder_path = sys.argv[1]
    data_folder_path = sys.argv[2]
    data_precision = sys.argv[3]
    images = os.listdir(image_folder_path)
    image_num = 0
    for image_cur in images:
        if not (image_cur.endswith(".jpeg") or image_cur.endswith(".JPEG")
                or image_cur.endswith(".jpg")):
            continue
        image_num += 1
        print("start to process image {}....=={}".format(image_cur, image_num))
        path_image = os.path.join(image_folder_path, image_cur)
        preprocess_mobilenet(path_image, data_folder_path, data_precision)
