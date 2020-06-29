# !/usr/bin/env python2
# -*- coding: UTF-8 -*-
#
#   =======================================================================
#
# Copyright (C) 2018, Hisilicon Technologies Co., Ltd. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1 Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   2 Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   3 Neither the names of the copyright holders nor the names of the
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#   =======================================================================
from __future__ import print_function
import argparse
import ConfigParser as configparser
import json
import os
import sys
import commands

try:
    import cv2 as cv 
except:
    ret, output = commands.getstatusoutput('whoami')
    if output != 'root':
        print('[ERROR] opencv-python not installed.')
        print("[ERROR] Please use the root user to execute this script again")
        exit(0)
    print('begin to install opencv-python...') 
    ret = os.system('yum install -y opencv-python')
    if ret != 0:
        ret = os.system('apt-get install -y python-opencv')
        if ret != 0:
            print('[ERROR] install opencv-python failed,please check env.')
            exit(0)
    import cv2 as cv
try:
    import numpy as np  
except:
    os.system('pip2 install numpy')
    import numpy as np 

def get_args():
    parser = argparse.ArgumentParser(
        conflict_handler='resolve',
        description='''eg1: python2 imgtobin.py
         -i ./images -w 416 -h 416 -f BGR -a NHWC -t uint8 -m [104,117,123] -c [1,1,1] -o ./out 
         eg2: python2 imgtobin.py -i ./test.txt -t uint8 -o ./out''')
    parser.add_argument('-i', '--input', required=True, type=str, \
        help='folder of input image or file of other input.')
    parser.add_argument('-w', '--width', type=int, \
        help='resized image width before inference.')
    parser.add_argument('-h', '--height', type=int, \
        help='resized image height before inference.')
    parser.add_argument('-f', '--output_image_format', default='BGR', type=str, \
        help='output image format in (BGR/RGB/YUV/GRAY).')
    parser.add_argument('-a', '--output_format', default='NCHW', type=str, \
        help='output format in (NCHW/NHWC).')
    parser.add_argument('-t', '--output_type', required=True, type=str, \
        help='output type in (float32/uint8/int32/uint32).')
    parser.add_argument('-m', '--mean', default='[0, 0, 0]', \
        help='reduce mean for each channel.')   
    parser.add_argument('-c', '--coefficient', default='[1, 1, 1]', \
        help='multiplying coefficients for each channel.')
    parser.add_argument('-o', '--output', default='./', \
        help='output path.')
    return parser.parse_args()


def eprint(*args, **kwargs):
    """print error message to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


def check_args(args):
    """check console parameters according to restrictions.
    :return: True or False
    """
    check_flag = True
    is_dir = True  
    if os.path.isdir(args.input):
        if not os.listdir(args.input):
            eprint('[ERROR] input image path=%r is empty.' % args.input)
            check_flag = False
    elif os.path.isfile(args.input):
        is_dir = False
    else:
        eprint('[ERROR] input path=%r does not exist.' % args.input)
        check_flag = False
    if args.output_image_format not in ('BGR','RGB', 'YUV', 'GRAY'):
        eprint("ERROR:Convert to %d is not support"%(args.output_image_format))
        check_flag = False
    return check_flag, is_dir
   


def convert_img(args, input_img):
    if args.output_image_format == 'BGR':
        converted_input_img = input_img
    elif args.output_image_format == 'RGB':
        converted_input_img = cv.cvtColor(input_img, cv.COLOR_BGR2RGB)
    elif args.output_image_format == 'YUV':
        if input_img.shape[0] % 2 == 1:
            if input_img.shape[1] % 2 == 1:
                input_img = cv.resize(input_img, ((input_img.shape[0] + 1), (input_img.shape[1] + 1)))
            else:
                input_img = cv.resize(input_img, ((input_img.shape[0] + 1), input_img.shape[1]))
        elif input_img.shape[1] % 2 == 1:
            input_img = cv.resize(input_img, (input_img.shape[0], input_img.shape[1] + 1))
        converted_input_img = cv.cvtColor(input_img, cv.COLOR_BGR2YUV_I420)
    elif args.output_image_format == 'GRAY':
        converted_input_img = cv.cvtColor(input_img, cv.COLOR_BGR2GRAY)
    return converted_input_img
        

def resize_img(args, input_img):
    resized_img = cv.resize(input_img, (args.width, args.height))
    return resized_img


def change_type(args, input_img):
    if args.output_type == 'float32':
        change_type_img = input_img.astype(np.float32)
    elif args.output_type == 'int32':
        change_type_img = input_img.astype(np.int32)
    elif args.output_type == 'uint32':
        change_type_img = input_img.astype(np.uint32)
    else:
        change_type_img = input_img.astype(np.uint8)
    return change_type_img


def mean(args, input_img):
    if isinstance (args.mean, str):
        args.mean = json.loads(args.mean)
    input_img = input_img.astype(np.float32)
    if args.output_image_format == 'GRAY':
        input_img[:, :] -= args.mean[0]
    elif args.output_image_format in ('BGR', 'RGB'):
        input_img[:, :, 0] -= args.mean[0]
        input_img[:, :, 1] -= args.mean[1]
        input_img[:, :, 2] -= args.mean[2]
    else:
        input_img[: int(args.width / 1.5), :] -= args.mean[0]
        input_img[int(args.width / 1.5) :, :: 2] -= args.mean[1]
        input_img[int(args.width / 1.5) :, 1: 2] -= args.mean[2]
    return input_img


def coefficient(args, input_img):
    if isinstance (args.coefficient, str):
        args.coefficient = json.loads(args.coefficient)
    input_img = input_img.astype(np.float32)
    if args.output_image_format == 'GRAY':
        input_img[:, :] *= args.coefficient[0]
    elif args.output_image_format in ('BGR', 'RGB'):
        input_img[:, :, 0] *= args.coefficient[0]
        input_img[:, :, 1] *= args.coefficient[1]
        input_img[:, :, 2] *= args.coefficient[2]
    else:
        input_img[: int(args.width / 1.5), :] *= args.coefficient[0]
        input_img[int(args.width / 1.5) :, :: 2] *= args.coefficient[1]
        input_img[int(args.width / 1.5) :, 1: 2] *= args.coefficient[2]
    return input_img


def change_format(args, input_img):
    if args.output_format == 'NCHW':
        if args.output_image_format in ('RGB', 'BGR'):
            change_format_img = input_img.transpose(2,0,1).copy()        
            return change_format_img
    return input_img


def mkdir_output(args):
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    return


def process(args, file_path):
    if file_path.endswith(".txt"):
        config = configparser.ConfigParser()
        config.read(file_path)
        input_node = json.loads(config['baseconf']['input_node'])
        shape = json.loads(config['baseconf']['shape'])
        input_node_np = np.array(input_node)
        change_type_img_info = change_type(args, input_node_np)
        img_info = np.reshape(change_type_img_info, shape)
        out_path = os.path.join(args.output, os.path.splitext(os.path.split(file_path)[1])[0] + ".bin")
        mkdir_output(args)
        img_info.tofile(out_path) 
    else:
        input_img = cv.imread(file_path) 
        if args.output_image_format == 'YUV':
            resized_img1 = resize_img(args, input_img) 
            converted_img = convert_img(args, resized_img1) 
            mean_img = mean(args, converted_img)
        else: 
            converted_img = convert_img(args, input_img)    
            resized_img = resize_img(args, converted_img)  
            mean_img = mean(args, resized_img)
        coefficient_img = coefficient(args, mean_img)
        change_type_img = change_type(args, coefficient_img)
        change_format_img = change_format(args, change_type_img)
        out_path = os.path.join(args.output, os.path.splitext(os.path.split(file_path)[1])[0] + ".bin")
        mkdir_output(args)
        change_format_img.tofile(out_path)
        

def main():
    """main function to receive params them change data to bin.
    """
    args = get_args()
    ret,is_dir = check_args(args)
    if ret:
        if is_dir:
            files_name = os.listdir(args.input)
            for file_name in files_name:
                file_path = os.path.join(args.input, file_name)
                process(args, file_path)  
        else:
            process(args, args.input)    


if __name__ == '__main__':
    main()


