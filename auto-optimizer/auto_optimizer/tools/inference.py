# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import argparse
import logging

from multiprocessing import Pool, Manager

from auto_optimizer.common.config import Config
from auto_optimizer.common import Register
from auto_optimizer.common.log import LogLevel, setup_logging

from auto_optimizer.inference_engine.data_process_factory import EvaluateFactory
from auto_optimizer.inference_engine.data_process_factory import PreProcessFactory
from auto_optimizer.inference_engine.data_process_factory import PostProcessFactory
from auto_optimizer.inference_engine.data_process_factory import InferenceFactory
from auto_optimizer.inference_engine.data_process_factory import DatasetFactory

logging = logging.getLogger("auto-optimizer")
setup_logging(level=LogLevel.WARNING)


class InferEngine():
    def __init__(self):
        max_queue_num = 100
        self.dataset = Manager().Queue(max_queue_num)
        self.pre_queue = Manager().Queue(max_queue_num)
        self.infer_queue = Manager().Queue(max_queue_num)
        self.post_queue = Manager().Queue(max_queue_num)

        self.dataset_pool = None
        self.pre_process_pool = None
        self.post_process_pool = None
        self.inference_pool = None
        self.evaluate_pool = None

    def inference(self, cfg):
        try:
            batch_size = cfg["batch_size"]
            engine_cfg = cfg["engine"]

            worker = engine_cfg["pre_process"]["worker"]
            dataset_path = engine_cfg["dataset"]["dataset_path"]
            file_len = len(os.listdir(dataset_path))

            # 计算inference等进程循环次数，数据考虑对齐
            if file_len % batch_size == 0:
                loop = file_len // batch_size
            else:
                loop = file_len // batch_size + 1
            logging.info("engine process loop count={}".format(loop))

            self._thread(loop, worker, batch_size, engine_cfg)
        except Exception as err:
            raise RuntimeError("inference failed error={}".format(err))

    def _thread(self, loop, worker, batch_size, engine_cfg):
        dataset, pre_process, post_process, inference, evaluate = \
            InferEngine._get_engine(engine_cfg)

        self.dataset_pool = Pool(1)
        self.pre_process_pool = Pool(worker)
        self.post_process_pool = Pool(1)
        self.inference_pool = Pool(1)
        self.evaluate_pool = Pool(1)

        self.dataset_pool.apply_async(dataset,
                                      args=(batch_size, engine_cfg["dataset"],
                                            None, self.dataset))

        for i in range(worker):
            pre_loop = (loop / worker + loop % worker) if i == 0 else loop / worker
            self.pre_process_pool.apply_async(pre_process,
                                              args=(int(pre_loop), engine_cfg["pre_process"],
                                                    self.dataset, self.pre_queue))

        # 除预处理用多进程，其他任务用单进程
        self.inference_pool.apply_async(inference,
                                        args=(loop, engine_cfg["inference"],
                                              self.pre_queue, self.infer_queue))
        self.post_process_pool.apply_async(post_process,
                                           args=(loop, engine_cfg["post_process"],
                                                 self.infer_queue, self.post_queue))
        self.evaluate_pool.apply_async(evaluate,
                                       args=(loop, batch_size, engine_cfg["evaluate"],
                                             self.post_queue, None))

        self.dataset_pool.close()
        self.pre_process_pool.close()
        self.inference_pool.close()
        self.post_process_pool.close()
        self.evaluate_pool.close()

        self.dataset_pool.join()
        self.pre_process_pool.join()
        self.inference_pool.join()
        self.post_process_pool.join()
        self.evaluate_pool.join()

    @staticmethod
    def _get_engine(engine):
        try:
            dataset = DatasetFactory.get_dataset(engine["dataset"]["type"])
            pre_process = PreProcessFactory.get_pre_process(engine["pre_process"]["type"])
            post_process = PostProcessFactory.get_post_process(engine["post_process"]["type"])
            inference = InferenceFactory.get_inference(engine["inference"]["type"])
            evaluate = EvaluateFactory.get_evaluate(engine["evaluate"]["type"])
        except Exception as err:
            raise RuntimeError("get params failed error={}".format(err))

        return dataset, pre_process, post_process, inference, evaluate


def parse_args():
    parser = argparse.ArgumentParser(description='model inference')
    parser.add_argument('config', help='inference config file path')

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    register = Register(os.path.join(os.getcwd(), "auto_optimizer"))
    register.import_modules()

    cfg = Config.read_by_file(args.config)

    infer_engine = InferEngine()
    infer_engine.inference(cfg)


if __name__ == '__main__':
    main()
