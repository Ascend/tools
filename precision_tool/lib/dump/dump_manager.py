# coding=utf-8
import os
import collections
from ..util.util import util
from ..util.constant import Constant
from .npu_dump import NpuDump
from .tf_dump import TfDump
from .pt_dump import PtDump
from ..config import config as cfg


class DumpManager(object):
    def __init__(self):
        self.npu_dumps = collections.OrderedDict()
        self.pt_dump = PtDump(cfg.PT_DIR)
        self.tf_dump = TfDump(cfg.TF_DUMP_DIR)
        self._init_dirs()

    def prepare(self):
        # 1. prepare npu dump
        sub_dirs = os.listdir(cfg.NPU_DIR)
        if len(sub_dirs) == 0:
            # create default
            sub_dirs = [Constant.DEFAULT_DEBUG_ID]
        sorted(sub_dirs)
        for sub_dir in sub_dirs:
            npu_dump = NpuDump(sub_dir)
            npu_dump.prepare()
            self.npu_dumps[sub_dir] = npu_dump
        # 2. prepare tf dump
        self.tf_dump.prepare()
        # 3. prepare pt dump
        self.pt_dump.prepare()

    def get_dump_root_dir(self, debug_id):
        if debug_id in self.npu_dumps:
            return self.npu_dumps[debug_id].dump_root
        return None

    def op_dump_summary(self, ops):
        npu_result = collections.OrderedDict()
        for debug_id, op in ops.items():
            if debug_id in self.npu_dumps:
                npu_result[debug_id] = collections.OrderedDict()
                for op_detail in op:
                    npu_result[debug_id][op_detail.graph_name] = self.npu_dumps[debug_id].op_dump_summary(op_detail)
        tf_result = None
        if self.tf_dump is not None and len(ops[Constant.DEFAULT_DEBUG_ID]) != 0:
            tf_result = self.tf_dump.op_dump_summary(ops[Constant.DEFAULT_DEBUG_ID][0])
        return npu_result, tf_result

    def convert_npu_dump(self, name, data_format=None, dst_path=None):
        for _, npu_dump in enumerate(self.npu_dumps):
            npu_dump.convert_npu_dump(name, data_format, dst_path)

    def print_tensor(self, file_name, is_convert):
        """Print numpy data file"""
        if os.path.isfile(file_name):
            return util.print_npy_summary(os.path.dirname(file_name), os.path.basename(file_name), is_convert)
        # file_name = file_name.replace('/', '_')
        # npu decode file
        npu_convert_files = self.npu_dumps[Constant.DEFAULT_DEBUG_ID].get_npu_dump_decode_files_by_name(file_name)
        self._print_tensors(npu_convert_files, is_convert)
        # util.list_npu_dump_convert_files(cfg.DECODE_DIR, file_name)
        # tf decode file
        tf_decode_files = self.tf_dump.get_dump_files_by_name(file_name, True)
        self._print_tensors(tf_decode_files, is_convert)
        # pt decode file
        pt_decode_files = self.pt_dump.get_dump_files_by_name(file_name)
        self._print_tensors(pt_decode_files, is_convert)

    @staticmethod
    def _print_tensors(file_infos, is_convert):
        if file_infos is not None:
            for file_info in file_infos.values():
                util.print_npy_summary(file_info.dir_path, file_info.file_name, is_convert)

    @staticmethod
    def _init_dirs():
        """Create dump file dirs"""
        util.create_dir(cfg.DUMP_DECODE_DIR)
        util.create_dir(cfg.NPU_OVERFLOW_DUMP_DIR)
        util.create_dir(cfg.OVERFLOW_DECODE_DIR)
        util.create_dir(cfg.TF_DUMP_DIR)
        util.create_dir(cfg.PT_DIR)
