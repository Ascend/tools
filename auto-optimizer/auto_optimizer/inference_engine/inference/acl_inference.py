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

import re
import logging
from abc import ABC
import subprocess

from .inference_base import InferenceBase
from ..data_process_factory import InferenceFactory

logging = logging.getLogger("auto-optimizer")


@InferenceFactory.register("acl")
class AclInference(InferenceBase, ABC):

    def __init__(self):
        # support msame and pyacl
        self.tool = 'pyacl'

    def __call__(self, loop, cfg, in_queue, out_queue):
        logging.debug("inference start")

        if self.tool == 'msame':
            msame_cmd = [
                cfg['bin_path'],
                '--model={}'.format(cfg['model']),
                '--output={}'.format(cfg['output']),
                '--outfmt={}'.format(cfg['outfmt']),
                '--loop={}'.format(loop),
            ]
            out = subprocess.run(msame_cmd, capture_output=True, shell=False)
            log = out.stdout.decode('utf-8')
            match = re.search("Inference average time without first time: (.+) ms", log)
            if not match or out.returncode:
                raise RuntimeError("msame inference failed!\n{}".format(log))
            time = float(match.group(1))
        elif self.tool == 'pyacl':
            from pyacl.acl_infer import AclNet, init_acl, release_acl

            device_id = cfg.get('device_id', None) or 0
            try:
                init_acl(device_id)
            except Exception as err:
                logging.error("acl init failed! error message: {}".format(err))
                raise RuntimeError("acl init failed! {}".format(err))
            try:
                net = AclNet(model_path=cfg['model'], device_id=device_id)
            except Exception as err:
                logging.error("load model failed! error message: {}".format(err))
                raise RuntimeError("load model failed! {}".format(err))
            time = 0
            for i in range(loop):
                data = in_queue.get()
                if len(data) < 2:   # include file_name and data
                    logging.error("data len less than 2! data should include label and data!")
                    raise RuntimeError("input params error len={}".format(len(data)))
                try:
                    outputs, exe_time = net(data[1])    
                except Exception as err:
                    logging.error("acl infer failed! error message: {}".format(err))
                out_queue.put([data[0], outputs])
                time += exe_time
        logging.debug("inference end")
        return time
