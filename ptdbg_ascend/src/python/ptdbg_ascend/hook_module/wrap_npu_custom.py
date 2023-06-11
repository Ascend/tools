#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2019-2020. Huawei Technologies Co., Ltd. All rights reserved.
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
"""

import os

import torch_npu
import yaml

from .hook_module import HOOKModule
from ..common.utils import torch_device_guard

cur_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(cur_path, "support_wrap_ops.yaml")
with open(yaml_path, 'r') as f:
    WrapNpuOps = yaml.safe_load(f).get('torch_npu')


class HOOKNpuOP(object):
    pass


class NpuOPTemplate(HOOKModule):

    def __init__(self, op_name, hook):
        self.op_name_ = op_name
        self.prefix_op_name_ = "NPU_" + str(op_name) + "_"
        super().__init__(hook)

    @torch_device_guard
    def forward(self, *args, **kwargs):
        return getattr(torch_npu._C._VariableFunctionsClass, str(self.op_name_))(*args, **kwargs)


def wrap_npu_op(op_name, hook):

    def npu_op_template(*args, **kwargs):
        return NpuOPTemplate(op_name, hook)(*args, **kwargs)

    return npu_op_template


def wrap_npu_ops_and_bind(hook):
    _npu_ops = WrapNpuOps
    for op_name in _npu_ops:
        setattr(HOOKNpuOP, "wrap_" + str(op_name), wrap_npu_op(op_name, hook))
