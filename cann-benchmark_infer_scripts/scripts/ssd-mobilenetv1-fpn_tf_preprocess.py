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
from PIL import Image
import sys
import numpy as np


def load_image_into_numpy_array(image):
    """
    load image into numpy array
    """
    im_width, im_height = image.size
    print(image.getdata().size)
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint0)


def read_imame_and_to_numpy(file_path, data_dtype, size=None):
    """
    read image and load into numpy
    """
    image = Image.open(file_path)
    image = image.convert("RGB")
    if size is not None:
        new_image = image.resize([size[1], size[0]], Image.BILINEAR)
    else:
        new_image = image
    image_np = load_image_into_numpy_array(new_image)
    image_np = image_np.astype(data_dtype)
    return image_np


def preprocess_image(src_path, save_path):
    """
    preprocess image
    """
    files = os.listdir(src_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    i = 0
    for file in files:
        (filename, extension) = os.path.splitext(file)
        if(extension == '.jpg' or extension == 'JPEG'):
            i += 1
            print(file, "====", i)
            img_path = os.path.join(src_path, file)
            input_type = np.uint8
            image_np = read_imame_and_to_numpy(img_path, input_type, [640, 640])
            image_np.tofile(os.path.join(save_path, file.split('.')[0] + ".bin"))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("usage: python3 xxx.py [src_path] [save_path]")
    src_path = sys.argv[1]
    save_path = sys.argv[2]
    src_path = os.path.realpath(src_path)
    save_path = os.path.realpath(save_path)
    preprocess_image(src_path, save_path)
