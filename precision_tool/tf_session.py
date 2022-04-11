# coding=utf-8
import tensorflow as tf
import numpy as np
from .lib.util.util import util
from .lib.train.train_analysis import TrainAnalysis
from .lib.config import config as cfg


class PrecisionTfSession(tf.Session):
    def __init__(self, target='', graph=None, config=None):
        super().__init__(target, graph, config)
        self.log = util.get_log()
        self._create_dir()
        self.running = False

    def run(self, fetches, feed_dict=None, options=None, run_metadata=None):
        """ wrapper super.run() """
        run_before_after = False
        if not self.running:
            self.running = True
            run_before_after = True
        if run_before_after:
            self._before_run(feed_dict)
        res = super(tf.Session, self).run(fetches, feed_dict, options, run_metadata)
        if run_before_after:
            # saver will call run func.
            self._after_run()
            self.running = False
        return res

    @staticmethod
    def _create_dir():
        util.create_dir(cfg.TF_CKPT_ROOT)
        util.create_dir(cfg.TF_CKPT_INPUT_DIR)

    def _save_data(self, feed, feed_val):
        self.log.info('Save: %s', feed)
        file_name = TrainAnalysis.gen_feed_file_name(feed.name)
        np.save(file_name, feed_val)

    def _before_run(self, feed_dict):
        """
        save feed dict tensors
        :return: None
        """
        if feed_dict is not None:
            self.log.info('Session run with feed_dict, will save feed dict.')
            for feed, feed_val in feed_dict.items():
                if not isinstance(feed, tf.Tensor):
                    return
                self._save_data(feed, feed_val)
        # Iterator case

    def _after_run(self):
        """
        save checkpoint for dump and
        :return:
        """
        saver = tf.train.Saver()
        saver.save(self, cfg.TF_CKPT_FILE)
