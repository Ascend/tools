import tensorflow as tf
import math
import time
import os
import train_helper
from logger import rank0log

import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../../../../utils'))
from benchmark_log import hwlog


class Trainer(object):
    def __init__(self, session, args, data, model, logger):
        self.sess = session
        self.args = args
        self.data = data
        self.model = model
        self.logger = logger
        self.print_logger = self.logger.logger
        self.all_preds = []
        self.all_targets = []

        self.classifier, self.training_hook = self.get_npu_classifier()

    def get_npu_classifier(self):
        from npu_bridge.estimator.npu.npu_config import NPURunConfig
        from npu_bridge.estimator.npu.npu_estimator import NPUEstimator

        run_config = NPURunConfig(
            hcom_parallel=True,
            precision_mode="allow_mix_precision",
            enable_data_pre_proc=True,
            save_checkpoints_steps=self.args.nsteps_per_epoch,
            session_config=self.sess.estimator_config,
            model_dir=self.args.log_dir,
            iterations_per_loop=self.args.iterations_per_loop,
            keep_checkpoint_max=5)

        classifier =NPUEstimator(
            model_fn= self.model.get_estimator_model_func, 
            config= run_config
      	  )
      
        training_hooks = []
        training_hooks.append(self.logger)

        return classifier, training_hooks

    def train(self):
    
        hwlog.remark_print(key=hwlog.CURRENT_EPOCH, value=self.args.max_epochs)

        print ('training steps: %d' % self.args.nstep)
        self.classifier.train( input_fn=lambda:self.data.get_train_input_fn(),
                               max_steps = self.args.nstep,
                               hooks = self.training_hook
                              )

    def evaluate(self):
        rank0log(self.print_logger, "Evaluating")
        rank0log(self.print_logger, "Validation dataset size: {}".format(self.args.num_evaluating_samples))
        time.sleep(5)  # a little extra margin...
        try:
            ckpts = train_helper.sort_and_load_ckpts(self.args.eval_dir)
            print("=========ckpt==========")
            print(ckpts)
            print("=========ckpt==========")
            for i, c in enumerate(ckpts):
                eval_result = self.classifier.evaluate(
                    input_fn=lambda: self.data.get_eval_input_fn(),
                    checkpoint_path=c['path'])
                    
                hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP1, value=float(eval_result.get("val-top1acc")))
                hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP5, value=float(eval_result.get("val-top5acc")))
    
                    
                c['epoch'] = math.ceil(c['step'] / (self.args.num_training_samples/ (self.args.batch_size)))
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
        epochs_between_evals = self.args.epochs_between_evals

        for i in range(self.args.max_epochs // epochs_between_evals):

            rank0log(self.print_logger, "Starting a training cycle")

            hwlog.remark_print(key=hwlog.CURRENT_EPOCH, value=self.args.max_epochs)

            
            self.classifier.train(input_fn=lambda:self.data.get_train_input_fn(),
                            steps = self.args.nsteps_per_epoch*epochs_between_evals,
                            hooks = self.training_hook )

            rank0log(self.print_logger, "Starting to evaluate")
            rank0log(self.print_logger, "Validation dataset size: {}".format(self.args.num_evaluating_samples))
            time.sleep(5)  # a little extra margin...

            ckpts = train_helper.sort_and_load_ckpts(self.args.log_dir)
            c = ckpts[-1]
            eval_result = self.classifier.evaluate(
                input_fn=lambda: self.data.get_eval_input_fn(),
                checkpoint_path=c['path'])

            hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP1, value=float(eval_result.get("val-top1acc")))
            hwlog.remark_print(key=hwlog.EVAL_ACCURACY_TOP5, value=float(eval_result.get("val-top5acc")))


            c['epoch'] = math.ceil(c['step'] / (self.args.num_training_samples / (self.args.batch_size * self.args.rank_size)))
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

