# coding=utf-8
import json
import re
from typing import List
from lib.desc import InputDesc
from lib.desc import OutputDesc
from lib.dump import Dump
from lib.util import util
from lib.constant import Constant

NO_INPUT_NODES = ['Data', 'AtomicAddrClean', 'Recv', 'Constant']
NO_OUTPUT_NODES = ['Send', 'Recv', 'NetOutput']

JSON_KEY_NAME = 'name'
JSON_KEY_TYPE = 'type'
JSON_KEY_ATTR = 'attr'
JSON_KEY = 'key'
JSON_VALUE = 'value'
JSON_KEY_STR = 's'
JSON_KEY_PASS_NAME = 'pass_name'
#dump_manager = Dump()


class Op(object):
    """ Op class.
        name: op name
        type: op type
        inputs: list of input descs
        outputs: list of output descs
    """
    def __init__(self, op_json, op_list):
        """Init"""
        self.op_json = op_json
        self.op_list = op_list
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
        return self._attr(self.name() + "_kernelname")

    def _attr(self, key):
        if JSON_KEY_ATTR in self.op_json:
            for attr in self.op_json[JSON_KEY_ATTR]:
                if key == attr[JSON_KEY]:
                    return attr[JSON_VALUE][JSON_KEY_STR]
        return ''

    def summary(self, origin_txt=False):
        """Summary of current op"""
        res_str = ['[%s] %s' % (self.type(), self.name()), 'KernelName: %s' % self.kernel_name(), 'Input:']
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
                if self.type() not in NO_INPUT_NODES:
                    self.log.warning('invalid input name.')
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
