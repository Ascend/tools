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

import os
import argparse


def cre_groundtruth_dict(gtfile_path):
    """
    :param filename: file contains the label and original data
    :return: dictionary key imagename, value is label number
    """
    tocken_labels = []
    with open(gtfile_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            tocken_labels.append(line.split('\t')[0])

    return tocken_labels


def load_statistical_predict_result(filepath):
    """
    function:
    the prediction esult file data extraction
    input:
    result file:filepath
    :return: probabilities
    """
    tocken_labels = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            print(filepath)
            left = line.split(' ')[0]
            right = line.split(' ')[1]
            tocken_labels.append(float(left))
            tocken_labels.append(float(right))
    return tocken_labels


def create_visualization_statistical_result(prediction_file_path,
                                            result_file,
                                            tocken_labels):
    """
    :param prediction_file_path:
    :param result_file:
    :param tocken_labels:
    :return: None
    """
    perfFilename = result_file
    count = 0
    resCnt = 0
    for tfile_name in os.listdir(prediction_file_path):
        temp = tfile_name.split('.')[0]
        index = temp.split('_')[1]
        if tfile_name.split('.')[1] == "txt":
            count += 1
            filepath = os.path.join(prediction_file_path, tfile_name)
            ret = load_statistical_predict_result(filepath)
            prediction0 = ret[0]
            prediction1 = ret[1]
            if prediction0 > prediction1:
                result = 0
            else:
                result = 1
            label = tocken_labels[int(index)]
            print("index:", index, " label: ", label, " predict: ", result)
            if int(index) == 0:
                resCnt += 1
            elif int(label.split(' ')[0]) == result:
                resCnt += 1

    print("rightNum: " + str(resCnt) + '\n' + "toatlNum: " + str(count) + '\n' + "rightRate: " + str(resCnt / count))
    with open(perfFilename, "w") as f:
        f.write(
            "rightNum: " + str(resCnt) + '\n' + "toatlNum: " + str(count) + '\n' + "rightRate: " + str(resCnt / count))
    print("result saved in " + perfFilename)


def check_args(args):
    """
        :param args:
        :return: args
    """
    if not (os.path.exists(args.anno_file)):
        print("annotation file:{} does not exist.".format(args.anno_file))
        exit()

    if not (os.path.exists(args.benchmark_out)):
        print("benchmark output:{} does not exist.".format(args.benchmark_out))
        exit()

    return args


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Precision statistics of Bert_base model')
    parser.add_argument("--anno_file", default="./data.txt", help='annotation file')
    parser.add_argument("--benchmark_out", default="result/dumpOutput_device0", help='Benchmark output directory')
    parser.add_argument("--result_file", default="./result_BERT_Base.txt", help='Output TXT file')
    args = parser.parse_args()
    args = check_args(args)
    tocken_labels = cre_groundtruth_dict(args.anno_file)
    create_visualization_statistical_result(args.benchmark_out, args.result_file, tocken_labels)
