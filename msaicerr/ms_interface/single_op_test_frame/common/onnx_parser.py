import json
import time

import onnx
import os
import sys

import tbe.common.platform
from google.protobuf import text_format

ascend_opp_path = os.environ.get('ASCEND_OPP_PATH') or "/usr/local/Ascend/latest/opp"
aic_info_path = os.path.join(ascend_opp_path, "op_impl", "built-in", "ai_core", "tbe", "config")


def get_arg_list(self, soc_name, op_type):
    """
    解析某一个信息库文件，获取arg列表
    """
    soc_name = soc_name.lower()
    op_type = op_type.replace("ge:", "")
    aic_info = os.path.join(aic_info_path, soc_name, "aic-{}-ops-info.json".format(self.soc_name))
    with open(aic_info) as aic_info_f:
        aic_info_dict = json.load(aic_info_f)
        op_type_info = aic_info_dict.get(op_type)
        if op_type_info is None:
            return []
        attr_list = op_type_info.get("attr")
        if attr_list is None:
            return []
        return attr_list.get("list").split(",")
    return []


def load_graph_def_from_pb(path):
    with open(path, "rb") as f:
        data = f.read()
        model = onnx.ModelProto()
        text_format.Parse(data, model)
    return model.graph


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
        elif attr.name == "input_desc_origin_dtype" + str(i):
            origin_dtype_attr = attr
        elif attr.name == "input_desc_origin_layout" + str(i):
            origin_format_attr = attr
        else:
            continue
    input_param = {"shape":tuple(shape_attr.ints),
                   "dtype":dtype_attr.s.decode(),
                   "format": format_attr.s.decode(),
                   "ori_shape": tuple(origin_shape_attr.ints),
                   "ori_dtype": origin_dtype_attr.s.decode(),
                   "ori_format": origin_format_attr.s.decode(),
                   "param_type":"input"}
    return input_param

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
        elif attr.name == "output_desc_origin_dtype" + str(i):
            origin_dtype_attr = attr
        elif attr.name == "output_desc_origin_layout" + str(i):
            origin_format_attr = attr
        else:
            continue
    output_param = {"shape":tuple(shape_attr.ints),
                   "dtype":dtype_attr.s.decode(),
                   "format": format_attr.s.decode(),
                   "ori_shape": tuple(origin_shape_attr.ints),
                   "ori_dtype": origin_dtype_attr.s.decode(),
                   "ori_format": origin_format_attr.s.decode(),
                   "param_type":"output"}
    return output_param

def get_node_attr_value(node, attr_name):
    dst_attr = None
    for attr in node.attribute:
        if (attr.name == attr_name):
            dst_attr = attr
    if not dst_attr:
        return None
    return dst_attr.int

def check_is_dynamic_node(node):
    for attr in node.attribute:
        if (attr.name == "_is_op_dynamic_impl"):
            dynamic_attr = attr
            break
    if not dynamic_attr:
        return False
    if dynamic_attr.i == 1:
        return True
    return False


if __name__ == "__main__":
    # pb_file =  sys.argv[1]
    pb_file = "/home/workspace/ge_onnx_00355_graph_51_Build.pbtxt"
    graph_def = load_graph_def_from_pb(pb_file)

    for node in graph_def.node:
        if node.name != "trans_TransData_2780":
            continue

        check_is_dynamic_node(node)
        index = 0
        case_params = []
        for input in node.input:
            if len(input) > 2 and input[-2] == '-':
                continue
            input_param = get_node_input_params(node, index)
            print("[INPUT:{}]:{}".format(index, input_param))
            case_params.append(input_param)
            index = index + 1

        index = 0
        for out in node.output:
            if len(out) > 2 and out[-2] == '-':
                continue
            output_param = get_node_output_params(node. index)
            print("[OUTPUT:{}]:{}".format(index, output_param))
            case_params.append(output_param)
            index = index + 1

        op_type = node.op_type
        soc_name = tbe.common.platform.get_soc_spec("FULL_SOC_VERSION") or "ascend310"
        arg_keys = get_arg_list(soc_name, op_type)
        for arg_key in arg_keys:
            value = get_node_attr_value(node, arg_key)
            case_params.append(value)

        test_case = {}
        test_case["params"] = case_params
        test_case["case_name"] = op_type + "_auto_gen_" + time.strftime("%Y%m%d%H%M%S", time.localtime())
        test_case["bin_path"] = None


