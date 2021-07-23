# coding=utf-8
from lib.util import util

ATTR = 'attr'
ATTR_KEY = 'key'
ATTR_VALUE = 'value'
DATA_DUMP_ORIGIN_OUTPUT_INDEX = '_datadump_origin_output_index'
FUSION_ORIGIN_OUTPUT_INDEX = '_fusion_origin_output_index'
DATA_DUMP_ORIGIN_NAME = '_datadump_origin_name'
ORIGIN_FORMAT = 'origin_format'
ORIGIN_SHAPE = 'origin_shape'
DT_STRING = 's'
DT_INT = 'i'
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

    def _get_attr_list(self, key, data_type):
        if ATTR in self.desc_json:
            for attr in self.desc_json[ATTR]:
                if attr[ATTR_KEY] == key:
                    return attr[ATTR_VALUE]['list'][data_type]
        return []

    def _get_attr(self, key, data_type):
        if ATTR in self.desc_json:
            for attr in self.desc_json[ATTR]:
                if attr[ATTR_KEY] == key:
                    return attr[ATTR_VALUE][data_type]
        return DATA_TYPE_DEFAULT_VALUE[data_type]

    def compare(self, right_desc):
        if self.dtype() == right_desc.dtype() and self.format() == right_desc.format():
            return "[green][%d] [%s][%s] %s[/green]" % (self.idx(), self.dtype(), self.format(), self.shape()), True
        else:
            return "[yellow][%d] [%s][%s] %s | [%s][%s] %s[/yellow]" % (
                self.idx(), self.dtype(), self.format(), self.shape(),
                right_desc.dtype(), right_desc.format(), right_desc.shape()), False


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
        if origin_txt:
            return "[%d][%s][%s]%s %s:%d" % (self.idx(), self.dtype(), self.format(),
                                             self.shape(), self.name(), self.peer_idx())
        return "[green][%d][/green][yellow][%s][%s]%s[/yellow] %s:%d" % (
            self.idx(), self.dtype(), self.format(), self.shape(), self.name(), self.peer_idx())


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
        return "[green][%d][/green][yellow][%s][%s]%s[/yellow] %s" % (
            self.idx(), self.dtype(), self.format(), self.shape(), self.names())

    def data_dump_origin_name(self):
        return self._get_attr(DATA_DUMP_ORIGIN_NAME, DT_STRING)

    def data_dump_origin_output_index(self):
        return self._get_attr(DATA_DUMP_ORIGIN_OUTPUT_INDEX, DT_INT)
