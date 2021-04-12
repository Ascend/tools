# coding=utf-8
import os
import re
from lib.tool_object import ToolObject
from lib.util import util
import config as cfg


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
        if file_info['type'] == 'input':
            self.input_files[file_info['idx']] = file_info
        else:
            self.output_files[file_info['idx']] = file_info

    def summary(self):
        txt = '[yellow][%s][TaskID: %d][/yellow][green][%s][/green] %s' % (
            self.timestamp, self.task_id, self.op_type, self.op_name)
        if len(self.input_files) > 0:
            info = self.input_files[0]
            shape, dtype, max_data, min_data, mean = util.npy_info(info['path'])
            txt += '\n - Input:  [green][0][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                shape, dtype, max_data, min_data, mean, info['file_name'])
            for idx in range(1, len(self.input_files)):
                info = self.input_files[idx]
                shape, dtype, max_data, min, mean = util.npy_info(info['path'])
                txt += '\n           [green][%d][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                    idx, shape, dtype, max_data, min_data, mean, info['file_name'])
        if len(self.output_files) > 0:
            info = self.output_files[0]
            shape, dtype, max_data, min_data, mean = util.npy_info(info['path'])
            txt += '\n - Output: [green][0][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                shape, dtype, max_data, min_data, mean, info['file_name'])
            for idx in range(1, len(self.output_files)):
                info = self.output_files[idx]
                shape, dtype, max_data, min_data, mean = util.npy_info(info['path'])
                txt += '\n           [green][%d][/green][yellow][%s][%s][Max:%d][Min:%d][Mean:%d][/yellow] %s' % (
                    idx, shape, dtype, max_data, min_data, mean, info['file_name'])
        return txt

    def _check(self, file_info):
        if self.timestamp == -1:
            self.timestamp = file_info['timestamp']
            self.op_name = file_info['op_name']
            self.op_type = file_info['op_type']
            self.task_id = file_info['task_id']
            # self.stream_id = file_info['stream']
            return True
        return self.timestamp == file_info['timestamp']


class Dump(ToolObject):

    def __init__(self):
        """Init"""
        super(Dump, self).__init__()
        self.log = util.get_log()
        self.npu_files = None
        self.cpu_files = None
        self.npu_parent_dirs = None
        self.npu_decode_files = None
        self.op_npu_decode_files = None
        self.sub_graph = None
        self._init_dirs()

    def prepare(self, sub_graph):
        """Prepare npu/cpu dump files"""
        self.sub_graph = sub_graph
        self._prepare_npu_dump()
        self._parse_cpu_dump_files()

    def _prepare_npu_dump(self):
        """prepare npu dump, mk soft link of of sub_graph"""
        if self.sub_graph is None:
            self.log.warning("Sub graph in build graph is None, please check.")
            return
        # find right path in DUMP_FILES_NPU_ALL
        sub_graph_path = ''
        for dir_path, dir_names, file_names in os.walk(cfg.DUMP_FILES_NPU_ALL, followlinks=True):
            for dir_name in dir_names:
                if dir_name in self.sub_graph:
                    sub_graph_path = os.path.join(dir_path, dir_name)
                    self.log.info("Find sub graph dir: %s", sub_graph_path)
        if sub_graph_path == '':
            self.log.warning("Can not find any sub graph dir %s in [%].", str(self.sub_graph.keys()), sub_graph_path)
            return
        # make link to DUMP_FILES_NPU
        os.symlink(sub_graph_path, cfg.DUMP_FILES_NPU)
        self.log.info("Link current npu dump dir to sub graph: %s", sub_graph_path)
        self._parse_npu_dump_files()

    def _init_dirs(self):
        """Create dump file dirs"""
        self.log.debug('Init dump dirs.')
        # util.create_dir(cfg.DUMP_FILES_NPU)
        util.create_dir(cfg.DUMP_FILES_DECODE)
        util.create_dir(cfg.DUMP_FILES_OVERFLOW)
        util.create_dir(cfg.DUMP_FILES_OVERFLOW_DECODE)
        util.create_dir(cfg.DUMP_FILES_CPU)

    def npu_dump_files(self):
        """Get npu dump files"""
        if self.npu_files is None:
            self._parse_npu_dump_files()
        return self.npu_files

    def cpu_dump_files(self):
        """Get cpu dump files"""
        if self.cpu_files is None:
            self._parse_cpu_dump_files()
        return self.cpu_files

    def list_dump(self, dir_path, file_name):
        """"""

    def print_data(self, file_name, is_convert):
        """Print numpy data file"""
        parent_dirs = []
        file_names = [file_name]
        if '/' in file_name:
            # maybe node name, replace to '_' and detect
            self.log.warning("Invalid file name[%s]. you may mean the files below.", file_name)
            file_names = self._detect_file_name(file_name)
        for parent_dir in [cfg.DUMP_FILES_DECODE, cfg.DUMP_FILES_CPU, cfg.DUMP_FILES_OVERFLOW_DECODE,
                           cfg.DUMP_FILES_CONVERT]:
            for file_name in file_names:
                if os.path.isfile(os.path.join(parent_dir, file_name)):
                    self.log.debug("Print data in %s", parent_dir)
                    util.print_npy_summary(parent_dir, file_name, is_convert)
                    parent_dirs.append(parent_dir)
        self.log.info("Find file [%s] in [%d] dirs. %s", file_name, len(parent_dirs), str(parent_dirs))

    def get_npu_dump_files_by_op(self, op):
        """Get npu dump files by Op"""
        npu_files = {}
        match_name = op.type() + '.' + op.name().replace('/', '_').replace('.', '_') + '\\.'
        for f in self.npu_dump_files():
            if re.match(match_name, f):
                npu_files[f] = self.npu_dump_files()[f]
        return npu_files

    def get_npu_dump_decode_files_by_op(self, op):
        """Get npu dump decode files by op"""
        match_name = op.type() + '.' + op.name().replace('/', '_').replace('.', '_') + '\\.'
        dump_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_DECODE, match_name)
        if len(dump_decode_files) == 0:
            self._decode_npu_dump_files_by_op(op)
            dump_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_DECODE, match_name)
        return dump_decode_files

    def get_cpu_dump_files_by_op(self, op):
        """Get cpu dump files by op"""
        cpu_files = {}
        match_name = op.name().replace('/', '_').replace('.', '_') + '\\.'
        for f in self.cpu_dump_files():
            if re.match(match_name, f):
                cpu_files[f] = self.cpu_dump_files()[f]
        return cpu_files

    def convert_npu_dump(self, name, data_format):
        """Convert npu dump to npy of data_format"""
        if name in self.npu_files:
            file_info = self.npu_files[name]
        else:
            # maybe op name
            file_info = self._get_file_by_op_name(name)
        if file_info is None:
            self.log.warning("Can not find any op/dump file named %s", name)
            return
        util.convert_dump_to_npy(file_info['path'], cfg.DUMP_FILES_CONVERT, data_format)
        dump_convert_files = util.list_npu_dump_convert_files(cfg.DUMP_FILES_CONVERT, name)
        # print result info
        summary_txt = 'SrcFile: %s' % file_info['file_name']
        for convert_file in dump_convert_files.values():
            summary_txt += '\n - %s' % convert_file['file_name']
        util.print_panel(summary_txt)

    def decode_all_npu_dump(self):
        """Decode all npu dump files"""
        for parent_dir in self.npu_parent_dirs:
            util.convert_dump_to_npy(parent_dir, cfg.DUMP_FILES_DECODE)
        self.npu_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_DECODE)
        self.op_npu_decode_files = {}
        for file_info in self.npu_decode_files.values():
            if file_info['op_name'] not in self.op_npu_decode_files:
                self.op_npu_decode_files[file_info['op_name']] = NpuDumpDecodeFile()
            op_decode_file = self.op_npu_decode_files[file_info['op_name']]
            op_decode_file.update(file_info)
        # sorted_list = list
        for op_decode_file in self.op_npu_decode_files.values():
            util.print_panel(op_decode_file.summary())

    def _get_file_by_op_name(self, op_name):
        """Get dump file info by op name"""
        for file_info in self.npu_files.values():
            if file_info['op_name'] == op_name:
                return file_info
        return None

    def _parse_npu_dump_files(self):
        self.npu_files, self.npu_parent_dirs = util.list_dump_files(cfg.DUMP_FILES_NPU)

    def _parse_cpu_dump_files(self):
        self.cpu_files = util.list_cpu_dump_decode_files(cfg.DUMP_FILES_CPU)

    def _decode_npu_dump_files_by_op(self, op):
        dump_files = self.get_npu_dump_files_by_op(op)
        for dump_file in dump_files.values():
            util.convert_dump_to_npy(dump_file['path'], cfg.DUMP_FILES_DECODE)

    @staticmethod
    def _detect_file_name(file_name):
        match_name = file_name.replace('/', '_').replace('.', '_') + '\\.'
        cpu_files = util.list_cpu_dump_decode_files(cfg.DUMP_FILES_CPU, match_name)
        summary = 'CPU_DUMP:'
        for file_name in cpu_files.keys():
            summary += '\n - %s' % file_name
        util.print_panel(summary)
        return cpu_files
