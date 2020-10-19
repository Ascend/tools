import os

import sys
import tensorflow as tf
import math
import time
from . import train_helper
from .train_helper import stage
from utils.logger import rank0log
# add by zwx5326390
from datetime import datetime
# import hwlog
from benchmark_log import hwlog

#from tensorflow.contrib.offline_train.python.npu.npu_config import NPURunConfig
#from tensorflow.contrib.offline_train.python.npu.npu_estimator import NPUEstimator
#from tensorflow.contrib.offline_train.python.npu.npu_optimizer import NPUDistributedOptimizer
from npu_bridge.estimator.npu.npu_config import NPURunConfig
from npu_bridge.estimator.npu.npu_estimator import NPUEstimator
from npu_bridge.estimator.npu.npu_optimizer import NPUDistributedOptimizer

# remark_logger = hwlog.get_logger(__file__, "hw_Resnext50.log")
# file_name = hwlog.get_file_name(__file__)

class GPUBaseTrain(object):
    def __init__(self, session, config, data, model, logger):
        self.sess = session
        self.config = config
        self.data = data
        self.model = model
        self.logger = logger
        self.print_logger = self.logger.logger
        self.all_preds = []
        self.all_targets = []

        # add by zwx5326390
        # work_num = "device " + str(os.environ.get("DEVICE_INDEX"))
        # date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        # hwlog.vlogger.info("namespace:%s,time_ts:%s,event_type:benchmark_start" % (work_num, date_time))

        if self.config['accelerator'] == 'gpu':
            self.classifier, self.training_hook = self.get_classifier()
        else:
            #from tensorflow.contrib.offline_train.python.npu.npu_config import NPURunConfig
            #from tensorflow.contrib.offline_train.python.npu.npu_estimator import NPUEstimator
            #from tensorflow.contrib.offline_train.python.npu.npu_optimizer import NPUDistributedOptimizer
            from npu_bridge.estimator.npu.npu_config import NPURunConfig
            from npu_bridge.estimator.npu.npu_estimator import NPUEstimator
            from npu_bridge.estimator.npu.npu_optimizer import NPUDistributedOptimizer
            self.classifier, self.training_hook = self.get_npu_classifier()
            
        

    def get_classifier(self):
        classifier = tf.estimator.Estimator(
            model_fn=self.model.get_estimator_model_func,
            model_dir=self.config['log_dir'],
            config = tf.estimator.RunConfig( 
                    session_config=self.sess.get_config(), 
                    save_summary_steps=self.config['save_summary_steps'] if self.config['do_checkpoint'] else None,
                    save_checkpoints_steps=self.config['save_checkpoints_steps'] if self.config['do_checkpoint'] else None,
                    keep_checkpoint_max=None
                     )
            )

        training_hooks = [train_helper.PrefillStagingAreasHook()]
        training_hooks.append(self.logger)

        return classifier, training_hooks

    def get_npu_classifier(self):
        session_config = tf.ConfigProto(
           inter_op_parallelism_threads=10,
           intra_op_parallelism_threads=10,
           allow_soft_placement=True)
        print (" config.debug:")
        print ( self.config['debug'])
        print (self.config['log_dir'])
        if self.config['debug'] :
            run_config = NPURunConfig(hcom_parallel=True, precision_mode='allow_mix_precision', enable_data_pre_proc=True, save_checkpoints_steps=112590, session_config=session_config, model_dir = self.config['model_dir'], iterations_per_loop=self.config['iterations_per_loop'], keep_checkpoint_max=5)
        else :
            run_config = NPURunConfig(hcom_parallel=True, precision_mode='allow_mix_precision', save_summary_steps=0, log_step_count_steps=None, enable_data_pre_proc=True,save_checkpoints_secs=1e9, session_config=session_config, model_dir = self.config['model_dir'], iterations_per_loop=self.config['iterations_per_loop'])
#        run_config = NPURunConfig(enable_data_pre_proc=True,save_checkpoints_secs=1e9, session_config=session_config, model_dir = self.config['model_dir'])

     #   classifier = tf.estimator.Estimator(
     #       model_fn=self.model.get_estimator_model_func,
     #       model_dir=self.config['log_dir'],
     #       config = tf.estimator.RunConfig( 
     #               session_config=self.sess.get_config(), 
     #               save_summary_steps=self.config['save_summary_steps'] if self.config['do_checkpoint'] else None,
     #               save_checkpoints_steps=self.config['save_checkpoints_steps'] if self.config['do_checkpoint'] else None,
     #               keep_checkpoint_max=None
     #                )
     #       )

        classifier =NPUEstimator(
            model_fn= self.model.get_estimator_model_func, 
            config= run_config
#            job_start_file='/tmp/config/deviceid_devindex_jobstart'
      	  )
      
        training_hooks = []
        if self.config['debug']:
            training_hooks = [train_helper.PrefillStagingAreasHook()]
            training_hooks.append(self.logger)

        return classifier, training_hooks

    def train(self):
        # add by zwx5326390
        # work_num = "device " + str(os.environ.get("DEVICE_INDEX"))
        # date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        # hwlog.vlogger.info("nemespace:%s,time_ts:%s,event_type:epoch_start, num_train_epochs: %d" % ( \
        #     work_num, date_time, self.config['num_epochs']))
        # date_time = hwlog.get_time()
        # remark_logger.info("ABK time_ts: %s, current_epoch: %d, batch_size: %d, file: %s, lineno: %s" % \
        #                    (date_time, self.config['num_epochs'], self.config['batch_size'], file_name,
        #                     sys._getframe().f_lineno))
        hwlog.remark_print(key=hwlog.CURRENT_EPOCH, value=self.config['num_epochs'])

        print ('training steps: %d' % self.config['nstep'])
        self.classifier.train( input_fn=lambda:self.data.get_train_input_fn(),
                             #  max_steps = self.config['max_train_steps'],
                               max_steps = self.config['nstep'],
                               #steps = 100,
                               hooks = self.training_hook
                              )
        # hwlog.vlogger.info("namespace:%s,time_ts:%s,event_type:epoch_stop, num_train_epochs: %d" % ( \
        #     work_num, date_time, self.config['num_epochs']))

    def evaluate(self):
        rank0log(self.print_logger, "Evaluating")
        rank0log(self.print_logger, "Validation dataset size: {}".format(self.config['num_evaluating_samples'] ))
        time.sleep(5)  # a little extra margin...
        try:
            ckpts = train_helper.sort_and_load_ckpts(self.config['ckpt_dir'])
            for i, c in enumerate(ckpts):
                if i < len(ckpts) - 1:
                    if i % self.config['eval_interval'] != 0:
                        continue
                eval_result = self.classifier.evaluate(
                    input_fn=lambda: self.data.get_eval_input_fn(),
                    checkpoint_path=c['path'])

                # add by zwx5326390
                # work_num = "device " + str(os.environ.get("DEVICE_INDEX"))
                # date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                # hwlog.vlogger.info("namespace:%s, time_ts:%s, val-top1acc:%d, val-top5acc: %d" % (
                #     work_num, date_time, eval_result.get("val-top1acc"), eval_result.get("val-top5acc")
                # ))
                # date_time = hwlog.get_time()
                # remark_logger.info("ABK time_ts: %s, accuracy: %f, accuracy_top_5: %f, file: %s, lineno: %s" % \
                #                    (date_time, float(eval_result.get("val-top1acc")),
                #                     float(eval_result.get("val-top5acc")), \
                #                     file_name, sys._getframe().f_lineno))
                hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP1, value=float(eval_result.get("val-top1acc")))
                hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP5, value=float(eval_result.get("val-top5acc")))

                #c['epoch'] = math.ceil(c['step'] / (self.config['num_training_samples']/ (self.config['batch_size'])))
                c['epoch'] = math.ceil(c['step'] / (self.config['num_training_samples']/ (self.config['batch_size'] * self.config['rank_size'])))
                c['top1'] = eval_result['val-top1acc']
                c['top5'] = eval_result['val-top5acc']
                c['loss'] = eval_result['loss']

            rank0log(self.print_logger, ' step  epoch  top1    top5     loss   checkpoint_time(UTC)')
            for i, c in enumerate(ckpts):
                if 'top1' not in c:
                    continue
                rank0log(self.print_logger,'{:5d}  {:5.1f}  {:5.3f}  {:6.2f}  {:6.2f}  {time}'
                         .format(c['step'],
                                 c['epoch'],
                                 c['top1'] * 100,
                                 c['top5'] * 100,
                                 c['loss'],
                                 time=time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.localtime(c['mtime']))))
            rank0log(self.print_logger, "Finished evaluation")
        except KeyboardInterrupt:
            self.print_logger.error("Keyboard interrupt")

    def train_and_evaluate(self):
        success = False
        epochs_between_evals = self.config.get('epochs_between_evals', 4)


        for i in range(self.config['num_epochs'] // epochs_between_evals):

            rank0log(self.print_logger, "Starting a training cycle")

            # add by zwx5326390
            # work_num = "device " + str(os.environ.get("DEVICE_INDEX"))
            # date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            # hwlog.vlogger.info("nemespace:%s,time_ts:%s,event_type:epoch_start, num_train_epochs: %d" % (\
            #     work_num, date_time, self.config['num_epochs']))
            # date_time = hwlog.get_time()
            # remark_logger.info("ABK time_ts: %s, current_epoch: %d, batch_size: %d, file: %s, lineno: %s" % \
            #                    (date_time, self.config['num_epochs'], self.config['batch_size'], file_name,
            #                     sys._getframe().f_lineno))
            hwlog.remark_print(key=hwlog.CURRENT_EPOCH, value=self.config['num_epochs'])

            self.classifier.train(input_fn=lambda:self.data.get_train_input_fn(),
                            steps = self.config['nsteps_per_epoch']*epochs_between_evals,
                            hooks = self.training_hook )
            
            # hwlog.vlogger.info("namespace:%s,time_ts:%s,event_type:epoch_stop, num_train_epochs: %d" % ( \
            #     work_num, date_time, self.config['num_epochs']))

            rank0log(self.print_logger, "Starting to evaluate")
            rank0log(self.print_logger, "Validation dataset size: {}".format(self.config['num_evaluating_samples'] ))
            time.sleep(5)  # a little extra margin...

            ckpts = train_helper.sort_and_load_ckpts(self.config['log_dir'])
            c = ckpts[-1]
            eval_result = self.classifier.evaluate(
                input_fn=lambda: self.data.get_eval_input_fn(),
                checkpoint_path=c['path'])

            # add by zwx5326390
            # work_num = "device " + str(os.environ.get("DEVICE_INDEX"))
            # date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            # hwlog.vlogger.info("namespace:%s, time_ts:%s, val-top1acc:%d, val-top5acc: %d" % (
            #     work_num, date_time, eval_result.get("val-top1acc"), eval_result.get("val-top5acc")
            # ))
            # date_time = hwlog.get_time()
            # remark_logger.info("ABK time_ts: %s, accuracy: %f, accuracy_top_5: %f, file: %s, lineno: %s" % \
            #                    (date_time, float(eval_result.get("val-top1acc")), float(eval_result.get("val-top5acc")), \
            #                     file_name, sys._getframe().f_lineno))

            hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP1, value=float(eval_result.get("val-top1acc")))
            hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP5, value=float(eval_result.get("val-top5acc")))

			
            c['epoch'] = math.ceil(c['step'] / (self.config['num_training_samples']/ (self.config['batch_size'] * self.config['rank_size'])))
            c['top1'] = eval_result['val-top1acc']
            c['top5'] = eval_result['val-top5acc']
            c['loss'] = eval_result['loss']

            rank0log(self.print_logger, ' step  epoch  top1    top5     loss   checkpoint_time(UTC)')

            rank0log(self.print_logger,'{:5d}  {:5.1f}  {:5.3f}  {:6.2f}  {:6.2f}  {time}'
                    .format(c['step'],
                            c['epoch'],
                            c['top1'] * 100,
                            c['top5'] * 100,
                            c['loss'],
                            time=time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(c['mtime']))))
            if eval_result['val-top1acc']*100 > self.config.get('stop_threshold', 74.9):
                success = True
                break



