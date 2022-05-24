# coding=utf-8
from ..util.util import util

ATTR = 'attr'
ATTR_KEY = 'key'
ATTR_VALUE = 'value'
DATA_DUMP_ORIGIN_OUTPUT_INDEX = '_datadump_origin_output_index'
FUSION_ORIGIN_OUTPUT_INDEX = '_fusion_origin_output_index'
DATA_DUMP_ORIGIN_NAME = '_datadump_origin_name'
ORIGIN_FORMAT = 'origin_format'
ORIGIN_SHAPE = 'origin_shape'
VALUE_RANGE = 'value_range'
SHAPE_RANGE = 'shape_range'
DT_STRING = 's'
DT_INT = 'i'
DT_LIST_LIST_INT = 'list_list_int'
DT_LIST_LIST_I = 'list_list_i'
DT_LIST = 'list'
DT_LIST_INT = 'list_i'
DATA_TYPE_DEFAULT_VALUE = {
    'i': 0,
    's': ''
}


class Desc(object):
    """ Op desc
        shape: data shape
        dtype: data type
        format: data format
        npu_file: npu file name/path
        cpu_file: cpu file name/path
        idx: input idx
    """
    def __init__(self, desc_json, index):
        self.desc_json = desc_json
        self.index = index
        self.log = util.get_log()

    def idx(self):
        return self.index

    def shape(self):
        return self.desc_json['shape']['dim'] if 'shape' in self.desc_json else []

    def dtype(self):
        return self.desc_json['dtype'] if 'dtype' in self.desc_json else ''

    def format(self):
        return self.desc_json['layout'] if 'layout' in self.desc_json else []

    def origin_shape(self):
        return self._get_attr_list(ORIGIN_SHAPE, DT_INT)

    def origin_format(self):
        return self._get_attr(ORIGIN_FORMAT, DT_STRING)

    def value_range(self):
        return self._get_attr_list_list(VALUE_RANGE, DT_LIST_INT)

    def shape_range(self):
        return self._get_attr_list_list(SHAPE_RANGE, DT_LIST_INT)

    def _get_attr_list_list(self, key, data_type):
        val = self._get_attr_base(key, DT_LIST_LIST_INT)
        if val is None or DT_LIST_LIST_I not in val:
            return []
        res = []
        for item in val[DT_LIST_LIST_I]:
            if data_type in item:
                res.append(item[data_type])
        return res

    def _get_attr_list(self, key, data_type):
        val = self._get_attr_base(key, DT_LIST)
        return val[data_type] if val is not None and data_type in val else []

    def _get_attr(self, key, data_type):
        val = self._get_attr_base(key, data_type)
        return val if val is not None else DATA_TYPE_DEFAULT_VALUE[data_type]

    def _get_attr_base(self, key, data_type):
        if ATTR in self.desc_json:
            for attr in self.desc_json[ATTR]:
                if attr[ATTR_KEY] == key:
                    if attr[ATTR_VALUE] is not None and data_type in attr[ATTR_VALUE]:
                        return attr[ATTR_VALUE][data_type]
        return None

    def compare(self, right_desc):
        if self.dtype() == right_desc.dtype() and self.format() == right_desc.format():
            return "[green][%d] [%s][%s] %s[/green]" % (self.idx(), self.dtype(), self.format(), self.shape()), True
        else:
            return "[yellow][%d] [%s][%s] %s | [%s][%s] %s[/yellow]" % (
                self.idx(), self.dtype(), self.format(), self.shape(),
                right_desc.dtype(), right_desc.format(), right_desc.shape()), False

    def data_dump_origin_name(self):
        return ''


class InputDesc(Desc):
    def __init__(self, name, desc_json, index):
        super(InputDesc, self).__init__(desc_json, index)
        if name == '':
            self.log.warning('invalid input name.')
        name_info = name.split(':')
        self.op_name = name
        self.peer_index = -2
        if len(name_info) == 2:
            self.op_name = name_info[0]
            self.peer_index = int(name_info[1])

    def name(self):
        return self.op_name

    def peer_idx(self):
        return self.peer_index

    def is_control(self):
        return self.peer_index == -1

    def summary(self, origin_txt=False):
        """idx | dtype | format | shape | [blue]value_range | shape_range| origin_shape[/blue] | op_name | peer_idx"""
        if origin_txt:
            return "[%d][%s][%s]%s %s:%d" % (self.idx(), self.dtype(), self.format(),
                                             self.shape(), self.name(), self.peer_idx())
        return "[green][%d][/green][yellow][%s][%s]%s[/yellow][blue] %s %s %s[/blue] %s:%d" % (
            self.idx(), self.dtype(), self.format(), self.shape(),
            self.value_range(), self.shape_range(), self.origin_shape(), self.name(), self.peer_idx())


class OutputDesc(Desc):
    def __init__(self, name, desc_json, index):
        super(OutputDesc, self).__init__(desc_json, index)
        if name == '':
            self.log.warning('invalid output name.')
        self.op_names = name.split(':')

    def names(self):
        return self.op_names

    def summary(self, origin_txt=False):
        if origin_txt:
            return "[%d][%s][%s]%s %s" % (self.idx(), self.dtype(), self.format(), self.shape(), self.names())
        return "[green][%d][/green][yellow][%s][%s]%s[/yellow][blue] %s %s %s[/blue] %s" % (
            self.idx(), self.dtype(), self.format(), self.shape(),
            self.value_range(), self.shape_range(), self.origin_shape(), self.names())

    def data_dump_origin_name(self):
        return self._get_attr(DATA_DUMP_ORIGIN_NAME, DT_STRING)

    def data_dump_origin_output_index(self):
        return self._get_attr(DATA_DUMP_ORIGIN_OUTPUT_INDEX, DT_INT)
