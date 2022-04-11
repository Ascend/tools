#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright 2020 Huawei Technologies Co., Ltd
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
# ============================================================================
"""
dtype_trans module
"""

import numpy as np


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    ASCEND_DTYPE_NP_DTYPE_MAP = {
        "float16": np.float16,
        "float32": np.float32,
        "float64": np.float64,
        "bool": np.bool,
        "int8": np.int8,
        "uint8": np.uint8,
        "int16": np.int16,
        "uint16": np.uint16,
        "int32": np.int32,
        "uint32": np.uint32,
        "int64": np.int64,
        "uint64": np.uint64
    }



def get_all_str_dtypes():
    """
    get all str dtypes
    """
    return Constant.ASCEND_DTYPE_NP_DTYPE_MAP.keys()


def str_to_np_dtype(dtype: str):
    """
    str to numpy dtype
    """
    if not isinstance(dtype, str):
        return dtype

    return Constant.ASCEND_DTYPE_NP_DTYPE_MAP.get(dtype)


def np_dtype_to_str(dtype):
    """
    numpy dtype to str
    """
    NP_DTYPE_ASCEND_TYPE_MAP = {
        np.float16.__name__: "float16",
        np.float32.__name__: "float32",
        np.float64.__name__: "float64",
        np.bool.__name__: "bool",
        np.int8.__name__: "int8",
        np.uint8.__name__: "uint8",
        np.int16.__name__: "int16",
        np.uint16.__name__: "uint16",
        np.int32.__name__: "int32",
        np.uint32.__name__: "uint32",
        np.int64.__name__: "int64",
        np.uint64.__name__: "uint64"
    }
    if isinstance(dtype, str):
        return dtype
    return NP_DTYPE_ASCEND_TYPE_MAP.get(dtype.type.__name__)


def get_dtype_byte(dtype):
    """
    get dtype byte
    """
    DTYPE_SIZE_MAP = {
        "bool": 1,
        "int8": 1,
        "uint8": 1,
        "int16": 2,
        "uint16": 2,
        "int32": 4,
        "uint32": 4,
        "int64": 8,
        "uint64": 8,
        "float16": 2,
        "float32": 4,
        "float64": 8
    }
    return DTYPE_SIZE_MAP.get(dtype)
