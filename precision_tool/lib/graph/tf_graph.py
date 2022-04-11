# coding=utf-8
import collections
import logging
import os
from ..util.util import util
from ..util.precision_tool_exception import catch_tool_exception
from ..util.precision_tool_exception import PrecisionToolException
from ..config import config as cfg

CKPT_META_SHUFFIX='.meta'


class TfGraph(object):
    def __init__(self, graph_root=cfg.TF_GRAPH_DIR):
        """"""
        self.graph_root = graph_root
        self.log = util.get_log()
        self.op_list = collections.OrderedDict()

    @catch_tool_exception
    def get_op_list(self, ckpt_path=None):
        if self.op_list is None:
            self._convert_ckpt_to_graph(ckpt_path)
        return self.op_list

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
        self.op_list = collections.OrderedDict()
        saver = tf.train.import_meta_graph(ckpt_file['path'], clear_devices=True)
        graph = tf.get_default_graph()
        for op in graph.get_operations():
            self.op_list[op.name] = op
