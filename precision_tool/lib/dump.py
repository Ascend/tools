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
        super(Dump, self).__init__()
        self._init_dirs()

    def preapre(self):
        self._parse_npu_dump_files()
        self._parse_cpu_dump_files()

    @staticmethod
    def _init_dirs():
        LOG.debug('Init dump dirs.')
        util.create_dir(cfg.DUMP_FILES_NPU)
        util.create_dir(cfg.DUMP_FILES_DECODE)
        util.create_dir(cfg.DUMP_FILES_OVERFLOW)
        util.create_dir(cfg.DUMP_FILES_OVERFLOW_DECODE)
        util.create_dir(cfg.DUMP_FILES_CPU)

    def npu_dump_files(self):
        if self.npu_files is None:
            self._parse_npu_dump_files()
        return self.npu_files

    def cpu_dump_files(self):
        if self.cpu_files is None:
            self._parse_cpu_dump_files()
        return self.cpu_files

    def print_data(self, file_name):
        if os.path.isfile(os.path.join(cfg.DUMP_FILES_DECODE, file_name)):
            LOG.debug("Print data in %s" % cfg.DUMP_FILES_DECODE)
            util.npy_summary(cfg.DUMP_FILES_DECODE, file_name)
        if os.path.isfile(os.path.join(cfg.DUMP_FILES_CPU, file_name)):
            LOG.debug("Print data in %s" % cfg.DUMP_FILES_CPU)
            util.npy_summary(cfg.DUMP_FILES_CPU, file_name)
        if os.path.isfile(os.path.join(cfg.DUMP_FILES_OVERFLOW_DECODE, file_name)):
            LOG.debug("Print data in %s" % cfg.DUMP_FILES_OVERFLOW_DECODE)
            util.npy_summary(cfg.DUMP_FILES_OVERFLOW_DECODE, file_name)

    def get_npu_dump_files_by_op(self, op):
        npu_files = {}
        match_name = op.type() + '.' + op.name().replace('/', '_').replace('.', '_') + '\\.'
        for f in self.npu_dump_files():
            if re.match(match_name, f):
                npu_files[f] = self.npu_dump_files()[f]
        return npu_files

    def get_npu_dump_decode_files_by_op(self, op):
        match_name = op.type() + '.' + op.name().replace('/', '_').replace('.', '_') + '\\.'
        dump_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_DECODE, match_name)
        if len(dump_decode_files) == 0:
            self._decode_npu_dump_files_by_op(op)
            dump_decode_files = util.list_npu_dump_decode_files(cfg.DUMP_FILES_DECODE, match_name)
        return dump_decode_files

    def get_cpu_dump_files_by_op(self, op):
        cpu_files = {}
        match_name = op.name().replace('/', '_').replace('.', '_') + '\\.'
        for f in self.cpu_dump_files():
            if re.match(match_name, f):
                cpu_files[f] = self.cpu_dump_files()[f]
        return cpu_files

    def _parse_npu_dump_files(self):
        self.npu_files, self.npu_parent_dirs = util.list_dump_files(cfg.DUMP_FILES_NPU)

    def _parse_cpu_dump_files(self):
        self.cpu_files = util.list_cpu_dump_decode_files(cfg.DUMP_FILES_CPU)

    def _decode_npu_dump_files_by_op(self, op):
        dump_files = self.get_npu_dump_files_by_op(op)
        for dump_file in dump_files.values():
            util.convert_dump_to_npy(dump_file['path'], cfg.DUMP_FILES_DECODE)

    def decode_all_dump(self):
        with Progress() as process:
            task = process.add_task('[green]Decode Dump files...', total=len(self.npu_files))
            for file_name in self.npu_files:
                file_info = self.npu_files[file_name]
                util.convert_dump_to_npy(file_info['path'], cfg.DUMP_FILES_DECODE)
                process.update(task)
