# coding=utf-8
import os
import numpy as np
from ..adapter.tf_adapter import TfAdapter
from ..dump.tf_dump import TfDump
from ..util.util import util
from ..config import config as cfg
from ..util.precision_tool_exception import PrecisionToolException


class TrainAnalysis(object):
    def __init__(self):
        self.log = util.get_log()
        self.tf_adapter = TfAdapter()

    @staticmethod
    def gen_feed_file_name(name):
        file_name = str(name).replace(':', '_').replace('/', '_') + '.npy'
        return os.path.join(cfg.TF_CKPT_INPUT_DIR, file_name)

    def _init_session(self, device='npu', action='dump'):
        """"""
        import tensorflow as tf
        if device == 'npu':
            # util.execute_command('source %s', cfg.ASCEND_SET_ENV)
            return tf.Session(config=self.tf_adapter.session_dump_config(None, action=action))
        sess = tf.Session(config=tf.ConfigProto())
        return self.tf_adapter.sess_dump(sess)

    def _reset_dropout_rate(self, graph):
        import tensorflow as tf
        for op in graph.get_operations():
            if 'dropout' in op.name and 'rate' in op.name:
                self.log.debug("Find dropout rate node [%s][%s]" % (op.type, op.name))
                # tensor = graph.get_tensor_by_name(op.name)
                if op.type != 'Const':
                    self.log.warning("Drop out op [%s] is not Const, skip reset rate. May cause difference.")
                    continue
                op._set_attr('value', tf.AttrValue(tensor=tf.make_tensor_proto(0.0, tf.float32)))
                self.log.debug("Set op: %s" % str(op))

    def _prepare_graph(self, graph):
        graph.seed = cfg.DUMP_SEED
        self._reset_dropout_rate(graph)
        return graph

    def _load_train_graph(self, sess):
        import tensorflow as tf
        if util.empty_dir(cfg.TF_CKPT_ROOT):
            raise PrecisionToolException('checkpoint dir [%s] is empty, can not run train analysis process.' %
                                         cfg.TF_CKPT_ROOT)
        checkpoint = tf.train.latest_checkpoint(cfg.TF_CKPT_ROOT)
        if checkpoint is None:
            raise PrecisionToolException('Load ckpt failed from [%s].' % cfg.TF_CKPT_ROOT)
        saver = tf.train.import_meta_graph(checkpoint + '.meta')
        self._prepare_graph(tf.get_default_graph())
        saver.restore(sess, checkpoint)
        return tf.get_default_graph()

    @staticmethod
    def _get_input_from_graph(graph):
        input_nodes = []
        tensor_index = {}
        for op in graph.get_operations():
            if 'Placeholder' == op.type:
                if op.name in tensor_index:
                    tensor_index[op.name] += 1
                else:
                    tensor_index[op.name] = 0
                node = graph.get_tensor_by_name(op.name + ':' + str(tensor_index[op.name]))
                input_nodes.append(node)
        return input_nodes

    def _get_input_tensors(self, input_nodes):
        feed_map = {}
        for node in input_nodes:
            file_name = self.gen_feed_file_name(node.name)
            if os.path.isfile(file_name):
                feed_map[node] = np.load(file_name)
            else:
                # TD data type
                feed_map[node] = np.random.random(node.shape)
        return feed_map

    def _build_feed_map(self, graph):
        input_nodes = self._get_input_from_graph(graph)
        return self._get_input_tensors(input_nodes)

    def _analysis(self, device, action='dump'):
        import tensorflow as tf
        if device == 'npu':
            import npu_bridge.npu_init
        sess = self._init_session(device, action=action)
        graph = self._load_train_graph(sess)
        train_op = tf.get_collection(tf.GraphKeys.TRAIN_OP)
        feed_map = self._build_feed_map(graph)
        sess.run(train_op, feed_dict=feed_map)
        if device == 'cpu':
            tf_dump = TfDump()
            tf_dump.run_tf_dbg_dump()

    def run(self, device='all', action='dump'):
        """
        :param device: all | npu | cpu
        :param action: dump | overflow | fusion_switch | fusion_off
        :return:
        """
        if device == 'all':
            self._analysis('cpu', action)
            self._analysis('npu', action)
        else:
            self._analysis(device, action)
