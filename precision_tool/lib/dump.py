# coding=utf-8
import os
import re
from lib.tool_object import ToolObject
from lib.util import util
import config as cfg
from lib.precision_tool_exception import catch_tool_exception
from lib.precision_tool_exception import PrecisionToolException

NEW_LINE = '\n'


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
                shape, dtype, max_data, min_data, mean = util.npy_info(info['path'])
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
        self.npu_decode_files = None
        self.op_npu_decode_files = None
        self.sub_graph = None
        self.sub_graph_path = None
        self._init_dirs()

    def prepare(self, sub_graph):
        """Prepare npu/cpu dump files"""
        self.sub_graph = sub_graph
        self._prepare_npu_dump()
        self._parse_cpu_dump_files()

    @catch_tool_exception
    def _prepare_npu_dump(self):
        """prepare npu dump, mk soft link of of sub_graph"""
        if self.sub_graph is None:
            raise PrecisionToolException("Sub graph in build graph is None, please check.")
        # find right path in DUMP_FILES_NPU_ALL
        for dir_path, dir_names, file_names in os.walk(cfg.DUMP_FILES_NPU, followlinks=True):
            for dir_name in dir_names:
                if dir_name == self.sub_graph:
                    self.sub_graph_path = os.path.join(dir_path, dir_name)
                    self.log.info("Find sub graph dir: %s", self.sub_graph_path)
        if self.sub_graph_path is None:
            raise PrecisionToolException("Can not find any sub graph dir %s in npu dump path [%s]." % (
                self.sub_graph, cfg.DUMP_FILES_NPU))
        self._parse_npu_dump_files()

    @staticmethod
    def _init_dirs():
        """Create dump file dirs"""
        # self.log.debug('Init dump dirs.')
        util.create_dir(cfg.DUMP_FILES_NPU)
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

    @catch_tool_exception
    def op_dump_summary(self, op):
        """ print op dump info"""
        if op is None:
            raise PrecisionToolException("Get None operator")
        # title = '[yellow]NPU/CPU-DumpFiles[/yellow][green][%s][/green]%s' % (op.type(), op.name())
        # search npu dump file by op name
        npu_dump_files = self.get_npu_dump_decode_files_by_op(op)
        npu_dump_files = sorted(npu_dump_files.values(), key=lambda x: x['idx'])
        input_txt = ['NpuDumpInput:']
        output_txt = ['NpuDumpOutput:']
        for npu_dump_file in npu_dump_files:
            if npu_dump_file['type'] == 'input':
                input_txt.append(' -[green][%s][/green] %s' % (npu_dump_file['idx'], npu_dump_file['file_name']))
                input_txt.append('  |- [yellow]%s[/yellow]' % util.gen_npy_info_txt(npu_dump_file['path']))
                # npu_dump_input_txt += '\n -[green][%s][/green] %s' % (npu_dump_file['idx'], npu_dump_file['file_name'])
            else:
                output_txt.append(' -[green][%s][/green] %s' % (npu_dump_file['idx'], npu_dump_file['file_name']))
                output_txt.append('  |- [yellow]%s[/yellow]' % util.gen_npy_info_txt(npu_dump_file['path']))
        # npu_dump_info = 'NpuDumpInput:%s\nNpuDumpOutput:%s' % (npu_dump_input_txt, npu_dump_output_txt)
        input_txt.extend(output_txt)
        npu_dump_info = NEW_LINE.join(input_txt)
        # cpu dump info
        cpu_dump_txt = ['CpuDumpOutput:']
        cpu_dump_files = self.get_cpu_dump_files_by_op(op)
        for cpu_dump_file in cpu_dump_files.values():
            cpu_dump_txt.append(' -[green][%s][/green] %s' % (cpu_dump_file['idx'], cpu_dump_file['file_name']))
            cpu_dump_txt.append('  |- [yellow]%s[/yellow]' % util.gen_npy_info_txt(cpu_dump_file['path']))
        cpu_dump_info = NEW_LINE.join(cpu_dump_txt)
        return NEW_LINE.join([npu_dump_info, cpu_dump_info])

    def print_data(self, file_name, is_convert):
        """Print numpy data file"""
        if os.path.isfile(file_name):
            return util.print_npy_summary(os.path.dirname(file_name), os.path.basename(file_name), is_convert)
        parent_dirs = []
        file_names = [file_name]
        if '/' in file_name:
            # maybe node name, replace to '_' and detect
            self.log.warning("Invalid file name[%s]. you may mean the files below.", file_name)
            file_names = self._detect_cpu_file_name(file_name)
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

    def convert_npu_dump(self, name, data_format, dst_path=None):
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
        elif self.npu_files is not None and name in self.npu_files:
            self.log.info("Decode npu dump file: %s in default dump path", name)
            file_info = self.npu_files[name]
            file_name = file_info['file_name']
            file_path = file_info['path']
        else:
            # maybe op name
            file_info = self._get_file_by_op_name(name)
            if file_info is None:
                raise PrecisionToolException("Can not find any op/dump file named %s" % name)
            file_name = file_info['file_name']
            file_path = file_info['path']
        dst_path = cfg.DUMP_FILES_CONVERT if dst_path is None else dst_path
        util.convert_dump_to_npy(file_path, dst_path, data_format)
        dump_convert_files = util.list_npu_dump_convert_files(dst_path, file_name)
        # print result info

        summary_txt = 'SrcFile: %s' % name
        for convert_file in dump_convert_files.values():
            summary_txt += '\n - %s' % convert_file['file_name']
        util.print_panel(summary_txt)

    def _get_file_by_op_name(self, op_name):
        """Get dump file info by op name"""
        for file_info in self.npu_files.values():
            if file_info['op_name'] == op_name:
                return file_info
        return None

    def _parse_npu_dump_files(self):
        # self.npu_files, self.npu_parent_dirs = util.list_dump_files(self.sub_graph_path)
        self.npu_files = util.list_npu_dump_files(self.sub_graph_path)
        parent_dirs = []
        for file_info in self.npu_files.values():
            if file_info['dir_path'] not in parent_dirs:
                parent_dirs.append(file_info['dir_path'])
        if len(parent_dirs) == 0:
            raise PrecisionToolException("Can not find any npu files in dir: %s" % self.sub_graph_path)
        if len(parent_dirs) > 1:
            self.log.warning("Npu dump files exist in different sub dirs, will select the first one. %s", parent_dirs)
        self.sub_graph_path = parent_dirs[0]
        self.log.info("Update sub graph path to %s", self.sub_graph_path)

    def _parse_cpu_dump_files(self):
        self.cpu_files = util.list_cpu_dump_decode_files(cfg.DUMP_FILES_CPU)

    def _decode_npu_dump_files_by_op(self, op):
        dump_files = self.get_npu_dump_files_by_op(op)
        for dump_file in dump_files.values():
            util.convert_dump_to_npy(dump_file['path'], cfg.DUMP_FILES_DECODE)

    @staticmethod
    def _detect_cpu_file_name(file_name):
        match_name = file_name.replace('/', '_').replace('.', '_') + '\\.'
        cpu_files = util.list_cpu_dump_decode_files(cfg.DUMP_FILES_CPU, match_name)
        summary = 'CPU_DUMP:'
        for file_name in cpu_files.keys():
            summary += '\n - %s' % file_name
        util.print_panel(summary)
        return cpu_files
