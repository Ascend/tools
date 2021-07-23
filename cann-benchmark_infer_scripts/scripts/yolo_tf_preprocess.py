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
from PIL import Image
import numpy as np


def preprocess(src_info, save_path, side=416):
    """
    yolo tf preprocess
    """
    in_files = []

    with open(src_info, 'r') as file:
        contents = file.read().split('\n')
    for i in contents[:-1]:
        in_files.append(i.split()[1])

    i = 0
    for file in in_files:
        if not os.path.isdir(file):
            i = i + 1
            print(file, "====", i)
            image = Image.open(file).convert('RGB')

            width, height = image.size
            scale = side / max([width, height])
            width_scaled = int(width * scale)
            height_scaled = int(height * scale)
            image_scaled = image.resize((width_scaled, height_scaled),
                                        resample=Image.LANCZOS)
            image_array = np.array(image_scaled, dtype=np.float32)
            image_padded = np.full([side, side, 3], 128, dtype=np.float32)
            width_offset = (side - width_scaled) // 2
            height_offset = (side - height_scaled) // 2
            image_padded[height_offset:height_offset + height_scaled, width_offset:width_offset + width_scaled, :] \
                = image_array
            image_norm = image_padded / 255

            temp_name = file[file.rfind('/') + 1:]
            image_norm.tofile(os.path.join(save_path, temp_name.split('.')[0] + ".bin"))


def check_args(args):
    """
    check arguments
    """
    if not os.path.exists(args.src_info):
        print('-' * 55)
        print("The specified '{}' file does not exist".format(args.src_info))
        print('You can get the correct parameter information from -h')
        print('-' * 55)
        exit()
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocessing of Yolo model')
    parser.add_argument('--src_info', default='./coco2014.info', type=str, help='The file records the pictures'
                                                                                ' that need to be preprocessed')
    parser.add_argument('--save_path', default='./input_bin', type=str, help='Output path, If not exist, create it')
    args = parser.parse_args()
    args = check_args(args)

    preprocess(args.src_info, args.save_path)
