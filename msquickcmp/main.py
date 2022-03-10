#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves the main function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""

import argparse
import os
import sys
import time

from atc.atc_utils import AtcUtils
from common import utils
from common.utils import AccuracyCompareException

from compare.net_compare import NetCompare
from npu.npu_dump_data import NpuDumpData


def _accuracy_compare_parser(parser):
    parser.add_argument("-m", "--model-path", dest="model_path", default="",
                        help="<Required> The original model (.onnx or .pb) file path", required=True)
    parser.add_argument("-om", "--offline-model-path", dest="offline_model_path", default="",
                        help="<Required> The offline model (.om) file path", required=True)
    parser.add_argument("-i", "--input-path", dest="input_path", default="",
                        help="<Optional> The input data path of the model. Separate multiple inputs with commas(,)."
                             " E.g: input_0.bin,input_1.bin")
    parser.add_argument("-c", "--cann-path", dest="cann_path", default="/usr/local/Ascend/ascend-toolkit/latest/",
                        help="<Optional> The CANN installation path")
    parser.add_argument("-o", "--out-path", dest="out_path", default="", help="<Optional> The output path")
    parser.add_argument("-s", "--input-shape", dest="input_shape", default="",
                        help="<Optional> Shape of input shape. Separate multiple nodes with semicolons(;)."
                             " E.g: input_name1:1,224,224,3;input_name2:3,300")
    parser.add_argument("-d", "--device", dest="device", default="0",
                        help="<Optional> Input device ID [0, 255], default is 0.")
    parser.add_argument("--output-size", dest="output_size", default="",
                        help="<Optional> The size of output. Separate multiple sizes with commas(,)."
                             " E.g: 10200,34000")
    parser.add_argument("--output-nodes", dest="output_nodes", default="",
                        help="<Optional> Output nodes designated by user. Separate multiple nodes with semicolons(;)."
                             " E.g: node_name1:0;node_name2:1;node_name3:0")


def _generate_golden_data_model(args):
    model_name, extension = utils.get_model_name_and_extension(args.model_path)
    if ".pb" == extension:
        from tf.tf_dump_data import TfDumpData
        return TfDumpData(args)
    elif ".onnx" == extension:
        from onnx_model.onnx_dump_data import OnnxDumpData
        return OnnxDumpData(args)
    else:
        utils.print_error_log("Only model files whose names end with .pb or .onnx are supported")
        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_MODEL_TYPE_ERROR)


def _correct_the_wrong_order(left_index, right_index, golden_net_output_info):
    if left_index != right_index:
        tmp = golden_net_output_info[left_index]
        golden_net_output_info[left_index] = golden_net_output_info[right_index]
        golden_net_output_info[right_index] = tmp
        utils.print_info_log("swap the {} and {} item in golden_net_output_info!"
                             .format(left_index, right_index))


def _check_output_node_name_mapping(original_net_output_node, golden_net_output_info):
    for left_index, node_name in original_net_output_node.items():
        match = False
        for right_index, dump_file_path in golden_net_output_info.items():
            dump_file_name = os.path.basename(dump_file_path)
            if dump_file_name.startswith(node_name.replace("/", "_").replace(":", ".")):
                match = True
                _correct_the_wrong_order(left_index, right_index, golden_net_output_info)
                break
        if not match:
            utils.print_warn_log("the original name: {} of net output maybe not correct!".format(node_name))
            break


def main():
    """
   Function Description:
       main process function
   Exception Description:
       exit the program when an AccuracyCompare Exception  occurs
   """
    parser = argparse.ArgumentParser()
    _accuracy_compare_parser(parser)
    args = parser.parse_args(sys.argv[1:])
    args.model_path = os.path.realpath(args.model_path)
    args.offline_model_path = os.path.realpath(args.offline_model_path)
    args.cann_path = os.path.realpath(args.cann_path)
    try:
        utils.check_file_or_directory_path(os.path.realpath(args.out_path), True)
        time_dir = time.strftime("%Y%m%d%H%M%S", time.localtime())
        args.out_path = os.path.realpath(os.path.join(args.out_path, time_dir))
        utils.check_file_or_directory_path(args.model_path)
        utils.check_file_or_directory_path(args.offline_model_path)
        utils.check_device_param_valid(args.device)
        # generate dump data by the original model
        golden_dump = _generate_golden_data_model(args)
        golden_dump_data_path = golden_dump.generate_dump_data()
        golden_net_output_info = golden_dump.get_net_output_info()
        # convert the om model to json
        output_json_path = AtcUtils(args).convert_model_to_json()
        # compiling and running source codes
        npu_dump = NpuDumpData(args, output_json_path)
        npu_dump_data_path, npu_net_output_data_path = npu_dump.generate_dump_data()
        expect_net_output_node = npu_dump.get_expect_output_name()
        # compare the entire network
        net_compare = NetCompare(npu_dump_data_path, golden_dump_data_path, output_json_path, args)
        net_compare.accuracy_network_compare()
        # Check and correct the mapping of net output node name.
        _check_output_node_name_mapping(expect_net_output_node, golden_net_output_info)
        net_compare.net_output_compare(npu_net_output_data_path, golden_net_output_info)
        # print the name of the first operator whose cosine similarity is less than 0.9
        csv_object_item = net_compare.get_csv_object_by_cosine()
        if csv_object_item is not None:
            utils.print_info_log(
                "{} of the first operator whose cosine similarity is less than 0.9".format(
                    csv_object_item.get("LeftOp")))
        else:
            utils.print_info_log("No operator whose cosine value is less then 0.9 exists.")
    except utils.AccuracyCompareException as error:
        sys.exit(error.error_info)


if __name__ == '__main__':
    main()
