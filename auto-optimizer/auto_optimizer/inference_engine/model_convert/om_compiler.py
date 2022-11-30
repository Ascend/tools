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

import subprocess
import logging

from .compiler import Compiler

logging = logging.getLogger("auto-optimizer")


class OmCompiler(Compiler):

    @staticmethod
    def _check_required_params(cfg):
        required_params = ('type', 'framework', 'model', 'output', 'soc_version')
        params = cfg.keys()
        for param in required_params:
            if param not in params:
                raise RuntimeError("Parameter missing! '{}' is required in om convert!".format(param))

    def __init__(self, cfg):
        OmCompiler._check_required_params(cfg)
        cmd_type = cfg['type']
        self.atc_cmd = []
        if cmd_type == 'atc':
            self.atc_cmd.append('atc')
            for key, value in cfg.items():
                if key != 'type':
                    self.atc_cmd.append('--{}={}'.format(key, value))
        elif cmd_type == 'aoe':
            self.atc_cmd.append('aoe')
        else:
            raise RuntimeError("Invalid cmd type! Only support 'atc', 'aoe', but got '{}'.".format(cmd_type))

    def build_model(self):
        logging.debug(self.atc_cmd)
        subprocess.run(self.atc_cmd, shell=False)
