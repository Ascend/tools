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
import logging
from abc import ABC

import numpy as np
from tqdm import tqdm

from ..evaluate_base import EvaluateBase
from ...data_process_factory import EvaluateFactory

logging = logging.getLogger("auto-optimizer")


@EvaluateFactory.register("classification")
class ClassificationEvaluate(EvaluateBase, ABC):

    def __call__(self, loop, batch_size, cfg, in_queue, out_queue):
        """
        和基类的参数顺序和个数需要一致
        """
        logging.debug("evaluate start")
        try:
            topk = ClassificationEvaluate._get_params(cfg)

            count = 0
            count_hit = np.zeros([len(topk), loop * batch_size])
            for i in tqdm(range(loop), desc="Evaluating"):
                in_data = in_queue.get()
                if len(in_data) < 2:  # include lable and data
                    raise RuntimeError("input params error len={}".format(len(in_data)))

                labels, data = in_data[0], in_data[1]

                # 多batch下，按batch取出对应的数据，先判断文件名称和模型输出数据大小是否一致
                if len(data[0]) != len(labels):
                    raise RuntimeError("input params error len={}".format(len(data[0])))

                for index, label in enumerate(labels):
                    for idx, k in enumerate(topk):
                        hit = self._is_hit_ground_truth([data[0][index]], label, k)

                        if hit:
                            count_hit[idx][count] = 1
                    count += 1

            for idx, k in enumerate(topk):
                if count:
                    top_k_accuracy = np.count_nonzero(count_hit[idx]) / count
                    logging.info("top_{}_accuracy={}".format(k, top_k_accuracy))
        except Exception as err:
            logging.error("evaluate failed error={}".format(err))

        logging.debug("evaluate end")

    def _is_hit_ground_truth(self, data, targets, k):
        values, indices = self._get_top_k(data, k)
        for indice in indices:
            if indice == int(targets):
                return True

        return False

    def _get_top_k(self, data, k, order=True):
        indices = np.argsort(data, axis=-1)[:, -k:]
        if order:
            temp = []
            for indice in indices:
                temp.append(indice[::-1])
            indices = np.array(temp)
        values = []
        for idx, item in zip(indices, data):
            value = item.reshape(1, -1)[:, idx].reshape(-1)
            values.append(value)
        return np.array(values)[0], indices[0]

    @staticmethod
    def _get_params(cfg):
        try:
            topk = cfg["topk"]
            return topk
        except Exception as err:
            raise RuntimeError("get params failed error={}".format(err))
