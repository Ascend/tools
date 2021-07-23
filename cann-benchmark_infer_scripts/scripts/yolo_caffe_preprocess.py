#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

import numpy as np
import os
import cv2


def process_image(img, min_side):
    """
    image process with min side
    """
    size = img.shape
    h, w = size[0], size[1]
    scale = max(w, h) / float(min_side)
    new_w, new_h = int(w / scale), int(h / scale)
    resize_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    if new_w % 2 != 0 and new_h % 2 == 0:
        top, bottom, left, right = (min_side - new_h) / 2, (min_side - new_h) / 2, (min_side - new_w) / 2 + 1, (
                    min_side - new_w) / 2
    elif new_h % 2 != 0 and new_w % 2 == 0:
        top, bottom, left, right = (min_side - new_h) / 2 + 1, (min_side - new_h) / 2, (min_side - new_w) / 2, (
                    min_side - new_w) / 2
    elif new_h % 2 == 0 and new_w % 2 == 0:
        top, bottom, left, right = (min_side - new_h) / 2, (min_side - new_h) / 2, (min_side - new_w) / 2, (
                    min_side - new_w) / 2
    else:
        top, bottom, left, right = (min_side - new_h) / 2 + 1, (min_side - new_h) / 2, \
                                   (min_side - new_w) / 2 + 1, (min_side - new_w) / 2
    pad_img = cv2.copyMakeBorder(resize_img, int(top), int(bottom), int(left), int(right),
                                 cv2.BORDER_CONSTANT, value=[0, 0, 0])
    return pad_img


def process(input_path):
    """
    image process
    """
    flbin = input_path.split('.')[0] + ".bin"
    imgSrc = cv2.imread(input_path)
    img_process = process_image(imgSrc, 416)
    imgDst = np.array(img_process)
    imgDst = np.expand_dims(imgDst, axis=0)
    imgDst = imgDst.astype("uint8")
    imgDst.tofile(flbin)


if __name__ == "__main__":
    images = os.listdir(r'./')
    for image_name in images:
        if not image_name.endswith(".jpg"):
            continue
        print("start to process image {}....".format(image_name))
        process(image_name)
