# coding=utf-8
import os
from npu_bridge.npu_init import DumpConfig
from tensorflow.core.protobuf import config_pb2
from tensorflow.core.protobuf.rewriter_config_pb2 import RewriterConfig
from tensorflow.python import debug as tf_debug
import tensorflow as tf
from . import config as cfg

FLAG_DUMP_GE_GRAPH = 'DUMP_GE_GRAPH'
FLAG_DUMP_GRAPH_LEVEL = 'DUMP_GRAPH_LEVEL'
FLAG_DUMP_GRAPH_PATH = 'DUMP_GRAPH_PATH'


def sess_dump(sess):
    """In session run mode. Use sess=sess_dump(sess)
    :param sess:
    :return:
    """
    # sess = tf_debug.LocalCLIDebugWrapperSession(sess, ui_type="readline")
    return tf_debug.DumpingDebugWrapperSession(sess, cfg.DUMP_FILES_CPU_DEBUG)


def estimator_dump():
    """In estimator mode. estim_spec = tf.estimator.EstimatorSpec(traing_hooks=[estimator_dump()])
    :return:
    """
    return tf_debug.DumpingDebugHook(cfg.DUMP_FILES_CPU_DEBUG)


def estimator_dump_config():
    """return DumpConfig.
    In estimator mode. set dump_config in NPURunConfig().
    exp. config = NPURunConfig(dump_config=estimator_dum_config(), session_config=session_config)
    :return: DumpConfig
    """
    _init()
    if _is_overflow():
        config = DumpConfig(enable_dump_debug=True, dump_path=cfg.DUMP_FILES_OVERFLOW, dump_step=cfg.TF_DUMP_STEP,
                            dump_mode="all", op_debug_level=cfg.OP_DEBUG_LEVEL,
                            fusion_switch_file=cfg.FUSION_SWITCH_FILE)
    elif _is_dump():
        config = DumpConfig(enable_dump=True, dump_path=cfg.DUMP_FILES_NPU, dump_step=cfg.TF_DUMP_STEP,
                            dump_mode="all", op_debug_level=cfg.OP_DEBUG_LEVEL,
                            fusion_switch_file=cfg.FUSION_SWITCH_FILE)
    else:
        config = DumpConfig()
    return config


def session_dump_config(session_config=None):
    """
    In TF session mode. set dump_config in session_config.
    exp. config = session_dump_config()
         config.[set your own configs]
         with tf.Session(config=config) as sess:
            sess.run(_)
            tf_debug.LocalCLIDebugWrapperSession(sess=sess, ui_type="readline")
    :param session_config: original session config
    :return: config_pb2.ConfigProto
    """
    _init()
    if ((not isinstance(session_config, config_pb2.ConfigProto)) and
            (not issubclass(type(session_config), config_pb2.ConfigProto))):
        session_config = config_pb2.ConfigProto()
    custom_op = session_config.graph_options.rewrite_options.custom_optimizers.add()
    custom_op.name = 'NpuOptimizer'
    custom_op.parameter_map['use_off_line'].b = True
    if _is_overflow():
        custom_op.parameter_map['enable_dump_debug'].b = True
        custom_op.parameter_map['dump_debug_mode'].s = tf.compat.as_bytes("all")
        custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.DUMP_FILES_OVERFLOW)
        custom_op.parameter_map['op_debug_level'].i = cfg.OP_DEBUG_LEVEL
        custom_op.parameter_map['fusion_switch_file'].s = tf.compat.as_bytes(cfg.FUSION_SWITCH_FILE)
        custom_op.parameter_map['dump_step'].s = tf.compat.as_bytes(cfg.TF_DUMP_STEP)
    elif _is_dump():
        custom_op.parameter_map['enable_dump'].b = True
        custom_op.parameter_map['dump_mode'].s = tf.compat.as_bytes("all")
        custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.DUMP_FILES_NPU)
        custom_op.parameter_map['op_debug_level'].i = cfg.OP_DEBUG_LEVEL
        custom_op.parameter_map['fusion_switch_file'].s = tf.compat.as_bytes(cfg.FUSION_SWITCH_FILE)
        custom_op.parameter_map['dump_step'].s = tf.compat.as_bytes(cfg.TF_DUMP_STEP)
    session_config.graph_options.rewrite_options.remapping = RewriterConfig.OFF
    return session_config


def _init():
    if not os.path.exists(cfg.DUMP_FILES_OVERFLOW):
        _create_dir(cfg.DUMP_FILES_OVERFLOW)
    if not os.path.exists(cfg.DUMP_FILES_NPU):
        _create_dir(cfg.DUMP_FILES_NPU)
    _set_dump_graph_flags()


def _create_dir(path):
    """ create dir """
    if os.path.exists(path):
        return
    try:
        os.makedirs(path, mode=0o700)
    except OSError as err:
        print("Failed to create {}. {}".format(path, str(err)))


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
    os.environ[FLAG_DUMP_GRAPH_PATH] = cfg.GRAPH_DIR_ALL


def _is_dump():
    if cfg.PRECISION_TOOL_DUMP_FLAG in os.environ and os.environ[cfg.PRECISION_TOOL_DUMP_FLAG] == 'True':
        print("======< PrecisionTool enable npu dump >======")
        return True
    return False


def _is_overflow():
    if cfg.PRECISION_TOOL_OVERFLOW_FLAG in os.environ and os.environ[cfg.PRECISION_TOOL_OVERFLOW_FLAG] == 'True':
        print("======< PrecisionTool enable npu overflow >======")
        return True
    return False


def _is_fusion_switch():
    if "FUSION_SWITCH" in os.environ:
        return os.environ["FUSION_SWITCH"] == 'True'
    else:
        return False
