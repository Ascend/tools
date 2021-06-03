# coding=utf-8
import os
import re
from lib.util import util
from lib.constant import Constant
import config as cfg
from lib.precision_tool_exception import catch_tool_exception
from lib.precision_tool_exception import PrecisionToolException


class TfDump(object):
    def __init__(self, dump_root=cfg.TF_DUMP_DIR):
        self.log = util.get_log()
        self.dump_root = dump_root
        self.dump_files = None

    def prepare(self):
        if not os.path.exists(self.dump_root):
            util.create_dir(self.dump_root)
        self._parse_dump_files()

    def get_dump_files_by_op(self, op):
        """Get cpu dump files by op"""
        tf_files = {}
        match_name = op.name().replace('/', '_').replace('.', '_') + '\\.'
        for f in self.dump_files:
            if re.match(match_name, f):
                tf_files[f] = self.dump_files[f]
        return tf_files

    @catch_tool_exception
    def op_dump_summary(self, op):
        # cpu dump info
        if op is None:
            return ''
        cpu_dump_txt = ['TfDumpOutput:']
        cpu_dump_files = self.get_dump_files_by_op(op)
        for cpu_dump_file in cpu_dump_files.values():
            cpu_dump_txt.append(' -[green][%s][/green] %s' % (cpu_dump_file.idx, cpu_dump_file.file_name))
            cpu_dump_txt.append('   └─ [yellow]%s[/yellow]' % util.gen_npy_info_txt(cpu_dump_file.path))
        return Constant.NEW_LINE.join(cpu_dump_txt)

    def _parse_dump_files(self):
        self.dump_files = util.list_cpu_dump_decode_files(self.dump_root)
