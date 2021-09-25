# coding=utf-8
import json
import re
from typing import List
from lib.desc import InputDesc
from lib.desc import OutputDesc
from lib.util import util
from lib.constant import Constant
from lib.precision_tool_exception import PrecisionToolException

NO_INPUT_NODES = ['Data', 'AtomicAddrClean', 'Recv', 'Constant']
NO_OUTPUT_NODES = ['Send', 'Recv', 'NetOutput']

JSON_KEY_NAME = 'name'
JSON_KEY_TYPE = 'type'
JSON_KEY_ATTR = 'attr'
JSON_KEY = 'key'
JSON_VALUE = 'value'
JSON_KEY_LIST = 'list'
JSON_KEY_STR = 's'
JSON_KEY_PASS_NAME = 'pass_name'
JSON_KEY_DATA_DUMP_ORIGINAL_OP_NAMES = '_datadump_original_op_names'
JSON_KEY_GE_ATTR_OP_KERNEL_LIB_NAME = "_ge_attr_op_kernel_lib_name"

KERNEL_NAME_SHUFFIX = '_kernelname'


class Op(object):
    """ Op class.
        name: op name
        type: op type
        inputs: list of input descs
        outputs: list of output descs
    """
    def __init__(self, op_json, op_list, graph_name):
        """Init"""
        self.op_json = op_json
        self.op_list = op_list
        self.graph_name = graph_name
        self.input_list = None
        self.output_list = None
        self.log = util.get_log()

    def name(self):
        """Get op name"""
        return self.op_json[JSON_KEY_NAME]

    def json(self):
        return json.dumps(self.op_json, indent=2)

    def type(self):
        """Get op type"""
        return self.op_json[JSON_KEY_TYPE]

    def inputs(self):
        """Get the input list"""
        if self.input_list is None:
            self._parse_inputs()
        return self.input_list

    def outputs(self):
        """Get output list"""
        if self.output_list is None:
            self._parse_outputs()
        return self.output_list

    def pass_name(self):
        return self._attr(JSON_KEY_PASS_NAME)

    def kernel_name(self):
        return self._attr(self.name() + KERNEL_NAME_SHUFFIX)

    def ge_attr_op_kernel_lib_name(self):
        return self._attr(JSON_KEY_GE_ATTR_OP_KERNEL_LIB_NAME)

    def data_dump_original_op_names(self):
        return self._attr(JSON_KEY_DATA_DUMP_ORIGINAL_OP_NAMES)

    def _attr(self, key):
        if JSON_KEY_ATTR in self.op_json:
            for attr in self.op_json[JSON_KEY_ATTR]:
                if key == attr[JSON_KEY]:
                    if JSON_KEY_STR in attr[JSON_VALUE]:
                        return attr[JSON_VALUE][JSON_KEY_STR]
                    elif JSON_KEY_LIST in attr[JSON_VALUE]:
                        if JSON_KEY_STR in attr[JSON_VALUE][JSON_KEY_LIST]:
                            return attr[JSON_VALUE][JSON_KEY_LIST][JSON_KEY_STR]
                    else:
                        self.log.warning("Unknown attr format: %s", attr[JSON_VALUE])
        return ''

    def compare(self, right_op):
        """Compare with another op"""
        if not isinstance(right_op, Op):
            raise PrecisionToolException("Should compare with another op.")
        res_str = ['LeftOp(Type/Name) : [green][%s][/green] %s' % (self.type(), self.name()),
                   'RightOp(Type/Name): [green][%s][/green] %s' % (right_op.type(), right_op.name())]
        similar = True
        if len(self.inputs()) != len(right_op.inputs()):
            res_str.append("Input: [yellow]Input num mismatch.[/yellow]")
        else:
            res_str.append("Input:")
        for left_input in self.inputs():
            for right_input in right_op.inputs():
                if left_input.idx() != right_input.idx():
                    continue
                txt, input_similar = left_input.compare(right_input)
                res_str.append(' - ' + txt)
                similar = similar and input_similar
        if len(self.outputs()) != len(right_op.outputs()):
            res_str.append("Output: [yellow]Output num mismatch.[/yellow]")
        else:
            res_str.append("Output:")
        for left_output in self.outputs():
            for right_output in right_op.outputs():
                if left_output.idx() != right_output.idx():
                    continue
                txt, output_similar = left_output.compare(right_output)
                res_str.append(' - ' + txt)
                similar = similar and output_similar
        return Constant.NEW_LINE.join(res_str), similar

    def summary(self, origin_txt=False):
        """Summary of current op"""
        res_str = ['Op(Type/Name): [green][%s][/green] %s' % (self.type(), self.name()),
                   'KernelName:    [yellow]%s[/yellow]' % self.kernel_name(),
                   'KernelLibName: [yellow]%s[/yellow]' % self.ge_attr_op_kernel_lib_name(),
                   'GraphName:     [yellow]%s[/yellow]' % self.graph_name]
        pass_name = self.pass_name()
        if pass_name != '':
            res_str.append('PassName: [yellow]%s[/yellow]' % pass_name)
        origin_op = self.data_dump_original_op_names()
        if origin_op != '':
            res_str.append('OriginalOp: %s' % origin_op)
        res_str.append('Input:%s' % InputDesc.summary.__doc__)
        for i in self.inputs():
            res_str.append(' -' + i.summary(origin_txt))
        res_str.append('Output:')
        for i in self.outputs():
            res_str.append(' -' + i.summary(origin_txt))
        return Constant.NEW_LINE.join(res_str)

    def _parse_inputs(self):
        """ parse input desc in graph """
        self.input_list = []
        if 'input' not in self.op_json:
            if self.type() not in NO_INPUT_NODES:
                self.log.warning('Parse Op[%s][%s] inputs error.' % (self.type(), self.name()))
            return self.input_list
        desc_index = 0
        for i in range(len(self.op_json['input'])):
            name = self.op_json['input'][i]
            if name == '':
                # if self.type() not in NO_INPUT_NODES:
                # self.log.warning('invalid input name.')
                continue
            name_info = name.split(':')
            if len(name_info) == 2 and int(name_info[1]) == -1:
                # control edge
                self.input_list.append(InputDesc(name, [], i))
            else:
                self.input_list.append(InputDesc(name, self.op_json['input_desc'][desc_index], i))
                desc_index += 1
        self.input_list.sort(key=lambda x: x.index)
        return self.input_list

    def _parse_outputs(self):
        """ parse output desc in graph """
        self.output_list = []
        if 'dst_index' not in self.op_json:
            if self.type() not in NO_OUTPUT_NODES:
                self.log.warning('Parse Op[%s][%s] outputs error.' % (self.type(), self.name()))
            return self.output_list
        desc_index = 0
        for i in range(len(self.op_json['dst_index'])):
            dst_name = self.op_json['dst_name'][i]
            if self.op_json['dst_index'][i] == -1:
                # control edge
                self.output_list.append(OutputDesc(dst_name, [], -1))
            else:
                self.output_list.append(OutputDesc(dst_name, self.op_json['output_desc'][desc_index], desc_index))
                desc_index += 1
        self.output_list.sort(key=lambda x: x.index)
        return self.output_list
