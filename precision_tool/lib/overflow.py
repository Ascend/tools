# coding=utf-8
import json
import os

from lib.util import util
import config as cfg
from lib.precision_tool_exception import PrecisionToolException
from lib.precision_tool_exception import catch_tool_exception
from lib.constant import Constant

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


class Overflow(object):
    def __init__(self):
        """Init"""
        self.log = util.get_log()
        self.debug_files = None

    @catch_tool_exception
    def prepare(self):
        """Prepare"""
        # find right path in DUMP_FILES_NPU_ALL
        util.create_dir(cfg.DUMP_FILES_OVERFLOW)
        sub_dir = util.get_newest_dir(cfg.DUMP_FILES_OVERFLOW)
        overflow_dump_files = util.list_npu_dump_files(os.path.join(cfg.DUMP_FILES_OVERFLOW, sub_dir))
        self.debug_files = [item for item in overflow_dump_files.values() if item.op_type == 'Opdebug']
        # sort by timestamp
        self.debug_files = sorted(self.debug_files, key=lambda x: x.timestamp)
        self.log.info("Find [%d] debug files in overflow dir.", len(self.debug_files))

    def check(self, max_num=3):
        """Check overflow info"""
        if len(self.debug_files) == 0:
            self.log.info("[Overflow] Checked success. find [0] overflow node!")
            return
        self.log.info("[Overflow] Find [%s] overflow debug file. Will show top %s ops.", len(self.debug_files), max_num)
        for i, debug_file in enumerate(self.debug_files):
            debug_decode_files = self._decode_file(debug_file, True)
            with open(debug_decode_files[0].path, 'r') as f:
                overflow_json = json.load(f)
                util.print_panel(self._json_summary(overflow_json, debug_file))
            if i >= max_num:
                break

    def _json_summary(self, json_txt, debug_file):
        res = []
        detail = {'task_id': -1}
        if 'AI Core' in json_txt and json_txt['AI Core']['status'] > 0:
            detail = json_txt['AI Core']
            res.append(' - [AI Core][Status:%s][TaskId:%s] %s' % (
                detail['status'], detail['task_id'], self._decode_ai_core_status(detail['status'])))
        if 'DHA Atomic Add' in json_txt and json_txt['DHA Atomic Add']['status'] > 0:
            detail = json_txt['DHA Atomic Add']
            res.append(' - [DHA Atomic Add][Status:%s][TaskId:%s] Overflow' % (detail['status'], detail['task_id']))
        if 'L2 Atomic Add' in json_txt and json_txt['L2 Atomic Add']['status'] > 0:
            detail = json_txt['L2 Atomic Add']
            res.append(' - [L2 Atomic Add][Status:%s][TaskId:%s] Overflow' % (detail['status'], detail['task_id']))
        dump_file_info = self._find_dump_files_by_task_id(detail['task_id'], debug_file.dir_path)
        res.append(' - First overflow file timestamp [%s] -' % debug_file.timestamp)
        if dump_file_info is None:
            self.log.warning("Can not find any dump file for debug file: %s, op task id: %s", debug_file.file_name,
                             detail['task_id'])
        else:
            dump_decode_files = self._decode_file(dump_file_info)
            for dump_decode_file in dump_decode_files:
                res.append(' |- %s' % dump_decode_file.file_name)
                res.append('  |- [yellow]%s[/yellow]' % util.gen_npy_info_txt(dump_decode_file.path))
            res.insert(0, '[green][%s][%s][/green] %s' % (dump_file_info.op_type, dump_file_info.task_id,
                                                          dump_file_info.op_name))
        return Constant.NEW_LINE.join(res)

    @staticmethod
    def _decode_file(file_info, debug=False):
        file_name = file_info.file_name
        if debug:
            decode_files = util.list_debug_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, file_name)
        else:
            decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, file_name)
        if len(decode_files) == 0:
            # decode info file
            util.convert_dump_to_npy(file_info.path, cfg.DUMP_FILES_OVERFLOW_DECODE)
            if debug:
                decode_files = util.list_debug_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, file_name)
            else:
                decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_OVERFLOW_DECODE, file_name)
        if len(decode_files) == 0:
            raise PrecisionToolException("Decode overflow debug file: %s failed." % file_name)
        decode_files = sorted(decode_files.values(), key=lambda x: x.timestamp)
        return decode_files

    @staticmethod
    def _find_dump_files_by_task_id(task_id, search_dir):
        dump_files = util.list_npu_dump_files(search_dir)
        dump_file_list = [item for item in dump_files.values() if item.op_type != 'Opdebug']
        dump_file_list = sorted(dump_file_list, key=lambda x: x.timestamp)
        for dump_file in dump_file_list:
            if dump_file.task_id == int(task_id):
                return dump_file
        return None

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
