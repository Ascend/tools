#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class is used to om fusion parser.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2021
"""
import itertools
import json
import numpy as np

from common.dump_data import DumpData
from common import utils
from common.utils import AccuracyCompareException

GRAPH_OBJECT = "graph"
OP_OBJECT = "op"
NAME_OBJECT = "name"
TYPE_OBJECT = "type"
INPUT_DESC_OBJECT = "input_desc"
INPUT_OBJECT = "input"
ATTR_OBJECT = "attr"
SHAPE_OBJECT = "shape"
SHAPE_RANGE_OBJECT = "shape_range"
DIM_OBJECT = "dim"
DATA_OBJECT = "Data"
NET_OUTPUT_OBJECT = "NetOutput"
ATC_CMDLINE_OBJECT = "atc_cmdline"
INPUT_SHAPE = "--input_shape"
INPUT_SHAPE_RANGE = "--input_shape_range"
LIST_LIST_INT_OBJECT = 'list_list_int'
LIST_LIST_I_OBJECT = 'list_list_i'
LIST_I_OBJECT = 'list_i'
LIST_OBJECT = 'list'
KEY_OBJECT = "key"
VALUE_OBJECT = "value"
SUBGRAPH_NAME = 'subgraph_name'
S_OBJECT = "s"
DTYPE_OBJECT = "dtype"
DTYPE_MAP = {"DT_FLOAT": np.float32, "DT_FLOAT16": np.float16, "DT_DOUBLE": np.float64, "DT_INT8": np.int8,
             "DT_INT16": np.int16, "DT_INT32": np.int32, "DT_INT64": np.int64, "DT_UINT8": np.uint8,
             "DT_UINT16": np.uint16, "DT_UINT32": np.uint32, "DT_UINT64": np.uint64, "DT_BOOL": np.bool}
OUT_NODES_NAME = "attr_model_out_nodes_name"
# special ops
SPECIAL_OPS_TYPE = ("Cast", "TransData")


class OmParser(object):
    """
    This class is used to parse om model.
    """

    def __init__(self, output_json_path):
        self.json_object = self._load_json_file(output_json_path)
        self.subgraph_name = self._get_sub_graph_name()
        self.shape_range = self._is_input_shape_range()
        self.contain_negative_1 = False
        self.special_op_attr = self._parse_special_op_attr()

    def _get_sub_graph_name(self):
        subgraph_name = []
        for graph in self.json_object.get(GRAPH_OBJECT):
            for operator in graph.get(OP_OBJECT):
                if SUBGRAPH_NAME in operator:
                    subgraph_name += operator.get(SUBGRAPH_NAME)
        return subgraph_name

    def _gen_operator_list(self):
        for graph in self.json_object.get(GRAPH_OBJECT):
            if graph.get(NAME_OBJECT) in self.subgraph_name:
                continue
            for operator in graph.get(OP_OBJECT):
                yield operator

    def get_shape_size(self):
        """
        Get shape size for input
        """
        input_desc_array = self._get_data_input_desc()
        # extracts the input shape value
        return self._process_inputs(input_desc_array)

    @staticmethod
    def _load_json_file(json_file_path):
        """
        Function Description:
            load json file
        Parameter:
            json_file_path: json file path
        Return Value:
            json object
        Exception Description:
            when invalid json file path throw exception
        """
        try:
            with open(json_file_path, "r") as input_file:
                try:
                    return json.load(input_file)
                except Exception as load_input_file_except:
                    print(str(load_input_file_except))
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PARSER_JSON_FILE_ERROR)
        except IOError as input_file_open_except:
            utils.print_error_log('Failed to open"' + json_file_path + '", ' + str(input_file_open_except))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR)

    def _get_data_input_desc(self):
        input_desc_list = []
        for operator in self._gen_operator_list():
            if DATA_OBJECT == operator.get(TYPE_OBJECT):
                if len(operator.get(INPUT_DESC_OBJECT)) != 0:
                    for item in operator.get(INPUT_DESC_OBJECT):
                        input_desc_list.append(item)
        return input_desc_list

    def get_net_output_count(self):
        """
        Get net output count
        """
        count = 0
        for operator in self._gen_operator_list():
            if NET_OUTPUT_OBJECT == operator.get(TYPE_OBJECT) and INPUT_DESC_OBJECT in operator:
                count += len(operator.get(INPUT_DESC_OBJECT))
        return count

    @staticmethod
    def _get_prefix(input_obj):
        return input_obj.split(':')[0]

    def _parse_special_op_attr(self):
        special_op_attr = {}
        for operator in self._gen_operator_list():
            if operator.get(TYPE_OBJECT) in SPECIAL_OPS_TYPE:
                special_op_attr[operator.get(NAME_OBJECT)] = operator.get(INPUT_OBJECT)
        return special_op_attr

    def get_expect_net_output_name(self):
        """
        Get the expected output tensor corresponding to Net_output.
        """
        expect_net_output_name = {}
        net_output_names = []
        if ATTR_OBJECT not in self.json_object:
            return expect_net_output_name
        for attr in self.json_object.get(ATTR_OBJECT):
            if not (KEY_OBJECT in attr and attr.get(KEY_OBJECT) == OUT_NODES_NAME):
                continue
            if not (VALUE_OBJECT in attr and LIST_OBJECT in attr.get(VALUE_OBJECT)):
                continue
            list_object = attr.get(VALUE_OBJECT).get(LIST_OBJECT)
            if S_OBJECT in list_object:
                net_output_names = list_object.get(S_OBJECT)
        for item, output_name in enumerate(net_output_names):
            expect_net_output_name[item] = output_name
        return expect_net_output_name

    @staticmethod
    def _parse_net_output_node_attr(operator):
        net_output_info = {}
        if INPUT_DESC_OBJECT in operator:
            input_index = 0
            for input_object in operator.get(INPUT_DESC_OBJECT):
                shape = []
                data_type = DTYPE_MAP.get(input_object.get(DTYPE_OBJECT))
                for num in input_object.get(SHAPE_OBJECT).get(DIM_OBJECT):
                    shape.append(num)
                net_output_info[input_index] = [data_type, shape]
                input_index += 1
        return net_output_info

    def get_net_output_data_info(self):
        """
        get_net_output_data_info
        """
        for operator in self._gen_operator_list():
            if NET_OUTPUT_OBJECT == operator.get(TYPE_OBJECT):
                return self._parse_net_output_node_attr(operator)

    def _is_input_shape_range(self):
        if ATTR_OBJECT not in self.json_object:
            return False
        for attr in self.json_object.get(ATTR_OBJECT):
            if KEY_OBJECT in attr and attr.get(KEY_OBJECT) == ATC_CMDLINE_OBJECT:
                if VALUE_OBJECT in attr and S_OBJECT in attr.get(VALUE_OBJECT):
                    if INPUT_SHAPE_RANGE in attr.get(VALUE_OBJECT).get(S_OBJECT):
                        return True
        return False

    def _get_range_shape_size_list(self, input_object):
        range_shape_size_list = []
        if ATTR_OBJECT not in input_object:
            return
        shape_list = []
        for attr in input_object.get(ATTR_OBJECT):
            if KEY_OBJECT in attr and attr.get(KEY_OBJECT) == SHAPE_RANGE_OBJECT:
                if VALUE_OBJECT in attr and attr.get(VALUE_OBJECT) and LIST_LIST_INT_OBJECT in attr.get(VALUE_OBJECT):
                    list_list_int_object = attr.get(VALUE_OBJECT).get(LIST_LIST_INT_OBJECT)
                    if LIST_LIST_I_OBJECT in list_list_int_object:
                        for list_list_i in list_list_int_object.get(LIST_LIST_I_OBJECT):
                            if LIST_I_OBJECT in list_list_i:
                                list_i = list_list_i.get(LIST_I_OBJECT)
                                if -1 in list_i:
                                    self.contain_negative_1 = True
                                    return []
                                if len(list_i) != 2:
                                    continue
                                shape_list.append(list(range(list_i[0], list_i[1] + 1)))
        shape_list_all = list(itertools.product(*shape_list))
        for item in shape_list_all:
            item_sum = 1
            for num in item:
                item_sum *= num
            range_shape_size_list.append(item_sum)
        return range_shape_size_list

    def _process_inputs(self, input_desc_array):
        value = []
        for input_object in input_desc_array:
            if SHAPE_OBJECT not in input_object:
                value.append(0)
                continue
            data_type = DTYPE_MAP.get(input_object.get(DTYPE_OBJECT))
            if not data_type:
                utils.print_error_log(
                    "The dtype attribute does not support {} value.".format(input_object[DTYPE_OBJECT]))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_KEY_ERROR)
            data_type_size = np.dtype(data_type).itemsize
            if self.shape_range:
                range_shape_size_list = self._get_range_shape_size_list(input_object)
                for item in range_shape_size_list:
                    value.append(item * data_type_size)
            else:
                item_sum = 1
                for num in input_object.get(SHAPE_OBJECT).get(DIM_OBJECT):
                    item_sum *= num
                value.append(item_sum * data_type_size)
        return value
