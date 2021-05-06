# coding=utf-8
from lib.util import util


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
        if 'attr' not in self.desc_json:
            return []
        for attr in self.desc_json['attr']:
            if attr['key'] == 'origin_format':
                return attr['value']['list']['i']

    def origin_format(self):
        if 'attr' not in self.desc_json:
            return []
        for attr in self.desc_json['attr']:
            if attr['key'] == 'origin_format':
                return attr['value']['s']


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
