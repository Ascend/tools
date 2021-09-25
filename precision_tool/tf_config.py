# coding=utf-8
import os
import random
from tensorflow.core.protobuf import config_pb2
from tensorflow.core.protobuf.rewriter_config_pb2 import RewriterConfig
from tensorflow.python import debug as tf_debug
import tensorflow as tf
from . import config as cfg

FLAG_DUMP_GE_GRAPH = 'DUMP_GE_GRAPH'
FLAG_DUMP_GRAPH_LEVEL = 'DUMP_GRAPH_LEVEL'
FLAG_DUMP_GRAPH_PATH = 'DUMP_GRAPH_PATH'

# Fusion switch file path
FUSION_SWITCH_FILE = os.path.join(os.path.dirname(__file__), 'fusion_switch.cfg')
FUSION_OFF_FILE = os.path.join(os.path.dirname(__file__), 'fusion_off.cfg')

DEFAULT_OP_DEBUG_DIR = cfg.DEFAULT_OP_DEBUG_DIR


def seed_everything(seed=cfg.DUMP_SEED):
    # set random seed
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    tf.random.set_random_seed(seed)
    print("[PrecisionTool] Set Tensorflow random seed to %d success." % seed)
    try:
        import numpy as np
        np.random.seed(seed)
        print("[PrecisionTool] Set numpy random seed to %d success." % seed)
    except ImportError as err:
        np = None
        print("[PrecisionTool] No numpy module.", err)


# set global random seed
seed_everything()


def sess_dump(sess):
    """wrapper session with dumping debug wrapper.
    In session run mode. Use sess=sess_dump(sess)
    :param sess: origin session
    :return: Session
    """
    _init()
    return tf_debug.DumpingDebugWrapperSession(sess, cfg.TF_DEBUG_DUMP_DIR)


def estimator_dump():
    """In estimator mode. estim_spec = tf.estimator.EstimatorSpec(traing_hooks=[estimator_dump()])
    :return:
    """
    _init()
    return tf_debug.DumpingDebugHook(cfg.TF_DEBUG_DUMP_DIR)


def estimator_dump_config(action=None):
    """return DumpConfig.
    In estimator mode. set dump_config in NPURunConfig().
    exp. config = NPURunConfig(dump_config=estimator_dum_config(), session_config=session_config)
    :return: DumpConfig
    """
    from npu_bridge.npu_init import DumpConfig
    _init()
    if _is_overflow(action):
        config = DumpConfig(enable_dump_debug=True, dump_path=cfg.NPU_OVERFLOW_DUMP_DIR, dump_mode="all")
    elif _is_dump(action):
        config = DumpConfig(enable_dump=True, dump_path=cfg.DEFAULT_NPU_DUMP_DIR, dump_step=cfg.TF_DUMP_STEP,
                            dump_mode="all")
    else:
        config = DumpConfig()
    return config


def session_dump_config(session_config=None, action=None):
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
    update_custom_op(custom_op, action)
    session_config.graph_options.rewrite_options.remapping = RewriterConfig.OFF
    return session_config


def update_custom_op(custom_op, action=None):
    """Update custom_op
    :param custom_op: origin custom op
    :param action: dump | overflow | fusion_off | fusion_switch
    :return:
    """
    _init()
    custom_op.parameter_map['debug_dir'].s = tf.compat.as_bytes(cfg.DEFAULT_OP_DEBUG_DIR)
    if _is_overflow(action):
        custom_op.parameter_map['enable_dump_debug'].b = True
        custom_op.parameter_map['dump_debug_mode'].s = tf.compat.as_bytes("all")
        custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.NPU_OVERFLOW_DUMP_DIR)
        custom_op.parameter_map['op_debug_level'].i = cfg.OP_DEBUG_LEVEL
    elif _is_dump(action):
        custom_op.parameter_map['enable_dump'].b = True
        custom_op.parameter_map['dump_mode'].s = tf.compat.as_bytes("all")
        custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.DEFAULT_NPU_DUMP_DIR)
        custom_op.parameter_map['op_debug_level'].i = cfg.OP_DEBUG_LEVEL
        custom_op.parameter_map['dump_step'].s = tf.compat.as_bytes(cfg.TF_DUMP_STEP)
    if _is_fusion_off(action):
        custom_op.parameter_map['fusion_switch_file'].s = tf.compat.as_bytes(FUSION_OFF_FILE)
        print("[PrecisionTool] Set fusion switch file: ", FUSION_OFF_FILE)
    elif _is_fusion_switch(action):
        custom_op.parameter_map['fusion_switch_file'].s = tf.compat.as_bytes(FUSION_SWITCH_FILE)
        print("[PrecisionTool] Set fusion switch file: ", FUSION_SWITCH_FILE)
    return custom_op


def _init():
    _create_dir(cfg.DEFAULT_OP_DEBUG_DIR)
    _create_dir(cfg.NPU_OVERFLOW_DUMP_DIR)
    _create_dir(cfg.DEFAULT_NPU_DUMP_DIR)
    _create_dir(cfg.DEFAULT_NPU_GRAPH_DIR)
    _set_dump_graph_flags()


def _create_dir(path):
    """ create dir """
    if os.path.exists(path):
        return
    try:
        os.makedirs(path, mode=0o700)
    except OSError as err_msg:
        print("[PrecisionTool] Failed to create %s. %s" % (path, str(err_msg)))


def _unset_dump_graph_flags():
    if FLAG_DUMP_GE_GRAPH in os.environ:
        del os.environ[FLAG_DUMP_GE_GRAPH]
    if FLAG_DUMP_GRAPH_LEVEL in os.environ:
        del os.environ[FLAG_DUMP_GRAPH_LEVEL]
    if FLAG_DUMP_GRAPH_PATH in os.environ:
        del os.environ[FLAG_DUMP_GRAPH_PATH]


def _set_dump_graph_flags():
    os.environ[FLAG_DUMP_GE_GRAPH] = str(cfg.DUMP_GE_GRAPH_VALUE)
    os.environ[FLAG_DUMP_GRAPH_LEVEL] = str(cfg.DUMP_GRAPH_LEVEL_VALUE)
    os.environ[FLAG_DUMP_GRAPH_PATH] = cfg.DEFAULT_NPU_GRAPH_DIR


def _is_dump(action):
    if action is not None:
        return 'dump' in action
    if cfg.PRECISION_TOOL_DUMP_FLAG in os.environ and os.environ[cfg.PRECISION_TOOL_DUMP_FLAG] == 'True':
        print("[PrecisionTool] enable npu dump >======")
        return True
    return False


def _is_overflow(action):
    if action is not None:
        return 'overflow' in action
    if cfg.PRECISION_TOOL_OVERFLOW_FLAG in os.environ and os.environ[cfg.PRECISION_TOOL_OVERFLOW_FLAG] == 'True':
        print("[PrecisionTool] enable npu overflow >======")
        return True
    return False


def _is_fusion_off(action):
    if action is not None:
        return 'fusion_off' in action
    return False


def _is_fusion_switch(action):
    if action is not None:
        return 'fusion_switch' in action
    return False
