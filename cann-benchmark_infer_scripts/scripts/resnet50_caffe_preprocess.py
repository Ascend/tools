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
import sys


def center_crop(img, out_height, out_width):
    """
    image center crop process
    """
    height, width, _ = img.shape
    left = int((width - out_width) / 2)
    right = int((width + out_width) / 2)
    top = int((height - out_height) / 2)
    bottom = int((height + out_height) / 2)
    img = img[top:bottom, left:right]
    return img


def resize_with_aspectratio(img, out_height, out_width, scale=87.5, inter_pol=cv2.INTER_LINEAR):
    """
    resize image with aspect ratio
    """
    height, width, _ = img.shape
    new_height = int(100. * out_height / scale)
    new_width = int(100. * out_width / scale)
    if height > width:
        w = new_width
        h = int(new_height * height / width)
    else:
        h = new_height
        w = int(new_width * width / height)
    img = cv2.resize(img, (w, h), interpolation=inter_pol)
    return img


def preprocess_resnet50(img, need_transpose=True, precision="fp16"):
    """
    resnet50 preprocess main function
    """
    output_height = 224
    output_width = 224
    cv2_interpol = cv2.INTER_AREA
    img = resize_with_aspectratio(img, output_height, output_width, inter_pol=cv2_interpol)
    img = center_crop(img, output_height, output_width)

    if precision == "fp32":
        img = np.asarray(img, dtype='float32')
    if precision == "fp16":
        img = np.asarray(img, dtype='float16')

    means = np.array([103.94, 116.78, 126.68], dtype=np.float16)
    img -= means
    if need_transpose:
        img = img.transpose([2, 0, 1])
    return img


def resnet50(input_path, output_path):
    """
    resnet50 model preprocess
    """
    img = cv2.imread(input_path)
    h, w, _ = img.shape
    img_name = input_path.split('/')[-1]
    bin_name = img_name.split('.')[0] + ".bin"
    output_fl = os.path.join(output_path, bin_name)
    if os.path.exists(output_fl):
        pass
    else:
        imgdst = preprocess_resnet50(img)
        imgdst.tofile(output_fl)


if __name__ == "__main__":
    pathSrcImgFD = sys.argv[1]
    pathDstBinFD = sys.argv[2]
    images = os.listdir(pathSrcImgFD)
    for image_name in images:
        if not (image_name.endswith(".jpeg") or image_name.endswith(".JPEG") or image_name.endswith(".jpg")):
            continue
        print("start to process image {}....".format(image_name))
        path_image = os.path.join(pathSrcImgFD, image_name)
        resnet50(path_image, pathDstBinFD)
