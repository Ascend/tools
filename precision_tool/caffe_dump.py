# coding=utf-8
"""
Source code:
    https://bbs.huaweicloud.com/blogs/181056
Example:
    python3.7 caffe_dump.py -m resnet50.prototxt -w resnet50.caffemodel -i test.bin -n 'data:0' -o ./output_dir

Guide for setting up Caffe/Tensorflow precision golden data generation environments:
    https://bbs.huaweicloud.com/blogs/181059
"""
import caffe
import sys
import argparse
import os
import caffe.proto.caffe_pb2 as caffe_pb2
import google.protobuf.text_format
import json
import numpy as np
import time

TIME_LENGTH = 1000
FILE_PERMISSION_FLAG = 0o600


class CaffeProcess:
    def __init__(self):
        parse = argparse.ArgumentParser()
        parse.add_argument("-w", dest="weight_file_path",
                           help="<Required> the caffe weight file path",
                           required=True)
        parse.add_argument("-m", dest="model_file_path",
                           help="<Required> the caffe model file path",
                           required=True)
        parse.add_argument("-o", dest="output_path", help="<Required> the output path",
                           required=True)
        parse.add_argument("-i", "--input_bins", dest="input_bins", help="input_bins bins. e.g. './a.bin;./c.bin'",
                           required=True)
        parse.add_argument("-n", "--input_names", dest="input_names",
                           help="input nodes name. e.g. 'graph_input_0:0;graph_input_0:1'",
                           required=True)
        args, _ = parse.parse_known_args(sys.argv[1:])
        self.weight_file_path = os.path.realpath(args.weight_file_path)
        self.model_file_path = os.path.realpath(args.model_file_path)
        self.input_bins = args.input_bins.split(";")
        self.input_names = args.input_names.split(";")
        self.output_path = os.path.realpath(args.output_path)
        self.net_param = None
        self.cur_layer_idx = -1

    @staticmethod
    def _check_file_valid(path, is_file):
        if not os.path.exists(path):
            print('Error: The path "' + path + '" does not exist.')
            exit(-1)
        if is_file:
            if not os.path.isfile(path):
                print('Error: The path "' + path + '" is not a file.')
                exit(-1)
        else:
            if not os.path.isdir(path):
                print('Error: The path "' + path + '" is not a directory.')
                exit(-1)

    def _check_arguments_valid(self):
        self._check_file_valid(self.model_file_path, True)
        self._check_file_valid(self.weight_file_path, True)
        self._check_file_valid(self.output_path, False)
        for input_file in self.input_bins:
            self._check_file_valid(input_file, True)

    @staticmethod
    def calDataSize(shape):
        dataSize = 1
        for dim in shape:
            dataSize *= dim
        return dataSize

    def _load_inputs(self, net):
        inputs_map = {}
        for layer_name, blob in net.blobs.items():
            if layer_name in self.input_names:
                input_bin = np.fromfile(
                    self.input_bins[self.input_names.index(layer_name)], np.float32)
                input_bin_shape = blob.data.shape
                if self.calDataSize(input_bin_shape) == self.calDataSize(input_bin.shape):
                    input_bin = input_bin.reshape(input_bin_shape)
                else:
                    print("Error: input node data size %d not match with input bin data size %d.", self.calDataSize(
                        input_bin_shape), self.calDataSize(input_bin.shape))
                    exit(-1)
                inputs_map[layer_name] = input_bin
        return inputs_map

    def process(self):
        """
        Function Description:
            process the caffe net, save result as dump data
        """
        # check path valid
        self._check_arguments_valid()

        # load model and weight file
        net = caffe.Net(self.model_file_path, self.weight_file_path,
                        caffe.TEST)
        inputs_map = self._load_inputs(net)
        for key, value in inputs_map.items():
            net.blobs[key].data[...] = value
        # process
        net.forward()

        # read prototxt file
        net_param = caffe_pb2.NetParameter()
        with open(self.model_file_path, 'rb') as model_file:
            google.protobuf.text_format.Parse(model_file.read(), net_param)
        for layer in net_param.layer:
            name = layer.name.replace("/", "_").replace(".", "_")
            index = 0
            for top in layer.top:
                data = net.blobs[top].data[...]
                file_name = name + "." + str(index) + "." + str(
                    round(time.time() * 1000000)) + ".npy"
                output_dump_path = os.path.join(self.output_path, file_name)
                np.save(output_dump_path, data)
                os.chmod(output_dump_path, FILE_PERMISSION_FLAG)
                print('The dump data of "' + layer.name
                      + '" has been saved to "' + output_dump_path + '".')
                index += 1


if __name__ == "__main__":
    caffe_process = CaffeProcess()
    caffe_process.process()