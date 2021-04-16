# coding=utf-8
import os
import tensorflow as tf

CKPT_META_SHUFFIX='.meta'


class TensorflowGraph(object):
    def __init__(self):
        """"""
        self.cpu_op_list = {}

    def convert_ckpt_to_graph(self, ckpt_path):
        if not str(ckpt_path).endswith(CKPT_META_SHUFFIX):
            if os.path.isfile(ckpt_path + CKPT_META_SHUFFIX):
                ckpt_path = ckpt_path + CKPT_META_SHUFFIX
            elif os.path.isdir(ckpt_path):
                # find .meta
                sub_files = os.listdir(ckpt_path)
                for file_name in sub_files:
                    if file_name.endswith(CKPT_META_SHUFFIX):
                        ckpt_path = file_name
        if not str(ckpt_path).endswith(CKPT_META_SHUFFIX):
            # LOG.error("Path [%s] is not valid.", ckpt_path)
            return
        saver = tf.train.import_meta_graph(ckpt_path, clear_devices=True)
        graph = tf.get_default_graph()
        for op in graph.get_operations():
            self.cpu_op_list[op.name] = op


