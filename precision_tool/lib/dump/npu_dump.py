# coding=utf-8
import os
import re
from ..util.util import util
from ..util.constant import Constant
from ..util.precision_tool_exception import catch_tool_exception
from ..util.precision_tool_exception import PrecisionToolException
from ..config import config as cfg


class NpuDumpDecodeFile(object):
    def __init__(self):
        self.log = util.get_log()
        self.input_files = {}
        self.output_files = {}
        self.timestamp = -1
        self.op_name = ''
        self.op_type = ''
        self.task_id = -1
        # self.stream_id = -1

    def update(self, file_info):
        """Prepare op npu decode file map."""
        if not self._check(file_info):
            self.log.warning('Invalid NpuDumpDecodeFile: %s', file_info)
            return
        if file_info.type == 'input':
            self.input_files[file_info.idx] = file_info
        else:
            self.output_files[file_info.idx] = file_info

    def summary(self):
        txt = ['[yellow][%s][TaskID: %d][/yellow][green][%s][/green] %s' % (
            self.timestamp, self.task_id, self.op_type, self.op_name)]
        if len(self.input_files) > 0:
            info = self.input_files[0]
            shape, dtype, max_data, min_data, mean = util.npy_info(info.path)
            txt.append(' - Input:  [green][0][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                shape, dtype, max_data, min_data, mean, info.file_name))
            for idx in range(1, len(self.input_files)):
                info = self.input_files[idx]
                shape, dtype, max_data, min_data, mean = util.npy_info(info.path)
                txt.append('           [green][%d][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                    idx, shape, dtype, max_data, min_data, mean, info.file_name))
        if len(self.output_files) > 0:
            info = self.output_files[0]
            shape, dtype, max_data, min_data, mean = util.npy_info(info.path)
            txt.append(' - Output: [green][0][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                shape, dtype, max_data, min_data, mean, info.file_name))
            for idx in range(1, len(self.output_files)):
                info = self.output_files[idx]
                shape, dtype, max_data, min_data, mean = util.npy_info(info.path)
                txt.append('           [green][%d][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                    idx, shape, dtype, max_data, min_data, mean, info.file_name))
        return Constant.NEW_LINE.join(txt)

    def _check(self, file_info):
        if self.timestamp == -1:
            self.timestamp = file_info.timestamp
            self.op_name = file_info.op_name
            self.op_type = file_info.op_type
            self.task_id = file_info.task_id
            # self.stream_id = file_info['stream']
            return True
        return self.timestamp == file_info['timestamp']


class NpuDump(object):
    def __init__(self, debug_id=Constant.DEFAULT_DEBUG_ID):
        """Init"""
        self.log = util.get_log()
        self.debug_id = debug_id
        npu_root = os.path.join(cfg.NPU_DIR, debug_id)
        self.dump_root = os.path.join(npu_root, Constant.DUMP)
        self.decode_dir = os.path.join(cfg.DUMP_DECODE_DIR, debug_id)
        self.dump_files = None
        self._init_dirs()

    def prepare(self):
        """Prepare npu/cpu dump files"""
        self._parse_dump_files()

    def get_dump_files_by_op(self, op):
        """Get npu dump files by Op"""
        npu_files = {}
        op_name = op.name().replace('/', '_').replace('.', '_')
        match_name = op.type() + '.' + op_name + '\\.'
        for f in self.dump_files:
            # match op name and graph name, infer dump directory may not has graph
            if re.match(match_name, f) and (op.graph_name in self.dump_files[f].path or cfg.NET_TYPE == 'infer'):
                npu_files[f] = self.dump_files[f]
        return npu_files

    @catch_tool_exception
    def op_dump_summary(self, op):
        """ print op dump info"""
        if op is None:
            raise PrecisionToolException("Get None operator")
        # search npu dump file by op name
        npu_dump_files = self.get_npu_dump_decode_files_by_op(op)
        npu_dump_files = sorted(npu_dump_files.values(), key=lambda x: (x.idx, x.timestamp))
        input_txt = ['NpuDumpInput:']
        output_txt = ['NpuDumpOutput:']
        for npu_dump_file in npu_dump_files:
            if npu_dump_file.type == 'input':
                input_txt.append(' -[green][%s][/green] %s' % (npu_dump_file.idx, npu_dump_file.file_name))
                input_txt.append('   └─ [yellow]%s[/yellow]' % util.gen_npy_info_txt(npu_dump_file.path))
            else:
                output_txt.append(' -[green][%s][/green] %s' % (npu_dump_file.idx, npu_dump_file.file_name))
                output_txt.append('   └─ [yellow]%s[/yellow]' % util.gen_npy_info_txt(npu_dump_file.path))
        input_txt.extend(output_txt)
        return Constant.NEW_LINE.join(input_txt)

    def _init_dirs(self):
        util.create_dir(self.dump_root)
        util.create_dir(self.decode_dir)

    @catch_tool_exception
    def _parse_dump_files(self):
        """prepare npu dump, support soft link"""
        sub_dir = util.get_newest_dir(self.dump_root)
        sub_dir = os.path.join(self.dump_root, sub_dir) if sub_dir != '' else self.dump_root
        self.dump_files = util.list_npu_dump_files(sub_dir)

    def list_dump(self, dir_path, file_name):
        """"""

    @staticmethod
    def get_npu_dump_decode_files_by_name(file_name):
        file_name = file_name.replace('/', '_')
        return util.list_npu_dump_convert_files(cfg.DECODE_DIR, file_name)

    def get_npu_dump_decode_files_by_op(self, op):
        """Get npu dump decode files by op"""
        dump_files = self.get_dump_files_by_op(op)
        result = {}
        for dump_file in dump_files.values():
            dump_decode_files = util.list_npu_dump_decode_files(self.decode_dir, dump_file.file_name)
            if len(dump_decode_files) == 0:
                util.convert_dump_to_npy(dump_file.path, self.decode_dir)
            dump_decode_files = util.list_npu_dump_decode_files(self.decode_dir, dump_file.file_name)
            result.update(dump_decode_files)
        return result

    def convert_npu_dump(self, name, data_format=None, dst_path=None):
        """Convert npu dump to npy of data_format"""
        if os.path.isfile(name):
            # absolute path to file
            self.log.info("Decode file: %s", name)
            file_name = os.path.basename(name)
            file_path = name
        elif os.path.isdir(name):
            # decode all files in path
            self.log.info("Decode all files in path: %s", name)
            file_name = ''
            file_path = name
        elif self.dump_files is not None and name in self.dump_files:
            self.log.info("Decode npu dump file: %s in default dump path", name)
            file_info = self.dump_files[name]
            file_name = file_info.file_name
            file_path = file_info.path
        else:
            # maybe op name
            file_info = self._get_file_by_op_name(name)
            if file_info is None:
                raise PrecisionToolException("Can not find any op/dump file named %s" % name)
            file_name = file_info.file_name
            file_path = file_info.path
        dst_path = cfg.DUMP_CONVERT_DIR if dst_path is None else dst_path
        util.convert_dump_to_npy(file_path, dst_path, data_format)
        dump_convert_files = util.list_npu_dump_convert_files(dst_path, file_name)
        # print result info

        summary_txt = ['SrcFile: %s' % name]
        for convert_file in dump_convert_files.values():
            summary_txt.append(' - %s' % convert_file.file_name)
        util.print_panel(Constant.NEW_LINE.join(summary_txt))

    def _get_file_by_op_name(self, op_name):
        """Get dump file info by op name"""
        op_name = op_name.replace('/', '_')
        for file_info in self.dump_files.values():
            if file_info.op_name == op_name:
                return file_info
        return None
