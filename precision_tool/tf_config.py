# coding=utf-8
import os
from npu_bridge.npu_init import DumpConfig
from tensorflow.core.protobuf import config_pb2
from tensorflow.core.protobuf.rewriter_config_pb2 import RewriterConfig
import tensorflow as tf
from . import config as cfg


def estimator_dump_config() -> DumpConfig:
    """return DumpConfig.
    In estimator mode. set dump_config in NPURunConfig().
    exp. config = NPURunConfig(dump_config=estimator_dum_config(), session_config=session_config)
    :return: DumpConfig
    """
    _init()
    if _is_overflow():
        config = DumpConfig(enable_dump_debug=True, dump_path=cfg.DUMP_FILES_OVERFLOW, dump_step=cfg.TF_DUMP_STEP,
                            dump_mode="all")
    else:
        config = DumpConfig(enable_dump=True, dump_path=cfg.DUMP_FILES_NPU, dump_step=cfg.TF_DUMP_STEP,
                            dump_mode="all", op_debug_level=1)
    return config


def session_dump_config(session_config=None) -> config_pb2.ConfigProto:
    """
    In TF session mode. set dump_config in session_config.
    exp. config = session_dump_config()
         config.[set your own configs]
         with tf.Session(config=config) as sess:
            sess.run(_)
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
    else:
        custom_op.parameter_map['enable_dump'].b = True
        custom_op.parameter_map['dump_mode'].s = tf.compat.as_bytes("all")
        custom_op.parameter_map['dump_path'].s = tf.compat.as_bytes(cfg.DUMP_FILES_NPU)
        custom_op.parameter_map['op_debug_level'].i = 1
    custom_op.parameter_map['dump_step'].s = tf.compat.as_bytes(cfg.TF_DUMP_STEP)
    session_config.graph_options.rewrite_options.remapping = RewriterConfig.OFF
    return session_config


def _init():
    if not os.path.exists(cfg.DUMP_FILES_OVERFLOW):
        _create_dir(cfg.DUMP_FILES_OVERFLOW)
    if not os.path.exists(cfg.DUMP_FILES_NPU):
        _create_dir(cfg.DUMP_FILES_NPU)


def _create_dir(path):
    """ create dir """
    if os.path.exists(path):
        return
    try:
        os.makedirs(path, mode=0o700)
    except OSError as err:
        print("Failed to create {}. {}".format(path, str(err)))


def _is_overflow() -> bool:
    if "CHECK_OVERFLOW" in os.environ:
        return os.environ["CHECK_OVERFLOW"] == 'True'
    else:
        return False
