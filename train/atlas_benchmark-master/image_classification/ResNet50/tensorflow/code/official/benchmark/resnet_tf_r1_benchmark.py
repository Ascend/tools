# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Executes CTL benchmarks and accuracy tests."""
from __future__ import print_function

import os
import sys
import time
# import pydevd_pycharm
# pydevd_pycharm.settrace('90.253.17.223', port=8008, stdoutToServer=True, stderrToServer=True, suspend=False)
# pylint: disable=g-bad-import-order
from absl import flags
import tensorflow as tf

#sys.path.append(r"/home/wx933135/0708/ResNet50/tensorflow/code")

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../../../../../../utils/atlasboost'))

from official.r1.resnet import imagenet_main
from official.utils.testing.perfzero_benchmark import PerfZeroBenchmark
from official.utils.testing import benchmark_wrappers
from official.utils.flags import core as flags_core
from benchmark_log import hwlog
from benchmark_log.basic_utils import get_environment_info
from benchmark_log.basic_utils import get_model_parameter


MIN_TOP_1_ACCURACY = 0.76
MAX_TOP_1_ACCURACY = 0.77

flags.DEFINE_integer('iterations_per_loop', 1000,'iterations per loop')
flags.DEFINE_integer('save_checkpoints_steps', 115200,'save checkpoints steps')
FLAGS = flags.FLAGS
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../../../config'))


class CtlBenchmark(PerfZeroBenchmark):
  """Base benchmark class with methods to simplify testing."""

  def __init__(self, output_dir=None, default_flags=None, flag_methods=None):
    self.output_dir = output_dir
    self.default_flags = default_flags or {}
    self.flag_methods = flag_methods or {}
    super(CtlBenchmark, self).__init__(
        output_dir=self.output_dir,
        default_flags=self.default_flags,
        flag_methods=self.flag_methods)

  def _report_benchmark(self,
                        stats,
                        wall_time_sec,
                        top_1_max=None,
                        top_1_min=None,
                        total_batch_size=None,
                        log_steps=None,
                        warmup=1):
    """Report benchmark results by writing to local protobuf file.

    Args:
      stats: dict returned from keras models with known entries.
      wall_time_sec: the during of the benchmark execution in seconds
      top_1_max: highest passing level for top_1 accuracy.
      top_1_min: lowest passing level for top_1 accuracy.
      total_batch_size: Global batch-size.
      log_steps: How often the log was created for stats['step_timestamp_log'].
      warmup: number of entries in stats['step_timestamp_log'] to ignore.
    """

    metrics = []
    if 'eval_acc' in stats:
      metrics.append({
          'name': 'accuracy_top_1',
          'value': stats['eval_acc'],
          'min_value': top_1_min,
          'max_value': top_1_max
      })
      metrics.append({'name': 'eval_loss', 'value': stats['eval_loss']})

      metrics.append({
          'name': 'top_1_train_accuracy',
          'value': stats['train_acc']
      })
      metrics.append({'name': 'train_loss', 'value': stats['train_loss']})

    if (warmup and 'step_timestamp_log' in stats and
        len(stats['step_timestamp_log']) > warmup + 1):
      # first entry in the time_log is start of step 0. The rest of the
      # entries are the end of each step recorded
      time_log = stats['step_timestamp_log']
      steps_elapsed = time_log[-1].batch_index - time_log[warmup].batch_index
      time_elapsed = time_log[-1].timestamp - time_log[warmup].timestamp
      examples_per_sec = total_batch_size * (steps_elapsed / time_elapsed)
      metrics.append({'name': 'exp_per_second', 'value': examples_per_sec})

    if 'avg_exp_per_second' in stats:
      metrics.append({
          'name': 'avg_exp_per_second',
          'value': stats['avg_exp_per_second']
      })
    print("start flags_core.get_nondefault_flags_as_str")
    flags_str = flags_core.get_nondefault_flags_as_str()
    self.report_benchmark(
        iters=-1,
        wall_time=wall_time_sec,
        metrics=metrics,
        extras={'flags': flags_str})


class Resnet50CtlAccuracy(CtlBenchmark):
  """Benchmark accuracy tests for ResNet50 in CTL."""

  def __init__(self, output_dir=None, root_data_dir=None, **kwargs):
    """A benchmark class.

    Args:
      output_dir: directory where to output e.g. log files
      root_data_dir: directory under which to look for dataset
      **kwargs: arbitrary named arguments. This is needed to make the
        constructor forward compatible in case PerfZero provides more named
        arguments before updating the constructor.
    """

    # flag_methods = [common.define_keras_flags]

    self.data_dir = os.path.join(root_data_dir, 'imagenet')
    super(Resnet50CtlAccuracy, self).__init__(
        output_dir=output_dir, flag_methods=flags)


  # @benchmark_wrappers.enable_runtime_flags
  def _run_and_report_benchmark(self):
    start_time_sec = time.time()
    stats = imagenet_main.main(flags.FLAGS)
    wall_time_sec = time.time() - start_time_sec

    super(Resnet50CtlAccuracy, self)._report_benchmark(
        stats,
        wall_time_sec,
        top_1_min=MIN_TOP_1_ACCURACY,
        top_1_max=MAX_TOP_1_ACCURACY,
        total_batch_size=FLAGS.batch_size,
        log_steps=100)

  def _get_model_dir(self, folder_name):
    return os.path.join(self.output_dir, folder_name)


class Resnet50CtlBenchmarkBase(CtlBenchmark):
  """Resnet50 benchmarks."""

  def __init__(self, output_dir=None, default_flags=None):

    super(Resnet50CtlBenchmarkBase, self).__init__(
        output_dir=output_dir,
        flag_methods=flags,
        default_flags=default_flags)

  # @benchmark_wrappers.enable_runtime_flags
  def _run_and_report_benchmark(self):
    start_time_sec = time.time()
    stats = imagenet_main.benchmark_main()
    wall_time_sec = time.time() - start_time_sec

    # Number of logged step time entries that are excluded in performance
    # report. We keep results from last 100 batches in this case.
    warmup = (FLAGS.train_steps - 100) // FLAGS.log_steps

    super(Resnet50CtlBenchmarkBase, self)._report_benchmark(
        stats,
        wall_time_sec,
        total_batch_size=FLAGS.batch_size,
        log_steps=FLAGS.log_steps,
        warmup=warmup)


  def benchmark_1_npu_fp16(self, config_dict, cluster_device_id):
    """Test v1 model with 1 NPU with tf mixed precision."""
    print("start benchmark_1_npu_fp16")
    FLAGS.resnet_size = 50
    FLAGS.resnet_version = 1
    # FLAGS.max_train_steps = 1000 # this is not global step , only the step per epoch. default is according to train images
    FLAGS.max_train_steps = config_dict.get('max_train_steps')
    FLAGS.hooks = ['examplespersecondhook']
    #FLAGS.data_dir = '/home/w00563133/data/resnet/imagenet_TF'
    FLAGS.data_dir = config_dict.get('data_dir')
    FLAGS.model_dir = os.getenv('MODEL_CKPT_PATH')
    FLAGS.train_epochs = config_dict.get('train_epochs')
    FLAGS.batch_size = config_dict.get('batch_size')
    # FLAGS.epochs_between_evals = 1
    FLAGS.epochs_between_evals = config_dict.get('epochs_between_evals')
    FLAGS.iterations_per_loop = config_dict.get('iterations_per_loop')
    FLAGS.save_checkpoints_steps = config_dict.get('save_checkpoints_steps')
    FLAGS.stop_threshold = MIN_TOP_1_ACCURACY
    self._run_and_report_benchmark()


class Resnet50CtlBenchmarkReal(Resnet50CtlBenchmarkBase):
  """Resnet50 real data benchmark tests."""

  def __init__(self, output_dir=None, root_data_dir=None, **kwargs):
    def_flags = {}
    # def_flags['skip_eval'] = True
    # def_flags['data_dir'] = os.path.join(root_data_dir, 'imagenet')
    # def_flags['train_steps'] = 110
    # def_flags['steps_per_loop'] = 20
    # def_flags['log_steps'] = 10

    super(Resnet50CtlBenchmarkReal, self).__init__(
        output_dir=output_dir, default_flags=def_flags)


if __name__ == '__main__':
    hwlog.ROOT_DIR = os.path.split(os.path.abspath(__file__))[0]
    cpu_info, npu_info, framework_info, os_info, benchmark_version = get_environment_info("tensorflow")
    config_info = get_model_parameter("tensorflow_config")
    initinal_data = {"base_lr": 0.128, "dataset": "imagenet1024", "optimizer": "SGD", "loss_scale": 512}
    hwlog.remark_print(key=hwlog.CPU_INFO, value=cpu_info)
    hwlog.remark_print(key=hwlog.NPU_INFO, value=npu_info)
    hwlog.remark_print(key=hwlog.OS_INFO, value=os_info)
    hwlog.remark_print(key=hwlog.FRAMEWORK_INFO, value=framework_info)
    hwlog.remark_print(key=hwlog.BENCHMARK_VERSION, value=benchmark_version)
    hwlog.remark_print(key=hwlog.CONFIG_INFO, value=config_info)
    hwlog.remark_print(key=hwlog.BASE_LR, value=initinal_data.get("base_lr"))
    hwlog.remark_print(key=hwlog.DATASET, value=initinal_data.get("dataset"))
    hwlog.remark_print(key=hwlog.OPT_NAME, value=initinal_data.get("optimizer"))
    hwlog.remark_print(key=hwlog.LOSS_SCALE, value=initinal_data.get("loss_scale"))
    hwlog.remark_print(key=hwlog.INPUT_BATCH_SIZE, value=initinal_data.get("batchsize"))
    cluster_device_id = None
    rank_count = sys.argv[1]
    if rank_count == "1":
        from resnet_config_1p_npu import resnet50_config
    elif rank_count == "2":
        from resnet_config_2p_npu import resnet50_config
    elif rank_count == "4":
        from resnet_config_4p_npu import resnet50_config
    elif rank_count == "16":
        from resnet_config_16p_npu import resnet50_config
    elif rank_count == "32":
        from resnet_config_32p_npu import resnet50_config
    else:
        from resnet_config_8p_npu import resnet50_config
    config_dict = resnet50_config()
    print("config dict info is {}".format(config_dict))
    imagenet_main.benchmark_pre()
    test=Resnet50CtlBenchmarkReal("./result","./result")
    test.benchmark_1_npu_fp16(config_dict, cluster_device_id)

