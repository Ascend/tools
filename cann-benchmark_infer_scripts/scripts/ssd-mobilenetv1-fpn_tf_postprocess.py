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
from PIL import Image


def get_class(coco_name_path):
    """
    get class name list
    """
    classes_path = os.path.expanduser(coco_name_path)
    with open(classes_path) as file:
        class_names = file.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names


def get_resultpath(data_info_path, result_path,
                   save_path, coco_name_path,
                   imagenet_pic_path):
    """
    get result path
    """
    name_list = []

    with open(data_info_path, 'r') as file:
        for line in file:
            line = line.strip('\n')
            line = line.split(' ')
            img_name = line[1].split('/')[-1].strip('.bin')
            name_list.append(img_name)

    for name in name_list:
        image = Image.open(imagenet_pic_path + '/' + name + '.jpg')
        im_w, im_h = image.size

        num_detections = np.fromfile(result_path + '/' + name + '_1.bin', np.float32)
        num_detections = num_detections.astype(np.int16)
        index = num_detections[0]
        out_boxes = np.fromfile(result_path + '/' + name + '_3.bin', np.float32)
        out_boxes = np.reshape(out_boxes, (100, 4))
        out_scores = np.fromfile(result_path + '/' + name + '_2.bin', np.float32)
        out_scores = np.reshape(out_scores, (100))
        out_classes = np.fromfile(result_path + '/' + name + '_4.bin', np.float32)
        out_classes = out_classes.astype(np.int16)
        out_classes = np.reshape(out_classes, (100))
        out_classes = out_classes[:index]
        print("out_classes", out_classes)
        print("shape", out_boxes.shape, out_classes.shape, out_scores.shape, num_detections)
        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))  # prompt for found number of bbox
        file = open(save_path + '/' + name + '.txt', 'w')
        print("out_scores", out_scores)
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = get_class(coco_name_path)
            predicted_class = predicted_class[c]
            box = out_boxes[i]
            score = out_scores[i]
            print("out_classes_sorces", c, predicted_class, score)
            top1, left1, bottom, right = box
            top = top1 * im_h
            left = left1 * im_w
            bottom = (bottom - top1) * im_h
            right = (right - left1) * im_w
            # write detected pos
            file.write(predicted_class + ' ' + str(score) + ' ' + str(left) + ' '
                       + str(top) + ' ' + str(right + left) + ' ' + str(
                    bottom + top) + '\n')
        file.close()


if __name__ == '__main__':
    """
    :param data_info_path: path of benchmark data.info
    :param result_path: path of benchmark generate result, usually is ./result/dumpOutput/
    :param save_path: path of save geberate reseult bin
    :param coco_name_path: path of coco.name
    :param imagenet_pic_path: imaegs path of coco dataset
    sample as:
    python3 ./postprocess_ssd_mobilenet_v1_fpn.py
        /home/Benchmark_autotest/dataset/coco_2014_bin.info
        /home/Benchmark_autotest/result/dumpOutput/
        /home/Benchmark_autotest/dataset/script/SSD/pre_txt.txt
        /home/Benchmark_autotest/dataset/script/images/coco.names
        /root/dataset/coco2014/val2014
    """
    if len(sys.argv) < 5:
        raise Exception("usage: python3 xxx.py [src_path] [save_path] "
                        "[coco_name_path] [imagenet_pic_path]")
    data_info_path = sys.argv[1]
    result_path = sys.argv[2]
    save_path = sys.argv[3]
    coco_name_path = sys.argv[4]
    imagenet_pic_path = sys.argv[5]

    data_info_path = os.path.realpath(data_info_path)
    result_path = os.path.realpath(result_path)
    save_path = os.path.realpath(save_path)
    coco_name_path = os.path.realpath(coco_name_path)
    imagenet_pic_path = os.path.realpath(imagenet_pic_path)

    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    get_resultpath(data_info_path, result_path, save_path, coco_name_path, imagenet_pic_path)
