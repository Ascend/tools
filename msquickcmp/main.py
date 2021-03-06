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
from onnx_model.onnx_dump_data import OnnxDumpData
from tf.tf_dump_data import TfDumpData


def _accuracy_compare_parser(parser):
    parser.add_argument("-m", "--model-path", dest="model_path", default="",
                        help="<Required> model_path,original model file path,for example,.pb or .onnx", required=True)
    parser.add_argument("-om", "--offline-model-path", dest="offline_model_path", default="",
                        help="<Required> offline model(.om) path", required=True)
    parser.add_argument("-i", "--input-path", dest="input_path", default="",
                        help="<Optional> Input data path of the model,If there are multiple input values,separate them "
                             "with commas (,),like 'input_0,input_1'")
    parser.add_argument("-c", "--cann-path", dest="cann_path", default="/usr/local/Ascend/ascend-toolkit/latest/",
                        help="<Optional> CANN installation path")
    parser.add_argument("-o", "--out-path", dest="out_path", default="", help="<Optional> output result path")


def _generate_cpu_data_model(args):
    model_name, extension = utils.get_model_name_and_extension(args.model_path)
    if ".pb" == extension:
        return TfDumpData(args)
    elif ".onnx" == extension:
        return OnnxDumpData(args)
    else:
        utils.print_error_log("Only model files whose names end with .pb or .onnx are supported")
        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_MODEL_TYPE_ERROR)


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
    utils.check_file_or_directory_path(os.path.realpath(args.out_path), True)
    time_dir = time.strftime("%Y%m%d%H%M%S", time.localtime())
    args.out_path = os.path.realpath(os.path.join(args.out_path, time_dir))
    args.model_path = os.path.realpath(args.model_path)
    args.offline_model_path = os.path.realpath(args.offline_model_path)
    args.cann_path = os.path.realpath(args.cann_path)
    utils.check_file_or_directory_path(args.model_path)
    utils.check_file_or_directory_path(args.offline_model_path)
    try:
        # generate dump data by the original model
        cpu_dump_data_path = _generate_cpu_data_model(args).generate_dump_data()
        # convert the om model to json
        output_json_path = AtcUtils(args).convert_model_to_json()
        # compiling and running source codes
        npu_dump_data_path = NpuDumpData(args, output_json_path).generate_dump_data()
        # compare the entire network
        net_compare = NetCompare(npu_dump_data_path, cpu_dump_data_path, output_json_path, args)
        net_compare.accuracy_network_compare()
        # print the name of the first operator whose cosine similarity is less than o.9
        csv_object_item = net_compare.get_csv_object_by_cosine()
        if csv_object_item is not None:
            utils.print_info_log(
                "{} of the first operator whose cosine similarity is less than o.9".format(
                    csv_object_item.get("LeftOp")))
        else:
            utils.print_info_log("No operator whose cosine value is less then 0.9 exists.")
    except utils.AccuracyCompareException as error:
        sys.exit(error.error_info)


if __name__ == '__main__':
    main()
