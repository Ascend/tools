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

import logging
from abc import ABC

from ..post_process_base import PostProcessBase
from ...data_process_factory import PostProcessFactory

logging = logging.getLogger("auto-optimizer")


@PostProcessFactory.register("classification")
class ClassificationPostProcess(PostProcessBase, ABC):

    def __call__(self, loop, cfg, in_queue, out_queue):
        """
        和基类的参数顺序和个数需要一致
        """
        logging.debug("post_process start")
        try:
            for i in range(loop):
                data = in_queue.get()

                out_queue.put(data)
        except Exception as err:
            logging.error("post_process failed error={}".format(err))

        logging.debug("post_process end")
