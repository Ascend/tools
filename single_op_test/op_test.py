import json
import time

import onnx
import os
import sys

import tbe.common.platform
from google.protobuf import text_format

import argparse

from onnx import numpy_helper
from op_test_frame.ut import OpUT


class Constant:
    CFG_INFO_TYPE_MAP = {
        'DT_FLOAT': 'float',
        'DT_FLOAT16': 'float16',
        'DT_FLOAT32': 'float32',
        'DT_INT8': 'int8',
        'DT_INT16': 'int16',
        'DT_INT32': 'int32',
        'DT_INT64': 'int64',
        'DT_UINT8': 'uint8',
        'DT_UINT16': 'uint16',
        'DT_UINT32': 'uint32',
        'DT_UINT64': 'uint64',
        'DT_BOOL': 'bool',
        "DT_COMPLEX64": "complex64",
        "DT_COMPLEX128": "complex128",
        "DT_DOUBLE": "double"
    }


def parse_args():
    parser = argparse.ArgumentParser(description='test single op.')
    parser.add_argument('--graph', dest="graph_name",
                        help='the graph pre_run after build,exp "ge_onnx_00000141_graph_1_PreRunAfterBuild.pbtxt"')
    parser.add_argument('--node', dest='node_name',
                        help='the node to test, exp "ReduceSum_in_0"')
    parser.add_argument('--bin_path', dest='bin_path', required=False,
                        help='the bin to test, exp "kernel_meta/te_transdata_ff9a78fdaf5103c60_feb5e077cf4dd9cc.o"')
    parser.add_argument('--value_path', dest='value_path', required=False,
                        help='the dump data, exp "/home/HwHiAiUser/dumptonumpy/Pooling.pool1.1147.1589195081588018",'
                        'value_path + "input.x.npy" wil be used for test')
    return parser.parse_args()


class OpUTCase:
    ascend_opp_path = os.environ.get('ASCEND_OPP_PATH') or os.path.join(
        "usr", "local", "Ascend", "opp")
    aic_info_path = os.path.join(
        ascend_opp_path, "op_impl", "built-in", "ai_core", "tbe", "config")

    def __init__(self):
        self.soc_name = None
        self.op_type = None
        self.sys_args = parse_args()

    @staticmethod
    def _convert_attribute_proto(onnx_arg):
        """
        Convert an ONNX AttributeProto into an appropriate Python object
        for the type.
        NB: Tensor attribute gets returned as numpy array
        """
        if onnx_arg.HasField('f'):
            return onnx_arg.f
        elif onnx_arg.HasField('i'):
            return onnx_arg.i
        elif onnx_arg.HasField('s'):
            return onnx_arg.s
        elif onnx_arg.HasField('t'):
            return numpy_helper.to_array(onnx_arg.t)
        elif len(onnx_arg.floats):
            return list(onnx_arg.floats)
        elif len(onnx_arg.ints):
            return list(onnx_arg.ints)
        elif len(onnx_arg.strings):
            return list(onnx_arg.strings)
        else:
            return None

    def get_arg_list(self, soc_name, op_type):
        """
        get args in aic_info.json
        """
        soc_name = soc_name.lower()
        aic_info = os.path.join(
            self.aic_info_path, soc_name, "aic-{}-ops-info.json".format(soc_name))
        with open(aic_info) as aic_info_f:
            aic_info_dict = json.load(aic_info_f)
            op_type_info = aic_info_dict.get(op_type)
            if op_type_info is None:
                return []
            attr_list = op_type_info.get("attr")
            if attr_list is None:
                return []
            return attr_list.get("list").split(",")

    @staticmethod
    def load_graph_def_from_pb(path):
        with open(path, "rb") as f:
            data = f.read()
            model = onnx.ModelProto()
            text_format.Parse(data, model)
        return model.graph

    @staticmethod
    def get_node_input_params(n, i):
        for attr in n.attribute:
            if attr.name == "input_desc_shape:" + str(i):
                shape_attr = attr
            elif attr.name == "input_desc_dtype:" + str(i):
                dtype_attr = attr
            elif attr.name == "input_desc_layout:" + str(i):
                format_attr = attr
            elif attr.name == "input_desc_origin_shape:" + str(i):
                origin_shape_attr = attr
            elif attr.name == "input_desc_origin_dtype:" + str(i):
                origin_dtype_attr = attr
            elif attr.name == "input_desc_origin_layout:" + str(i):
                origin_format_attr = attr
            else:
                continue
        input_param = {"shape": tuple(shape_attr.ints),
                       "dtype": Constant.CFG_INFO_TYPE_MAP.get(dtype_attr.s.decode()),
                       "format": format_attr.s.decode(),
                       "ori_shape": tuple(origin_shape_attr.ints),
                       "ori_dtype": Constant.CFG_INFO_TYPE_MAP.get(origin_dtype_attr.s.decode()),
                       "ori_format": origin_format_attr.s.decode(),
                       "param_type": "input"}
        return input_param

    @staticmethod
    def get_node_output_params(n, i):
        for attr in n.attribute:
            if attr.name == "output_desc_shape:" + str(i):
                shape_attr = attr
            elif attr.name == "output_desc_dtype:" + str(i):
                dtype_attr = attr
            elif attr.name == "output_desc_layout:" + str(i):
                format_attr = attr
            elif attr.name == "output_desc_origin_shape:" + str(i):
                origin_shape_attr = attr
            elif attr.name == "output_desc_origin_dtype:" + str(i):
                origin_dtype_attr = attr
            elif attr.name == "output_desc_origin_layout:" + str(i):
                origin_format_attr = attr
            else:
                continue
        output_param = {"shape": tuple(shape_attr.ints),
                        "dtype": Constant.CFG_INFO_TYPE_MAP.get(dtype_attr.s.decode()),
                        "format": format_attr.s.decode(),
                        "ori_shape": tuple(origin_shape_attr.ints),
                        "ori_dtype": Constant.CFG_INFO_TYPE_MAP.get(origin_dtype_attr.s.decode()),
                        "ori_format": origin_format_attr.s.decode(),
                        "param_type": "output"}
        return output_param

    def get_node_attr_value(self, node, attr_name):
        dst_attr = None
        for attr in node.attribute:
            if (attr.name == attr_name):
                dst_attr = attr
                break
        if not dst_attr:
            return None
        return self._convert_attribute_proto(dst_attr)

    def check_is_dynamic_node(self, node):
        dynamic_attr = None
        for attr in node.attribute:
            if (attr.name == "_is_op_dynamic_impl"):
                dynamic_attr = attr
                break
        if not dynamic_attr:
            return False
        if dynamic_attr.i == 1:
            return True
        return False

    def get_ut_case(self):
        pb_file = self.sys_args.graph_name
        node_name = self.sys_args.node_name
        bin_path = self.sys_args.bin_path
        value_path = self.sys_args.value_path

        graph_def = self.load_graph_def_from_pb(pb_file)

        for node in graph_def.node:
            if node.name != node_name:
                continue

            self.check_is_dynamic_node(node)
            index = 0
            case_params = []
            for input in node.input:
                if len(input) > 2 and input[-2] == '-':
                    continue
                input_param = self.get_node_input_params(node, index)
                if value_path:
                    input_param["value"] = f"{value_path}.input.{index}.npy"
                print("[INPUT:{}]:{}".format(index, input_param))
                case_params.append(input_param)
                index = index + 1

            index = 0
            for out in node.output:
                if len(out) > 2 and out[-2] == '-':
                    continue
                output_param = self.get_node_output_params(node, index)
                print("[OUTPUT:{}]:{}".format(index, output_param))
                case_params.append(output_param)
                index = index + 1

            self.op_type = node.op_type.replace("ge:", "")
            self.soc_name = tbe.common.platform.get_soc_spec(
                "FULL_SOC_VERSION") or "Ascend310"
            # self.soc_name = self.soc_name.lower()
            arg_keys = self.get_arg_list(self.soc_name, self.op_type)
            for arg_key in arg_keys:
                value = self.get_node_attr_value(node, arg_key)
                case_params.append(value)

            case_params = {"params": case_params,
                           "case_name": self.op_type + "autogen_" + time.strftime("%Y%m%d%H%M%S", time.localtime())}
            if bin_path:
                case_params["bin_path"] = bin_path
            return case_params
        return None


if __name__ == "__main__":
    op_ut_case = OpUTCase()
    test_case = op_ut_case.get_ut_case()
    ut_case = OpUT(op_ut_case.op_type, None, None)
    ut_case.add_direct_case(test_case)
    ut_case.run(op_ut_case.soc_name)
