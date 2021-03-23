# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Source code:
    https://bbs.huaweicloud.com/blogs/181057
Example:
    python3.7 caffe_dump.py -m resnet50.prototxt -w resnet50.caffemodel -i test.bin -n 'data:0' -o ./output_dir

Guide for setting up Caffe/Tensorflow precision golden data generation environments:
    https://bbs.huaweicloud.com/blogs/181059
"""
import numpy as np
import math
import sys
import os
import argparse
from logging import *
import logging
import tensorflow as tf
import shutil
import time


def errorExit(msg, *args, **kwargs):
    error(msg, *args, **kwargs)
    exit()


def checkConditionExit(condition, msg,  *args, **kwargs):
    if not condition:
        errorExit(msg, *args, **kwargs)


def convertToShape(shapeStr):
    try:
        shape = eval(shapeStr)
    except:
        errorExit("%s shape is invalid", shapeStr)
    return shape


def load_graph(filename):
    with tf.gfile.GFile(filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")
    return graph


def load_inputs(input_bins, input_names, shapes, graph):
    input_bins = input_bins.split(";")
    input_names = input_names.split(";")
    inputs_map = {}
    input_shapes = []
    if shapes != None:
        shapes = shapes.split(";")
        for shape in shapes:
            input_shapes.append(convertToShape(shape))
    checkConditionExit(len(input_names) == len(input_bins), "input_names must have same length with input_bins")
    for i in range(len(input_bins)):
        input_name = input_names[i]
        input = graph.get_tensor_by_name(input_name)
        if len(input_shapes) == 0:
            input_bin = np.fromfile(input_bins[i], np.float32).reshape(input.shape)
        else:
            input_bin = np.fromfile(input_bins[i], np.float32).reshape(input_shapes[i])
        inputs_map[input] = input_bin
    return inputs_map


def load_outputs(dump_all, dump_nodes, graph):
    outputs = []
    if dump_all:
        ops = graph.get_operations()
        output_names = []
        for op in ops:
            op_outputs = op.inputs
            for op_output in op_outputs:
                output_names.append(op_output.name)
        for output_name in output_names:
            node = graph.get_tensor_by_name(output_name)
            outputs.append(node)
    else:
        checkConditionExit(dump_nodes != None, "no dump_nodes provides, %s", dump_nodes)
        dump_nodes = dump_nodes.split(";")
        for dump_node in dump_nodes:
            node = graph.get_tensor_by_name(dump_node)
            outputs.append(node)
    return outputs


def NHWC2NCHW(input):
    result = input.transpose([0, 3, 1, 2])
    return result


def main(args):
    print(args)
    protobuf = args.protobuf
    pb_path = protobuf.name
    graph = load_graph(pb_path)
    input_bins = args.input_bins
    input_names = args.input_names
    shapes = args.shapes
    inputs_map = load_inputs(input_bins, input_names, shapes, graph)
    dump_all = args.dump_all
    outputs = load_outputs(dump_all, None, graph)
    config = tf.ConfigProto(log_device_placement=False, allow_soft_placement=True)
    with tf.Session(graph=graph, config=config) as sess:
        dump_bins = sess.run(outputs, feed_dict=inputs_map)
    pathSep = os.path.sep
    dir_name = os.path.dirname(os.path.abspath(pb_path))
    output_floder = dir_name + pathSep + os.path.basename(pb_path).split('.')[0] + "_dump"
    # print(output_floder)
    if os.path.exists(output_floder):
        info("remove dir %s", output_floder)
        shutil.rmtree(output_floder)
    info("create dir %s", output_floder)
    os.mkdir(output_floder, 755)

    for i in range(len(outputs)):
        output = outputs[i].name
        output = output.replace("/", "_")
        output = output.replace(":", ".")
        prefix = output + "." + str(round(time.time() * 1000000))
        dump_bin = dump_bins[i]
        dump_path = output_floder + pathSep + prefix + ".npy"
        np.save(dump_path, dump_bin)


if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s", level=logging.DEBUG)
    argsParse = argparse.ArgumentParser(
        prog=sys.argv[0], description="This script is dump tensorflow output.only support float32", epilog="Enjoy it.")
    argsParse.add_argument("protobuf", help="protobuf file path",
                           type=argparse.FileType('r', encoding="utf-8"))
    dump_cate_group = argsParse.add_mutually_exclusive_group(required=True)
    argsParse.add_argument("-i", "--input_bins", help="input_bins bins. e.g. './a.bin;./c.bin'", required=True)
    argsParse.add_argument("-n", "--input_names", help="input nodes name. e.g. 'graph_input_0:0;graph_input_0:1'")
    dump_cate_group.add_argument(
        "-a", "--dump_all", help="dump all nodes' outputs. don't use this option for large network \
        if you don't mind when will get all out. in this mode will not dump last layer outputs", action="store_true", default=False)
    argsParse.add_argument(
        "-s", "--shapes", help="input shapes. e.g. [1,2,3,4];[2,3,4,5]. if input is placeholder set input shapes by this.", default=None)
    args = argsParse.parse_args()
    main(args)