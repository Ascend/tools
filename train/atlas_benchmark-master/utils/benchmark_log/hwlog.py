# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import logging
import json
import os
import re
import sys
import uuid
import datetime


ABK_VERSION = "1.0.0"   # ABK version
CPU_INFO = "cpu_info"
NPU_INFO = "npu_info"
OS_INFO = "os_info"
FRAMEWORK_INFO = "framework_info"
CONFIG_INFO = "config_info"
BENCHMARK_VERSION = "benchmark_version"
YAML_INFO = "yaml_info"
DATA_URL = "data_url"
LOSS_SCALE = "loss_scale"
ITERATION_TIME = "iteration_time"
TOTAL_RUNNING_TIME = "total_running_time"
LOSS = "loss"
MLM_LOSS = "mlm_loss"
NSP_LOSS = "nsp_loss"
Average_LOSS = "average_loss"
MASKED_LM_ACCURACY = "masked_lm_accuracy"
MASKED_LM_LOSS = "masked_lm_loss"
NEXT_SENTENCE_ACCURACY = "next_sentence_accuracy"
NEXT_SENTENCE_LOSS = "next_sentence_loss"
GLOBAL_BATCH_SIZE = "global_batch_size"
ACC = "acc"
F1 = "f1"
PREC = "prec"
REC = "rec"
RUN_START = "run_start"
RUN_STOP = "run_stop"
RUN_FINAL = "run_final"
INPUT_SIZE = "input_size"
INPUT_BATCH_SIZE = "input_batch_size"
OPT_NAME = "opt_name"
OPT_LR = "opt_learning_rate"
OPT_MOMENTUM = "opt_momentum"
OPT_WEIGHT_DECAY = "opt_weight_decay"
GLOBAL_STEP = "global_step"
CURRENT_STEP = "current_step"
EVAL_RESULTS = "eval_results"
TRAIN_LOOP = "train_loop"
TOTAL_TRAIN_EPOCH = "total_train_epoch"
CURRENT_EPOCH = "current_epoch"
FPS = "fps"
THROWOUT = "throwout"
TRAIN_ACCURACY = "train_accuracy"
TRAIN_ACCURACY_TOP1 = "train_accuracy_top1"
TRAIN_ACCURACY_TOP5 = "train_accuracy_top5"
TRAIN_CHECKPOINT = "train_checkpoint"
EVAL_START = "eval_start"
EVAL_SIZE = "eval_size"
EVAL_TARGET = "eval_target"
EVAL_ACCURACY = "eval_accuracy"
EVAL_ACCURACY_TOP1 = "eval_accuracy_top1"
EVAL_ACCURACY_TOP5 = "eval_accuracy_top5"
EVAL_STOP = "eval_stop"
EVAL_ITERATION_ACCURACY = "eval_iteration_accuracy"
DATASET = "dataset"
BASE_LR = "base_lr"
# Set by imagenet_main.py
STDOUT_TAG_SET = {
    ABK_VERSION,
    CPU_INFO,
    NPU_INFO,
    OS_INFO,
    FRAMEWORK_INFO,
    CONFIG_INFO,
    BENCHMARK_VERSION,
    YAML_INFO,
    DATA_URL,
    DATASET,
    TRAIN_ACCURACY,
    LOSS_SCALE,
    ITERATION_TIME,
    TOTAL_RUNNING_TIME,
    RUN_START,
    RUN_STOP,
    RUN_FINAL,
    INPUT_SIZE,
    GLOBAL_BATCH_SIZE,
    INPUT_BATCH_SIZE,
    OPT_NAME,
    OPT_LR,
    BASE_LR,
    OPT_MOMENTUM,
    OPT_WEIGHT_DECAY,
    GLOBAL_STEP,
    CURRENT_STEP,
    TRAIN_LOOP,
    TRAIN_ACCURACY_TOP1,
    TRAIN_ACCURACY_TOP5,
    TOTAL_TRAIN_EPOCH,
    CURRENT_EPOCH,
    FPS,
    THROWOUT,
    TRAIN_CHECKPOINT,
    EVAL_START,
    EVAL_SIZE,
    EVAL_TARGET,
    EVAL_ACCURACY,
    EVAL_ACCURACY_TOP1,
    EVAL_ACCURACY_TOP5,
    EVAL_STOP,
    EVAL_ITERATION_ACCURACY,
    MLM_LOSS,
    NSP_LOSS,
    Average_LOSS,
    MASKED_LM_ACCURACY,
    MASKED_LM_LOSS,
    NEXT_SENTENCE_ACCURACY,
    NEXT_SENTENCE_LOSS,
    LOSS,
    EVAL_RESULTS,
    ACC,
    F1,
    PREC,
    REC,
}


REMARK_TAGS = (
    ABK_VERSION,
    CPU_INFO,
    NPU_INFO,
    OS_INFO,
    FRAMEWORK_INFO,
    CONFIG_INFO,
    BENCHMARK_VERSION,
    YAML_INFO,
    DATA_URL,
    DATASET,
    LOSS_SCALE,
    ITERATION_TIME,
    TOTAL_RUNNING_TIME,
    RUN_START,
    RUN_STOP,
    RUN_FINAL,
    INPUT_SIZE,
    GLOBAL_BATCH_SIZE,
    INPUT_BATCH_SIZE,
    OPT_NAME,
    TRAIN_ACCURACY,
    TRAIN_ACCURACY_TOP1,
    TRAIN_ACCURACY_TOP5,
    OPT_LR,
    BASE_LR,
    OPT_MOMENTUM,
    OPT_WEIGHT_DECAY,
    GLOBAL_STEP,
    CURRENT_STEP,
    TRAIN_LOOP,
    TOTAL_TRAIN_EPOCH,
    CURRENT_EPOCH,
    FPS,
    THROWOUT,
    TRAIN_CHECKPOINT,
    EVAL_START,
    EVAL_SIZE,
    EVAL_TARGET,
    EVAL_ACCURACY,
    EVAL_ACCURACY_TOP1,
    EVAL_ACCURACY_TOP5,
    EVAL_STOP,
    EVAL_ITERATION_ACCURACY,
    MLM_LOSS,
    NSP_LOSS,
    Average_LOSS,
    MASKED_LM_ACCURACY,
    MASKED_LM_LOSS,
    NEXT_SENTENCE_ACCURACY,
    NEXT_SENTENCE_LOSS,
    LOSS,
    EVAL_RESULTS,
    ACC,
    F1,
    PREC,
    REC,
)


ABK_VERSION = "1.0.0"   # ABK version
ROOT_DIR = None
PATTERN = re.compile('[a-zA-Z0-9]+')
LOG_FILE = os.getenv("REMARK_LOG_FILE")
LOGGER = logging.getLogger('benchmark_log')
LOGGER.setLevel(logging.DEBUG)
_STREAM_HANDLER = logging.StreamHandler(stream=sys.stdout)
_STREAM_HANDLER.setLevel(logging.INFO)
LOGGER.addHandler(_STREAM_HANDLER)
BENCHMARK = (os.getenv("REMARK_LOG_FILE").split("_")[1]).split(".")[0]


if LOG_FILE:
    _FILE_HANDLER = logging.FileHandler(LOG_FILE)
    _FILE_HANDLER.setLevel(logging.DEBUG)
    LOGGER.addHandler(_FILE_HANDLER)
else:
    _STREAM_HANDLER.setLevel(logging.DEBUG)


def get_caller(stack_index=2, root_dir=None):
    ''' Returns file.py:lineno of your caller. A stack_index of 2 will provide
        the caller of the function calling this function. Notice that stack_index
        of 2 or more will fail if called from global scope. '''
    caller = inspect.getframeinfo(inspect.stack()[stack_index][0])
    # Trim the filenames for readability.
    filename = caller.filename
    filename = os.path.basename(filename)
    # if root_dir is not None:
    #  filename = re.sub("^" + root_dir + "/", "", filename)
    return "%s:%d" % (filename, caller.lineno)


TAG_SET = set(REMARK_TAGS)


def remark_print(key, value=None, benchmark=BENCHMARK, stack_offset=0,
                 tag_set=TAG_SET, deferred=False, root_dir=ROOT_DIR,
                 extra_print=False):
    ''' Prints out an benchmark Log Line.
    key: The benchmark log key such as 'EVAL_ACCURACY_TOP1' or 'FPS'.
    value: The value which contains no newlines.
    benchmark:  model type: such as resnet50
    stack_offset: Increase the value to go deeper into the stack to find the callsite. For example, if this
                  is being called by a wraper/helper you may want to set stack_offset=1 to use the callsite
                  of the wraper/helper itself.
    tag_set: The set of tags in which key must belong.
    deferred: The value is not presently known. In that case, a unique ID will
              be assigned as the value of this call and will be returned. The
              caller can then include said unique ID when the value is known
              later.
    root_dir: Directory prefix which will be trimmed when reporting calling file
              for compliance logging.
    extra_print: Print a blank line before logging to clear any text in the line.
    Example output:
      ::::ABK V1.0.0 resnet50 2020-08-12 06:22:09.670723 (hooks.py:149) fps: 681.8494655321242
    '''

    return_value = None
    if (tag_set is None and not PATTERN.match(key)) or key not in tag_set:
        raise ValueError('Invalid key for MLPerf print: ' + str(key))
    if value is not None and deferred:
        raise ValueError("deferred is set to True, but a value was provided")
    if deferred:
        return_value = str(uuid.uuid4())
        value = "DEFERRED: {}".format(return_value)
    if value is None:
        tag = key
    else:
        str_json = json.dumps(value)
        tag = "{key}: {value}".format(key=key, value=str_json)
    callsite = get_caller(2 + stack_offset, root_dir=root_dir)
    # now = time.time()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    message = ':::ABK {version} {benchmark} {secs} ({callsite}) {tag}'.format(
        version=ABK_VERSION, secs=now, benchmark=benchmark, callsite=callsite, tag=tag)
    if extra_print:
        print()  # There could be prior text on a line
    if tag in STDOUT_TAG_SET:
        LOGGER.info(message)
    else:
        LOGGER.debug(message)
    return return_value
