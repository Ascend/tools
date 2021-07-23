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
import numpy as np
import argparse


def read_class_names(class_file_name):
    """
    loads class name from a file
    """
    names = {}
    with open(class_file_name, 'r') as data:
        for id, name in enumerate(data):
            names[id] = name.strip('\n')
    return names


def parse_line(line):
    """
    parse line information
    """
    temp = line.split(" ")
    index = temp[1].split("/")[-1].split(".")[0]
    return index, (int(temp[3]), int(temp[2]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Postprocessing of Yolo-caffe model')
    parser.add_argument("--bin_data_path", default="./pic_1024/", help='Benchamrk output path')
    parser.add_argument("--test_annotation", default="./VOC2017.info", help='Test set annotation file')
    parser.add_argument("--det_results_path", default="./input/detection-results/", help='Output TXT directory')
    parser.add_argument("--coco_class_names", default="./input/coco.names", help='coco dataset classes')
    parser.add_argument("--voc_class_names", default="./input/voc.names", help='vocal dataset classes')
    parser.add_argument("--net_input_width", default=416, help='width of the input image')
    parser.add_argument("--net_input_height", default=416, help='height of the input image')
    flags = parser.parse_args()

    # load the test image info
    img_size_dict = dict()
    with open(flags.test_annotation)as f:
        for line in f.readlines():
            temp = parse_line(line)
            img_size_dict[temp[0]] = temp[1]

    # load label class name
    coco_class_map = read_class_names(flags.coco_class_names)
    coco_set = set(coco_class_map.values())
    voc_class_map = read_class_names(flags.voc_class_names)
    voc_set = set(voc_class_map.values())

    # load the output files
    # "_1.bin" for detinfo
    # "_2.bin" for numbox
    bin_path = flags.bin_data_path
    net_input_width = flags.net_input_width
    net_input_height = flags.net_input_height
    det_results_path = flags.det_results_path
    if not os.path.exists(det_results_path):
        os.makedirs(det_results_path)
    for img_name in img_size_dict:
        boxbuf = []
        boxnum = []
        det_results_str = ""
        path_det_output1 = os.path.join(bin_path, img_name + "_1.bin")
        if os.path.exists(path_det_output1):
            boxbuf = np.fromfile(path_det_output1, dtype="float32")
        else:
            print("[ERROR] file not exist", path_det_output1)
            break
        path_det_output2 = os.path.join(bin_path, img_name + "_2.bin")
        if os.path.exists(path_det_output2):
            boxnum = np.fromfile(path_det_output2, dtype="float32")
        else:
            print("[ERROR] file not exist", path_det_output2)
            break
        boxcnt = boxnum[0].astype(int)
        if(boxcnt == 0):
            det_results_str = ""
        else:
            j = 0
            expect_data_list = []
            pre_box_list = []
            for i in boxbuf[0:boxcnt * 6]:
                expect_data_list.append(round(float(i), 3))
            for i in range(6):
                pre_box_list.append(list(expect_data_list[j:j + boxcnt]))
                j += boxcnt
            for i in range(int(boxcnt)):
                class_ind = int(pre_box_list[5][i])
                if class_ind < 0:
                    print("[ERROR] predicted object class error:", class_ind)
                    continue
                else:
                    class_name = coco_class_map[class_ind]
                    if class_name in voc_set:
                        det_results_str += "{} {} {} {} {} {}\n".format(
                            class_name, str(pre_box_list[4][i]), str(pre_box_list[0][i]),
                            str(pre_box_list[1][i]), str(pre_box_list[2][i]),
                            str(pre_box_list[3][i]))
        det_results_file = os.path.join(det_results_path, img_name + ".txt")
        with open(det_results_file, "w") as detf:
            detf.write(det_results_str)
