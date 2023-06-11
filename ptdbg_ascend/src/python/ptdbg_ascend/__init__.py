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
# ==============================================================================
"""

from .compare.acc_compare import compare, parse
from .compare.distributed_compare import compare_distributed
from .dump.dump import acc_cmp_dump
from .overflow_check.overflow_check import overflow_check
from .overflow_check.utils import set_overflow_check_switch
from .dump.utils import set_dump_path, set_dump_switch, set_backward_input
from .hook_module.register_hook import register_hook
from .common.utils import seed_all
from .common.version import __version__
seed_all()

__all__ = ["register_hook", "set_dump_path", "set_dump_switch", "set_overflow_check_switch", "seed_all",
           "acc_cmp_dump", "overflow_check", "compare", "parse", "compare_distributed", "set_backward_input"]
