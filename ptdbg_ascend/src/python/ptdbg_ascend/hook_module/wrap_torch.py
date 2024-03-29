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

import torch
import yaml

from .hook_module import HOOKModule
from ..common.utils import torch_device_guard

cur_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(cur_path, "support_wrap_ops.yaml")
with open(yaml_path, 'r') as f:
    WrapTorchOps = yaml.safe_load(f).get('torch')


def get_torch_ops():
    global WrapTorchOps
    _torch_ops = dir(torch._C._VariableFunctionsClass)
    return set(WrapTorchOps) & set(_torch_ops)


class HOOKTorchOP(object):
    pass


class TorchOPTemplate(HOOKModule):

    def __init__(self, op_name, hook):
        self.op_name_ = op_name
        self.prefix_op_name_ = "Torch_" + str(op_name) + "_"
        super().__init__(hook)

    def input_param_need_adapt(self):
        special_op_list = ["broadcast_tensors"]
        for item in special_op_list:
            if item in self.op_name_:
                return True
        return False

    @torch_device_guard
    def forward(self, *args, **kwargs):
        if self.input_param_need_adapt():
            return getattr(torch._C._VariableFunctionsClass, str(self.op_name_))(args, **kwargs)
        else:
            return getattr(torch._C._VariableFunctionsClass, str(self.op_name_))(*args, **kwargs)


def wrap_torch_op(op_name, hook):

    def torch_op_template(*args, **kwargs):
        return TorchOPTemplate(op_name, hook)(*args, **kwargs)

    return torch_op_template


def wrap_torch_ops_and_bind(hook):
    _torch_ops = get_torch_ops()
    for op_name in _torch_ops:
        setattr(HOOKTorchOP, "wrap_" + op_name, wrap_torch_op(op_name, hook))
