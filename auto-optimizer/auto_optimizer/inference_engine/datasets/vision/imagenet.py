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
import re
import logging
from abc import ABC

from ..dataset_base import DatasetBase
from ...data_process_factory import DatasetFactory

logging = logging.getLogger("auto-optimizer")


@DatasetFactory.register("imagenet")
class ImageNetDataset(DatasetBase, ABC):
    def __call__(self, batch_size, cfg, in_queue, out_queue):
        """
        和基类的参数顺序和个数需要一致
        """
        logging.debug("dataset start")
        try:
            dataset_path, label_path = super()._get_params(cfg)

            data = []
            labels = []
            with open(label_path, 'r') as f:
                for label_file in f:
                    image_name, label = re.split(r"\s+", label_file.strip())
                    file_path = os.path.join(dataset_path, image_name)

                    labels.append(label)
                    data.append(file_path)

                    if len(data) == batch_size:
                        out_queue.put([labels, data])
                        labels.clear()
                        data.clear()

                while len(data) and len(data) < batch_size:
                    labels.append(labels[0])     # 数据补齐
                    data.append(data[0])
                    out_queue.put([labels, data])

        except Exception as err:
            logging.error("pre_process failed error={}".format(err))

        logging.debug("dataset end")

