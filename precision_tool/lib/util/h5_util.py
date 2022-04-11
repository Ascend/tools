import os
import numpy as np

try:
    import h5py
except ImportError as import_err:
    h5py = None
    print("Failed to import h5py. some function may disable. Run 'pip3 install h5py' to fix it.",
          import_err)

from ..util.util import util
from ..util.constant import Constant
from ..config import config as cfg


class IdxType(object):
    # /batch_norm/88/input/xxx
    OP_TYPE = 'OP_TYPE'
    OP_NAME = 'OP_NAME'
    OP_ANC = 'OP_ANC'


H5_NAME_IDX = [IdxType.OP_TYPE, IdxType.OP_NAME, IdxType.OP_ANC]


class H5OpDesc(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data


class H5Op(object):
    def __init__(self, tid):
        self.id = tid
        self.inputs = []
        self.outputs = []


class H5Util(object):
    def __init__(self, file_name):
        self.log = util.get_log()
        self.file_name = file_name
        self.h5 = None
        self.ops = {}
        self._prepare()

    def __del__(self):
        if self.h5 is not None:
            self.h5.close()

    def get_tensor_by_name(self, tensor_name):
        if self.h5 is None:
            self.log.warning("h5 file is None.")
            return None
        if tensor_name in self.h5:
            return np.array(self.h5[tensor_name])
        return None

    def print_tensor(self, tensor_name):
        tensor = self.get_tensor_by_name(tensor_name)
        if tensor is None:
            self.log.warning("Tensor:%s not exist." % tensor_name)
            return
        file_path = self._dump_numpy(tensor_name, tensor)
        util.print_npy_summary(os.path.dirname(file_path), os.path.basename(file_path))

    def _prepare(self):
        if not os.path.isfile(self.file_name) or not str(self.file_name).endswith(Constant.Suffix.H5):
            self.log.error("File [%s] not exist or not a h5 file" % self.file_name)
        if h5py is None:
            self.log.warning("Can not find python module h5py.")
        self.h5 = h5py.File(self.file_name, 'r')
        # self._list_tensors(self.h5)

    def _list_tensors(self, h5, idx=0, name=''):
        for item in h5:
            if isinstance(h5[item], h5py.Group):
                item_name = name + '/' + item
                print(item_name)
                # check
                if H5_NAME_IDX[idx] == IdxType.OP_NAME and item_name not in self.ops:
                    self.ops[item_name] = H5Op(item)
                if H5_NAME_IDX[idx] == IdxType.OP_ANC:
                    self.ops[item_name] = H5Op(item)
                self._list_tensors(h5[item], idx + 1, item_name)

    def _dump_numpy(self, tensor_name, tensor):
        if not os.path.exists(cfg.DUMP_DECODE_DIR):
            util.create_dir(cfg.DUMP_DECODE_DIR)
        file_name = tensor_name.replace('/', '_').strip('_') + '.npy'
        file_path = os.path.join(cfg.DUMP_DECODE_DIR, file_name)
        self.log("Dump file: %s" % file_path)
        np.save(file_path, tensor)
        return file_path
