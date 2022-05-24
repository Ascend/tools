# coding=utf-8
import os
import random
import tensorflow as tf
from .lib.adapter.tf_adapter import TfAdapter
from .lib.config import config as cfg


adapter = TfAdapter()


def seed_everything(seed=cfg.DUMP_SEED):
    """ set random seed
    :param seed: random seed
    :return: None
    """
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
    return adapter.sess_dump(sess)


def estimator_dump():
    """In estimator mode. estim_spec = tf.estimator.EstimatorSpec(traing_hooks=[estimator_dump()])
    :return:
    """
    return adapter.estimator_dump()


def npu_device_dump_config(npu_device, action):
    """For tf2.x
    :param npu_device: npu_device
    :param action: dump | overflow| fusion_off | fusion_switch
    :return: npu_device
    """
    return adapter.npu_device_dump_config(npu_device, action)


def estimator_dump_config(action=None):
    """return DumpConfig.
    In estimator mode. set dump_config in NPURunConfig().
    exp. config = NPURunConfig(dump_config=estimator_dum_config(), session_config=session_config)
    :return: DumpConfig
    """
    return adapter.estimator_dump_config(action)


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
    return adapter.session_dump_config(session_config, action)


def update_custom_op(custom_op, action=None):
    """Update custom_op
    :param custom_op: origin custom op
    :param action: dump | overflow | fusion_off | fusion_switch
    :return:
    """
    return adapter.update_custom_op(custom_op, action)


class NpuPrintLossScaleCallBack(tf.keras.callbacks.Callback):
    """
    For TF2.x callbacks. Usage:
        callbacks = []
        # append other callbacks.
        callbacks.append(NpuPrintLossScaleCallBack(opt))
        model.fit(xx, xx, callbacks=callbacks)
    """
    def __init__(self, optimizer, loss=None):
        super(NpuPrintLossScaleCallBack, self).__init__()
        self.optimizer = optimizer
        self.loss = loss

    def on_train_batch_begin(self, batch, logs=None):
        print("PrecisionTool: Train steps {}, loss_scale={:.3f} / not_overflow_status={}".format(
            batch, self.optimizer.loss_scale.numpy(), self.optimizer.last_step_finite.numpy()
        ), flush=True)
