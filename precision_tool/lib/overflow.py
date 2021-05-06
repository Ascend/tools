# coding=utf-8
import json
import collections
from lib.tool_object import ToolObject
from lib.util import util
import config as cfg
from lib.precision_tool_exception import PrecisionToolException
from lib.precision_tool_exception import catch_tool_exception

AI_CORE_OVERFLOW_STATUS = {
    '0x8': '符号证书最小附属NEG符号位取反溢出',
    '0x10': '整数加法、减法、乘法或乘加操作计算有溢出',
    '0x20': '浮点计算有溢出',
    '0x80': '浮点数转无符号数的输入是负数',
    '0x100': 'FP32转FP16或32位富豪整数转FP16中出现溢出',
    '0x400': 'CUBE累加出现溢出'
}
DHA_ATOMIC_ADD_STATUS = {
    '0x9': '[atomic overflow] 向上溢出',
    '0xA': '[atomic underflow] 向下溢出',
    '0xB': '[atomic src nan] 源操作数非法',
    '0xC': '[atomic dst nan] 目的操作数非法',
    '0xD': '[atomic both nan] 源操作数和目的操作数均非法'
}
L2_ATOMIC_ADD_STATUS = {
    '001': '[atomic overflow] 向上溢出',
    '010': '[atomic underflow] 向下溢出',
    '011': '[atomic src nan] 源操作数非法',
    '100': '[atomic dst nan] 目的操作数非法',
    '101': '[atomic both nan] 源操作数和目的操作数均非法'
}


class Overflow(ToolObject):
    overflow_ops = collections.OrderedDict()
    overflow_dump_files = {}
    task_id_to_file_map = {}
    overflow_dump_parent_dirs = {}

    def __init__(self):
        """Init"""
        super(Overflow, self).__init__()
        self.log = util.get_log()

    @catch_tool_exception
    def prepare(self):
        """Prepare"""
        self.overflow_dump_files, self.overflow_dump_parent_dirs = util.list_dump_files(cfg.DUMP_FILES_OVERFLOW)
        self._parse_overflow_files()

    def check(self, max_num=3):
        """Check overflow info"""
        if len(self.overflow_ops) == 0:
            self.log.info("[Overflow] Checked success. find [0] overflow node!")
            return
        max_num = min(max_num, len(self.overflow_ops))
        self.log.info("[Overflow] Find [%s] overflow node. Will show top %s ops.", len(self.overflow_ops), max_num)
        cnt = 0
        for op_name in self.overflow_ops:
            file_infos = self.overflow_ops[op_name]
            first_timestamp = sorted(file_infos.keys())[0]
            file_info = file_infos[first_timestamp]
            self._decode_overflow_info(file_info)
            self._parse_overflow_info(file_info)
            cnt += 1
            if cnt == max_num:
                break
        self.log.info("[Overflow] Checked success. find [%d] overflow node!", len(self.overflow_ops))

    def _parse_overflow_files(self):
        # make relationship between dump_file and debug_file
        for dirs in self.overflow_dump_parent_dirs.values():
            dump_file_list = [item for item in dirs.values() if item['op_type'] != 'Opdebug']
            debug_file_list = [item for item in dirs.values() if item['op_type'] == 'Opdebug']
            if len(dump_file_list) != len(debug_file_list):
                raise PrecisionToolException("Dump files num not equal to Debug files info")
            dump_file_list = sorted(dump_file_list, key=lambda x: x['timestamp'])
            debug_file_list = sorted(debug_file_list, key=lambda x: x['timestamp'])
            for i in range(len(dump_file_list)):
                dump_file_list[i]['debug_file'] = debug_file_list[i]
        # makeup overflow_ops
        op_dump_files = filter(lambda x: x['op_type'] != 'Opdebug', self.overflow_dump_files.values())
        # sorted by taskid
        op_dump_files = sorted(op_dump_files, key=lambda x: x['task_id'])
        for file_info in op_dump_files:
            op_name = file_info['op_name']
            timestamp = file_info['timestamp']
            if op_name not in self.overflow_ops:
                self.overflow_ops[op_name] = {}
                self.log.debug("Find overflow op, [TaskId:%s][OpName:%s]", file_info['task_id'], op_name)
            self.overflow_ops[op_name][timestamp] = file_info

    @staticmethod
    def _decode_overflow_info(file_info):
        debug_file = file_info['debug_file']
        file_path = file_info['path']
        # do not convert again
        dump_name = file_info['file_name']
        debug_name = debug_file['file_name']
        dump_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, dump_name)
        debug_decode_files = util.list_debug_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, debug_name)
        if len(dump_decode_files) == 0:
            # decode dump file
            util.convert_dump_to_npy(file_path, cfg.DUMP_FILES_OVERFLOW_DECODE)
            dump_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, dump_name)
        if len(debug_decode_files) == 0:
            # decode info file
            util.convert_dump_to_npy(debug_file['path'], cfg.DUMP_FILES_OVERFLOW_DECODE)
            debug_decode_files = util.list_debug_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, debug_name)
        file_info['dump_decode_files'] = dump_decode_files
        file_info['debug_decode_files'] = debug_decode_files
        return file_info

    def _parse_overflow_info(self, file_info):
        """"""
        debug_decode_files = file_info['debug_decode_files']
        for debug_decode_file in debug_decode_files.values():
            with open(debug_decode_file['path'], 'r') as f:
                overflow_json = json.load(f)
                util.print_panel(self._json_summary(overflow_json, file_info))

    def _json_summary(self, json_txt, file_info):
        res = "[green][%s][%s][/green] %s" % (file_info['op_type'], file_info['task_id'], file_info['op_name'])
        if 'AI Core' in json_txt and json_txt['AI Core']['status'] > 0:
            detail = json_txt['AI Core']
            res += '\n - [AI Core][Status:%s][TaskId:%s] %s' % (
                detail['status'], detail['task_id'], self._decode_ai_core_status(detail['status']))
        if 'DHA Atomic Add' in json_txt and json_txt['DHA Atomic Add']['status'] > 0:
            detail = json_txt['DHA Atomic Add']
            res += '\n - [DHA Atomic Add][Status:%s][TaskId:%s] Overflow' % (detail['status'], detail['task_id'])
        if 'L2 Atomic Add' in json_txt and json_txt['L2 Atomic Add']['status'] > 0:
            detail = json_txt['L2 Atomic Add']
            res += '\n - [L2 Atomic Add][Status:%s][TaskId:%s] Overflow' % (detail['status'], detail['task_id'])
        res += '\n - First overflow file timestamp [%s] -' % file_info['timestamp']
        for dump_decode_file in file_info['dump_decode_files'].values():
            res += '\n |- %s' % dump_decode_file['file_name']
            res += '\n  |- [yellow]%s[/yellow]' % util.gen_npy_info_txt(dump_decode_file['path'])
        return res

    def _decode_ai_core_status(self, status):
        error_code = []
        if type(status) is not int:
            return error_code
        bin_status = ''.join(reversed(bin(status)))
        prefix = ''
        self.log.debug('Decode AI Core Overflow status:[%s]', hex(status))
        for i in range(len(bin_status)):
            if bin_status[i] == '1':
                error_code.append(AI_CORE_OVERFLOW_STATUS[hex(int('1' + prefix, 2))])
            prefix += '0'
        return error_code
