# coding=utf-8
from ..util.util import util
from ..util.h5_util import H5Util
from ..config import config as cfg


class PtDump(object):
    def __init__(self, data_dir):
        self.log = util.get_log()
        self.npu = None
        self.gpu = None
        self.data_dir = data_dir

    def prepare(self):
        util.create_dir(cfg.PT_NPU_DIR)
        util.create_dir(cfg.PT_GPU_DIR)
        if not util.empty_dir(cfg.PT_NPU_DIR):
            self.npu = H5Util()
        if not util.empty_dir(cfg.PT_GPU_DIR):
            self.gpu = H5Util()

    def get_dump_files_by_name(self, file_name):
        """Get dump files by name"""
        print(file_name)
        return {}
