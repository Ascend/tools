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
import argparse
import xml.etree.ElementTree as ET


CLASSES = ('aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car',
                'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
                'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor')

def parse_info(idx, jpg_name, img_path, ann_path, gtp, info):
    key_name = jpg_name.split('.')[0]
    xml_name = os.path.join(ann_path, key_name + '.xml')
    #parse xml
    tree = ET.parse(xml_name)
    root = tree.getroot()
    size = root.find('size')
    width = size.find('width').text
    height = size.find('height').text
    info.write('{} {} {} {}'.format(idx, os.path.join(img_path, jpg_name), width, height))
    info.write('\n')

    with open('{}/{}'.format(gtp, key_name + '.txt'), 'w') as f:
        for obj in root.iter('object'):
            difficult = int(obj.find('difficult').text)
            cls_name = obj.find('name').text.strip().lower()
            if cls_name not in CLASSES:
                continue
            xml_box = obj.find('bndbox')
            xmin = (float(xml_box.find('xmin').text))
            ymin = (float(xml_box.find('ymin').text))
            xmax = (float(xml_box.find('xmax').text))
            ymax = (float(xml_box.find('ymax').text))

            if difficult:
                comment = '{} {} {} {} {} {}'.format(cls_name, xmin, ymin, xmax, ymax, 'difficult')
            else:
                comment = '{} {} {} {} {}'.format(cls_name, xmin, ymin, xmax, ymax)
            f.write(comment)
            f.write('\n')

def main(arg):
    """
    @description: main process
    @param arg  input parameters
    @return none
    """
    info = open('./VOC2007.info', 'w')
    cls = open('./voc.names', 'w')
    for i in CLASSES:
        cls.write(i)
        cls.write('\n')

    for idx, jpg_name in enumerate(os.listdir(arg.img_path)):
        parse_info(idx, jpg_name, arg.img_path, arg.ann_path, arg.gtp, info)


def err_msg(msg):
    """
    @description: error printing packaging function
    @param msg  error message
    @return none
    """
    print('-' * 55)
    print("The specified '{}' file does not exist".format(msg))
    print('You can get the correct parameter information from -h')
    print('-' * 55)
    exit()


def check_args(args):
    """
    @description: check arguments
    @param args  jpg file path
    @return args
    """
    if not os.path.exists(args.img_path):
        err_msg(args.img_path)
    if not os.path.exists(args.ann_path):
        err_msg(args.ann_path)
    if not os.path.exists(args.gtp):
        os.makedirs(args.gtp)
    return args


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse the VOC2007 dataset label')
    parser.add_argument("--img_path", default="JPEGImages", help='The image path')
    parser.add_argument("--ann_path", default="Annotations", help='Origin xml path')
    parser.add_argument("--gtp", default="ground-truth/", help='The ground true file path')
    args = parser.parse_args()
    args = check_args(args)
    main(args)