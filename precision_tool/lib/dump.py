# coding=utf-8
import os
import re
from lib.tool_object import ToolObject
from lib.util import util
from lib.util import LOG
import config as cfg
from rich.progress import Progress


class Dump(ToolObject):
    npu_files = None
    cpu_files = None
    npu_parent_dirs = None

    def __init__(self):
        """Init"""
        super(Dump, self).__init__()
        self._init_dirs()

    def preapre(self):
        """Prepare npu/cpu dump files"""
        self._parse_npu_dump_files()
        self._parse_cpu_dump_files()

    @staticmethod
    def _init_dirs():
        """Create dump file dirs"""
        LOG.debug('Init dump dirs.')
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

    @staticmethod
    def print_data(file_name):
        """Print numpy data file"""
        parent_dirs = []
        for parent_dir in [cfg.DUMP_FILES_DECODE, cfg.DUMP_FILES_CPU, cfg.DUMP_FILES_OVERFLOW_DECOD,
                           cfg.DUMP_FILES_CONVERT]:
            if os.path.isfile(os.path.join(parent_dir, file_name)):
                LOG.debug("Print data in %s", parent_dir)
                util.print_npy_summary(parent_dir, file_name)
                parent_dirs.append(parent_dir)
        LOG.info("Find file [%s] in [%d] dirs. %s", file_name, len(parent_dirs), str(parent_dirs))

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
            LOG.warning("Can not find any op/dump file named %s", name)
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
        with Progress() as process:
            task = process.add_task('[green]Decode Dump files...', total=len(self.npu_files))
            for file_name in self.npu_files:
                file_info = self.npu_files[file_name]
                util.convert_dump_to_npy(file_info['path'], cfg.DUMP_FILES_DECODE)
                process.update(task)

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
