# coding=utf-8
import re
from typing import List
from lib.util import LOG
from lib.desc import InputDesc
from lib.desc import OutputDesc
from lib.dump import Dump
from lib.util import util

NO_INPUT_NODES = ['Data', 'AtomicAddrClean', 'Recv', 'Constant']
NO_OUTPUT_NODES = ['Send', 'Recv', 'NetOutput']

dump_manager = Dump()


class Op(object):
    """ Op class.
        name: op name
        type: op type
        inputs: list of input descs
        outputs: list of output descs
    """
    def __init__(self, op_json, op_list):
        self.op_json = op_json
        self.op_list = op_list
        self.input_list = None
        self.output_list = None
        self.npu_input_files = None
        self.npu_output_files = None
        self.cpu_output_files = None

    def name(self):
        return self.op_json['name']

    def type(self):
        return self.op_json['type']

    def inputs(self) -> List[InputDesc]:
        """ Return the input list
        """
        if self.input_list is None:
            self._parse_inputs()
        return self.input_list

    def outputs(self) -> List[OutputDesc]:
        """ Return output list
        """
        if self.output_list is None:
            self._parse_outputs()
        return self.output_list

    def npu_dump_input_files(self):
        if self.npu_input_files is None:
            self._parse_decode_file()
        return self.npu_input_files

    def npu_dump_output_files(self):
        if self.npu_output_files is None:
            self._parse_decode_file()
        return self.npu_output_files

    def cpu_dump_output_files(self):
        if self.cpu_output_files is None:
            self.cpu_output_files = {}
            cpu_files = dump_manager.get_cpu_dump_files_by_op(self)
            for cpu_file in cpu_files.values():
                self.cpu_output_files[cpu_file['idx']] = cpu_file
                cpu_file['shape'], cpu_file['dtype'] = util.npy_info(cpu_file['path'])
        return self.cpu_output_files

    def _parse_decode_file(self):
        dump_decode_files = dump_manager.get_npu_dump_decode_files_by_op(self)
        self.npu_input_files = {}
        self.npu_output_files = {}
        for dump_file in dump_decode_files.values():
            dump_file['shape'], dump_file['dtype'] = util.npy_info(dump_file['path'])
            if dump_file['type'] == 'input':
                self.npu_input_files[dump_file['idx']] = dump_file
            else:
                self.npu_output_files[dump_file['idx']] = dump_file

    def _parse_inputs(self):
        """ parse input desc in graph """
        self.input_list = []
        if 'input' not in self.op_json:
            if self.type() not in NO_INPUT_NODES:
                LOG.warning('Parse Op[%s][%s] inputs error.' % (self.type(), self.name()))
            return self.input_list
        desc_index = 0
        for i in range(len(self.op_json['input'])):
            name = self.op_json['input'][i]
            if name == '':
                if self.type() not in NO_INPUT_NODES:
                    LOG.warning('invalid input name.')
                continue
            name_info = name.split(':')
            if len(name_info) == 2 and int(name_info[1]) == -1:
                # control edge
                self.input_list.append(InputDesc(name, [], i))
            else:
                self.input_list.append(InputDesc(name, self.op_json['input_desc'][desc_index], i))
                desc_index += 1
        return self.input_list

    def _parse_outputs(self):
        """ parse output desc in graph """
        self.output_list = []
        if 'dst_index' not in self.op_json:
            if self.type() not in NO_OUTPUT_NODES:
                LOG.warning('Parse Op[%s][%s] outputs error.' % (self.type(), self.name()))
            return self.output_list
        desc_index = 0
        for i in range(len(self.op_json['dst_index'])):
            dst_name = self.op_json['dst_name'][i]
            if self.op_json['dst_index'][i] == -1:
                # control edge
                self.output_list.append(OutputDesc(dst_name, [], i))
            else:
                self.output_list.append(OutputDesc(dst_name, self.op_json['output_desc'][desc_index], i))
                desc_index += 1

    def summary(self):
        """ summary of current op """
        input_txt = ''
        output_txt = ''
        for i in self.inputs():
            input_txt += '\n -' + i.summary()
        for i in self.outputs():
            output_txt += '\n -' + i.summary()
        res_str = "[%s] %s\nInput:%s\nOutput:%s\nNpuDump:\n -%s\nCpuDump:\n -%s" % (
            self.type(), self.name(), input_txt, output_txt,
            str(dump_manager.get_npu_dump_files_by_op(self).keys()),
            str(dump_manager.get_cpu_dump_files_by_op(self).keys()))
        npu_dump_input_txt = ''
        npu_dump_output_txt = ''
        for npu_dump_file in self.npu_dump_input_files().values():
            # [index][shape] file_name
            npu_dump_input_txt += '\n -[green][%s][/green][yellow][%s][/yellow] %s' % (
                npu_dump_file['idx'], npu_dump_file['shape'], npu_dump_file['file_name'])
        for npu_dump_file in self.npu_dump_output_files().values():
            npu_dump_output_txt += '\n -[green][%s][/green][yellow][%s][/yellow] %s' % (
                npu_dump_file['idx'], npu_dump_file['shape'], npu_dump_file['file_name'])
        npu_dump_info = 'NpuDumpInput:%s\nNpuDumpOutput:%s' % (npu_dump_input_txt, npu_dump_output_txt)
        cpu_dump_txt = ''
        for cpu_dump_file in self.cpu_dump_output_files().values():
            cpu_dump_txt += '\n -[green][%s][/green][yellow][%s][/yellow] %s' % (
                cpu_dump_file['idx'], cpu_dump_file['shape'], cpu_dump_file['file_name'])
        res_str += "\n%s\nCpuDumpOutput:%s" % (npu_dump_info, cpu_dump_txt)
        return res_str
