# coding=utf-8
import os
from ..util.util import util
from ..config import config as cfg
FLAG_DUMP_GE_GRAPH = 'DUMP_GE_GRAPH'
FLAG_DUMP_GRAPH_LEVEL = 'DUMP_GRAPH_LEVEL'
FLAG_DUMP_GRAPH_PATH = 'DUMP_GRAPH_PATH'
FLAG_NPU_DUMP_GRAPH = 'NPU_DUMP_GRAPH'
FUSION_SWITCH_FILE = os.path.join(os.path.dirname(__file__), '../config/fusion_switch.cfg')
FUSION_OFF_FILE = os.path.join(os.path.dirname(__file__), '../config/fusion_off.cfg')


class TfAdapter(object):
    def __init__(self):
        self.log = util.get_log()

    def sess_dump(self, sess):
        """wrapper session with dumping debug wrapper.
        In session run mode. Use sess=sess_dump(sess)
        :param sess: origin session
        :return: Session
        """
        from tensorflow.python import debug as tf_debug
        self._init()
        return tf_debug.DumpingDebugWrapperSession(sess, cfg.TF_DEBUG_DUMP_DIR)

    def estimator_dump(self):
        """In estimator mode. estim_spec = tf.estimator.EstimatorSpec(traing_hooks=[estimator_dump()])
        :return:
        """
        from tensorflow.python import debug as tf_debug
        self._init()
        return tf_debug.DumpingDebugHook(cfg.TF_DEBUG_DUMP_DIR)

    def session_dump_config(self, session_config=None, action=None):
        """
        In TF session mode. set dump_config in session_config.
        exp. config = session_dump_config()
             config.[set your own configs]
             with tf.Session(config=config) as sess:
                sess.run(_)
                tf_debug.LocalCLIDebugWrapperSession(sess=sess, ui_type="readline")
        :param session_config: original session config
        :param action: if set action, no need to start app with cli wrapper
        :return: config_pb2.ConfigProto
        """
        from tensorflow.core.protobuf import config_pb2
        from tensorflow.core.protobuf.rewriter_config_pb2 import RewriterConfig
        if ((not isinstance(session_config, config_pb2.ConfigProto)) and
                (not issubclass(type(session_config), config_pb2.ConfigProto))):
            session_config = config_pb2.ConfigProto()
        custom_op = None
        for existed_custom_op in session_config.graph_options.rewrite_options.custom_optimizers:
            if existed_custom_op.name == 'NpuOptimizer':
                custom_op = existed_custom_op
        if custom_op is None:
            custom_op = session_config.graph_options.rewrite_options.custom_optimizers.add()
        custom_op.name = 'NpuOptimizer'
        custom_op.parameter_map['use_off_line'].b = True
        self.update_custom_op(custom_op, action)
        session_config.graph_options.rewrite_options.remapping = RewriterConfig.OFF
        return session_config

    def estimator_dump_config(self, action=None):
        """return DumpConfig.
        In estimator mode. set dump_config in NPURunConfig().
        exp. config = NPURunConfig(dump_config=estimator_dum_config(), session_config=session_config)
        :return: DumpConfig
        """
        from npu_bridge.npu_init import DumpConfig
        self._init()
        if self._is_overflow(action):
            config = DumpConfig(enable_dump_debug=True, dump_path=cfg.NPU_OVERFLOW_DUMP_DIR, dump_mode="all")
        elif self._is_dump(action):
            config = DumpConfig(enable_dump=True, dump_path=cfg.DEFAULT_NPU_DUMP_DIR, dump_step=cfg.TF_DUMP_STEP,
                                dump_mode="all")
        else:
            config = DumpConfig()
        return config

    def npu_device_dump_config(self, npu_device, action):
        """For tf2.x
        :param npu_device: npu_device
        :param action: dump | overflow| fusion_off | fusion_switch
        :return: npu_device
        """
        self._init()
        if self._is_overflow(action):
            npu_device.global_options().dump_config.enable_dump_debug = True
            npu_device.global_options().dump_config.dump_path = cfg.NPU_OVERFLOW_DUMP_DIR
            npu_device.global_options().dump_config.dump_debug_mode = "all"
            npu_device.global_options().op_debug_level = cfg.OP_DEBUG_LEVEL
        if self._is_dump(action):
            npu_device.global_options().dump_config.enable_dump = True
            npu_device.global_options().dump_config.dump_path = cfg.DEFAULT_NPU_DUMP_DIR
            npu_device.global_options().dump_config.dump_debug_mode = "all"
            npu_device.global_options().op_debug_level = cfg.OP_DEBUG_LEVEL
            npu_device.global_options().dump_config.dump_step = cfg.TF_DUMP_STEP
        if self._is_fusion_off(action):
            npu_device.global_options().fusion_switch_file = FUSION_OFF_FILE
            print("[PrecisionTool] Set fusion switch file: ", FUSION_OFF_FILE)
        if self._is_fusion_switch(action):
            npu_device.global_options().fusion_switch_file = FUSION_SWITCH_FILE
            print("[PrecisionTool] Set fusion switch file: ", FUSION_SWITCH_FILE)
        return npu_device

    def update_custom_op(self, custom_op, action=None):
        """Update custom_op
        :param custom_op: origin custom op
        :param action: dump | overflow | fusion_off | fusion_switch
        :return:
        """
        import tensorflow as tf
        self._init()
        custom_op.parameter_map['debug_dir'].s = tf.compat.as_bytes(cfg.DEFAULT_OP_DEBUG_DIR)
        if self._is_overflow(action):
            custom_op.parameter_map['enable_dump_debug'].b = True
            custom_op.parameter_map['dump_debug_mode'].s = tf.compat.as_bytes("all")
            custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.NPU_OVERFLOW_DUMP_DIR)
            custom_op.parameter_map['op_debug_level'].i = cfg.OP_DEBUG_LEVEL
        elif self._is_dump(action):
            custom_op.parameter_map['enable_dump'].b = True
            custom_op.parameter_map['dump_mode'].s = tf.compat.as_bytes("all")
            custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.DEFAULT_NPU_DUMP_DIR)
            custom_op.parameter_map['op_debug_level'].i = cfg.OP_DEBUG_LEVEL
            custom_op.parameter_map['dump_step'].s = tf.compat.as_bytes(cfg.TF_DUMP_STEP)
        if self._is_fusion_off(action):
            custom_op.parameter_map['fusion_switch_file'].s = tf.compat.as_bytes(FUSION_OFF_FILE)
            print("[PrecisionTool] Set fusion switch file: ", FUSION_OFF_FILE)
        elif self._is_fusion_switch(action):
            custom_op.parameter_map['fusion_switch_file'].s = tf.compat.as_bytes(FUSION_SWITCH_FILE)
            print("[PrecisionTool] Set fusion switch file: ", FUSION_SWITCH_FILE)
        return custom_op

    def _init(self):
        util.create_dir(cfg.DEFAULT_OP_DEBUG_DIR)
        util.create_dir(cfg.NPU_OVERFLOW_DUMP_DIR)
        util.create_dir(cfg.DEFAULT_NPU_DUMP_DIR)
        util.create_dir(cfg.DEFAULT_NPU_GRAPH_DIR)
        self._set_dump_graph_flags()

    @staticmethod
    def _set_dump_graph_flags():
        os.environ[FLAG_DUMP_GE_GRAPH] = str(cfg.DUMP_GE_GRAPH_VALUE)
        os.environ[FLAG_DUMP_GRAPH_LEVEL] = str(cfg.DUMP_GRAPH_LEVEL_VALUE)
        os.environ[FLAG_DUMP_GRAPH_PATH] = cfg.DEFAULT_NPU_GRAPH_DIR
        os.environ[FLAG_NPU_DUMP_GRAPH] = 'true'

    @staticmethod
    def _is_dump(action):
        if action is not None:
            return 'dump' in action
        if cfg.PRECISION_TOOL_DUMP_FLAG in os.environ and os.environ[cfg.PRECISION_TOOL_DUMP_FLAG] == 'True':
            print("[PrecisionTool] enable npu dump >======")
            return True
        return False

    @staticmethod
    def _is_overflow(action):
        if action is not None:
            return 'overflow' in action
        if cfg.PRECISION_TOOL_OVERFLOW_FLAG in os.environ and os.environ[cfg.PRECISION_TOOL_OVERFLOW_FLAG] == 'True':
            print("[PrecisionTool] enable npu overflow >======")
            return True
        return False

    @staticmethod
    def _is_fusion_off(action):
        return 'fusion_off' in action if action is not None else False

    @staticmethod
    def _is_fusion_switch(action):
        return ('fusion_switch' in action) if action is not None else False

