import h5py
import os
import numpy as np

from lib.util import util
from lib.constant import Constant
import config as cfg


class H5Util(object):
    def __init__(self, file_name):
        self.log = util.get_log()
        self.file_name = file_name
        self.h5 = None
        self._prepare()

    def __del__(self):
        if self.h5 is not None:
            self.h5.close()

    def _prepare(self):
        if not os.path.isfile(self.file_name) or not str(self.file_name).endswith(Constant.Suffix.H5):
            self.log.error("File [%s] not exist or not a h5 file" % self.file_name)
        self.h5 = h5py.File(self.file_name, 'r')

    def get_tensor_by_name(self, tensor_name):
        if self.h5 is None:
            self.log.warning("h5 file is None.")
            return None
        return np.array(self.h5[tensor_name])

    def print_tensor(self, tensor_name):
        tensor = self.get_tensor_by_name(tensor_name)
        if tensor is None:
            self.log.warning("Tensor:%s not exist." % tensor_name)
            return
        file_path = self._dump_numpy(tensor_name, tensor)
        util.print_npy_summary(os.path.dirname(file_path), os.path.basename(file_path))

    def _dump_numpy(self, tensor_name, tensor):
        if not os.path.exists(cfg.DUMP_DECODE_DIR):
            util.create_dir(cfg.DUMP_DECODE_DIR)
        file_name = tensor_name.replace('/', '_').strip('_') + '.npy'
        file_path = os.path.join(cfg.DUMP_DECODE_DIR, file_name)
        self.log("Dump file: %s" % file_path)
        np.save(file_path, tensor)
        return file_path
