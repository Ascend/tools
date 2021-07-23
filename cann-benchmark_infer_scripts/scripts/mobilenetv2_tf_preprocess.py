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

import sys
import os
import time
from PIL import Image
import tensorflow.compat.v1 as tf
import numpy as np


def preprocess_for_eval(image,
                        height,
                        width,
                        central_fraction=0.875,
                        scope=None,
                        central_crop=True,
                        use_grayscale=False):
    """Prepare one image for evaluation.

    If height and width are specified it would output an image with that size by
    applying resize_bilinear.

    If central_fraction is specified it would crop the central fraction of the
    input image.

    Args:
        image: 3-D Tensor of image. If dtype is tf.float32 then the range should be
        [0, 1], otherwise it would converted to tf.float32 assuming that the range
        is [0, MAX], where MAX is largest positive representable number for
        int(8/16/32) data type (see `tf.image.convert_image_dtype` for details).
        height: integer
        width: integer
        central_fraction: Optional Float, fraction of the image to crop.
        scope: Optional scope for name_scope.
        central_crop: Enable central cropping of images during preprocessing for
            evaluation.
        use_grayscale: Whether to convert the image from RGB to grayscale.
    Returns:
        3-D float Tensor of prepared image.
    """
    with tf.name_scope(scope, 'eval_image', [image, height, width]):
        if image.dtype != tf.float32:
            image = tf.image.convert_image_dtype(image, dtype=tf.float32)
        if use_grayscale:
            image = tf.image.rgb_to_grayscale(image)
        # Crop the central region of the image with an area containing 87.5% of
        # the original image.
        if central_crop and central_fraction:
            image = tf.image.central_crop(image, central_fraction=central_fraction)

        if height and width:
            # Resize the image to the specified height and width.
            image = tf.expand_dims(image, 0)
            image = tf.image.resize_bilinear(image, [height, width],
                                             align_corners=False)
            image = tf.squeeze(image, [0])
        image = tf.subtract(image, 0.5)

        image = tf.multiply(image, 2.0)
        return image


def convert_jpg2rgb(img_name):
    """
    @description: convert jpg to rgb
    @param img_name
    @return image
    """
    image = Image.open(img_name).convert('RGB')
    return image


def preprocess(src_path, save_path, width, height):
    """
    @description: mobilenet v2 preprocess
    @param src_path
    @param save_path
    @param width
    @param height
    @return none
    """
    in_files = os.listdir(src_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    i = 0

    img_pl = tf.placeholder(tf.uint8, (None, None, 3), name='input_tensor')
    image = preprocess_for_eval(img_pl, height=height, width=width, central_crop=True,
                                use_grayscale=False)

    for file in in_files:
        i = i + 1
        print(file, "====", i)
        start = time.time()
        img_np = convert_jpg2rgb(os.path.join(src_path, file))
        img_np = np.array(img_np)

        with tf.Session() as sess:
            img = sess.run(image, feed_dict={img_pl: img_np})
        img.tofile(os.path.join(save_path, file.split('.')[0] + ".bin"))
        end = time.time()
        cast = end - start
        print('time case {}'.format(cast))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise Exception("usage: python3 xxx.py [src_path] [save_path]"
                        "[whith] [height]")
    src_path = sys.argv[1]
    save_path = sys.argv[2]
    width = sys.argv[3]
    height = sys.argv[4]
    src_path = os.path.realpath(src_path)
    save_path = os.path.realpath(save_path)

    preprocess(src_path, save_path, int(width), int(height))
