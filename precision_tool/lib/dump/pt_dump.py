# coding=utf-8
from ..util.util import util
from ..util.h5_util import H5Util
from ..util.h5_util import gen_h5_data_name
from ..config import config as cfg
from ..util.constant import Constant


class PtDump(object):
    def __init__(self, data_dir):
        self.log = util.get_log()
        self.npu = None
        self.gpu = None
        self.data_dir = data_dir

    def prepare(self):
        util.create_dir(cfg.PT_NPU_DIR)
        util.create_dir(cfg.PT_GPU_DIR)
        util.create_dir(cfg.PT_DUMP_DECODE_DIR)
        if not util.empty_dir(cfg.PT_NPU_DIR):
            npu_h5_files = util.list_h5_files(cfg.PT_NPU_DIR)
            if len(npu_h5_files) != 0:
                file_list = sorted(npu_h5_files.values(), key=lambda x: x.timestamp)
                self.npu = H5Util(file_list[0].path, prefix='npu')
        if not util.empty_dir(cfg.PT_GPU_DIR):
            gpu_h5_files = util.list_h5_files(cfg.PT_GPU_DIR)
            if len(gpu_h5_files) != 0:
                file_list = sorted(gpu_h5_files.values(), key=lambda x: x.timestamp)
                self.gpu = H5Util(file_list[0].path, prefix='gpu')

    @staticmethod
    def get_dump_files_by_name(file_name):
        """Get dump files by name"""
        npu_pattern = gen_h5_data_name(file_name, 'npu') if '/' in file_name else file_name
        gpu_pattern = gen_h5_data_name(file_name, 'gpu') if '/' in file_name else file_name
        files = util.list_numpy_files(cfg.PT_DUMP_DECODE_DIR, extern_pattern=npu_pattern)
        files.update(util.list_numpy_files(cfg.PT_DUMP_DECODE_DIR, extern_pattern=gpu_pattern))
        return files

    def op_dump_summary(self, ir_name):
        summary_list = []
        op_id = self._parse_op_id(ir_name)
        if self.npu is not None:
            h5_op = self.npu.get_op(op_id)
            if h5_op is not None:
                summary_list.append('NPU:')
                summary_list.append(h5_op.summary())
        if self.gpu is not None:
            h5_op = self.gpu.get_op(op_id)
            if h5_op is not None:
                summary_list.append('GPU:')
                summary_list.append(h5_op.summary())
        return Constant.NEW_LINE.join(summary_list)

    @staticmethod
    def _parse_op_id(ir_name):
        op_id = str(ir_name)
        if op_id.isnumeric():
            op_id = ir_name
        else:
            for name in op_id.split('/'):
                if name.isnumeric():
                    op_id = name
                    break
        return op_id
