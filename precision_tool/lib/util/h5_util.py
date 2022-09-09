import collections
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


def gen_h5_data_name(name, prefix='npu'):
    return "%s_h5%s.npy" % (prefix, name.replace('/', '_'))


class H5Data(object):
    def __init__(self, data, prefix='npu'):
        self.data = data
        self.prefix = prefix
        self.name = gen_h5_data_name(self.data.name, self.prefix)

    def np_data(self):
        np_data = np.array(self.data)
        self._save(np_data)
        return np_data

    def _save(self, data):
        path = os.path.join(cfg.PT_DUMP_DECODE_DIR, self.name)
        np.save(path, data)


class H5Op(object):
    def __init__(self, name, h5_node, prefix='npu'):
        self.log = util.get_log()
        self.name = name
        self.prefix = prefix
        self.h5_node = h5_node
        self.inputs = {}
        self.outputs = {}
        self.group = {
            'grads': {},
            'tensors': {},
            'grad_inputs': {},
            'result': {}
        }
        '''
        self.input_grad = {}
        self.output_grad = {}
        self.input_tensor = {}
        self.output_tensor = {}
        '''
        self._prepare()

    def summary(self):
        summary_txt = []
        summary_txt.extend(self._gen_txt(self.inputs, '-Input:'))
        summary_txt.extend(self._gen_txt(self.outputs, '-Output:'))
        summary_txt.extend(self._gen_txt(self.group['grads'], 'Grads:'))
        summary_txt.extend(self._gen_txt(self.group['tensors'], '-Tensors:'))
        summary_txt.extend(self._gen_txt(self.group['grad_inputs'], '-GradInputs:'))
        summary_txt.extend(self._gen_txt(self.group['result'], '-Result:'))
        return Constant.NEW_LINE.join(summary_txt)

    @staticmethod
    def _gen_txt(h5_data, name):
        if len(h5_data) == 0:
            return []
        txt = [name]
        for idx, data in enumerate(h5_data.values()):
            txt.append(' └─[green][%s][/green] %s' % (idx, data.name))
            txt.append('   └─ [yellow]%s[/yellow]' % util.gen_npy_info_txt(data.np_data()))
        return txt

    def _parse_group(self, node):
        sub_node_type = node.name.split('/')[-1]
        if sub_node_type in self.group.keys():
            for item in node:
                sub_node = node[item]
                if isinstance(sub_node, h5py.Dataset):
                    self.group[sub_node_type][item] = H5Data(sub_node, self.prefix)
                else:
                    self.log.warning("Unknown sub node: %s" % sub_node)
        else:
            self.log.warning("Unknown sub node type: %s(%s)" % (sub_node_type, node))

    def _prepare_input_output(self, node, desc_type):
        for desc_name in node:
            sub_node = node[desc_name]
            if isinstance(sub_node, h5py.Group):
                self._parse_group(sub_node)
            elif isinstance(sub_node, h5py.Dataset):
                update_dict = self.inputs if desc_type == 'input' else self.outputs
                update_dict[desc_name] = H5Data(sub_node, self.prefix)
            else:
                self.log.warning("Unknown type: %s(%s)" % (type(sub_node), sub_node))

    def _prepare(self):
        for desc_type in self.h5_node:
            if desc_type in ['input', 'output']:
                self._prepare_input_output(self.h5_node[desc_type], desc_type)
            else:
                self.log.warning("Unknown desc type: %s(%s)" % (desc_type, self.h5_node))


class H5Util(object):
    def __init__(self, file_name, prefix):
        self.log = util.get_log()
        self.file_name = file_name
        self.prefix = prefix
        self.h5 = None
        self.ops = collections.OrderedDict()
        self._prepare()

    def __del__(self):
        if self.h5 is not None:
            self.h5.close()

    def get_op(self, op_id):
        if op_id in self.ops:
            return self.ops[op_id]
        self.log.warning("Can not find any h5 op id: %s" % op_id)
        return None

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
        self._list_tensors(self.h5)

    def _list_tensors(self, h5, idx=0, name=''):
        for item in h5:
            item_name = name + '/' + item
            if idx == 1:
                self.ops[str(item)] = H5Op(item_name, h5[item_name], self.prefix)
                continue
            self._list_tensors(h5[item], idx+1, item_name)

    def _list_tensors_loop(self, h5, idx=0, name=''):
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
        if not os.path.exists(cfg.PT_DUMP_DECODE_DIR):
            util.create_dir(cfg.PT_DUMP_DECODE_DIR)
        file_name = tensor_name.replace('/', '_').strip('_') + '.npy'
        file_path = os.path.join(cfg.PT_DUMP_DECODE_DIR, file_name)
        self.log("Dump file: %s" % file_path)
        np.save(file_path, tensor)
        return file_path
