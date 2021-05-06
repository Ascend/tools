# coding=utf-8
import collections
import logging
import os
from lib.util import util
from lib.precision_tool_exception import catch_tool_exception
from lib.precision_tool_exception import PrecisionToolException

CKPT_META_SHUFFIX='.meta'


class TensorflowGraph(object):
    def __init__(self):
        """"""
        self.cpu_op_list = None
        self.log = util.get_log()

    @catch_tool_exception
    def get_op_list(self, ckpt_path=None):
        if self.cpu_op_list is None:
            self._convert_ckpt_to_graph(ckpt_path)
        return self.cpu_op_list

    def _convert_ckpt_to_graph(self, ckpt_path):
        log_level = self.log.level
        try:
            self.log.setLevel('ERROR')
            import tensorflow as tf
            self.log.setLevel(log_level)
        except ImportError as err:
            self.log.setLevel(log_level)
            raise PrecisionToolException("Import tensorflow failed.")
        meta_files = util.list_cpu_graph_files(ckpt_path)
        if len(meta_files) == 0:
            raise PrecisionToolException("Can not find any ckpt meta files.")
        file_list = sorted(meta_files.values(), key=lambda x: x['timestamp'])
        ckpt_file = file_list[-1]
        self.log.info("Find %d tf ckpt meta files, choose [%s]" % (len(meta_files), ckpt_file['file_name']))
        self.cpu_op_list = collections.OrderedDict()
        saver = tf.train.import_meta_graph(ckpt_file['path'], clear_devices=True)
        graph = tf.get_default_graph()
        for op in graph.get_operations():
            self.cpu_op_list[op.name] = op
