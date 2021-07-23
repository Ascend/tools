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

# 1 convert model with aipp config below
# 2 preprocess images with this script
#
# AIPP config
# aipp_op {
#       aipp_mode: static
#       input_format: RGB888_U8
#       mean_chn_0: 128
#       mean_chn_1: 128
#       mean_chn_2: 128
#       var_reci_chn_0: 0.00301
#       var_reci_chn_0: 0.00301
#       var_reci_chn_0: 0.00301
#       src_image_size_w: 299
#       src_image_size_h: 299
# }
# 

import os
import sys
import time
import numpy as np
import shutil
from PIL import Image
import tensorflow as tf


def preprocess(src_path, save_path):
    """
        @description: tf image preprocess and save
        @param src_path  image paths
        @param save_path target path after preprocessing
        @return none
    """
    in_files = os.listdir(src_path)
    resize_shape = [299, 299, 3]
    if os.path.isdir(save_path):
        shutil.rmtree(save_path)
    i = 0
    img_pl = tf.placeholder(tf.uint8, (None, None, 3), name='input_tensor')
    img_tf = tf.image.central_crop(img_pl, 0.875)
    img_tf = tf.expand_dims(img_tf, 0)
    img_tf = tf.image.resize_bilinear(img_tf, resize_shape[:-1], align_corners=False)
    img_tf = tf.squeeze(img_tf, [0])
    img_tf = tf.cast(img_tf, tf.uint8)
    for file in in_files:
        i = i + 1
        print(file, "=============================================", i)
        start = time.time()
        img_np = Image.open(os.path.join(src_path, file)).convert('RGB')
        img_np = np.array(img_np)
        with tf.Session() as sess:
            img = sess.run(img_tf, feed_dict={img_pl: img_np})
        img.tofile(os.path.join(save_path, file.split('.')[0] + ".bin"))
        end = time.time()
        cast = end - start


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("usage: python3 xxx.py [src_path] [save_path]")
    src_path = sys.argv[1]
    save_path = sys.argv[2]
    src_path = os.path.realpath(src_path)
    save_path = os.path.realpath(save_path)
    preprocess(src_path, save_path)
