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
from inspect import signature
from functools import wraps


def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        # Map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            # Enforce type assertions across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError(
                            f'Argument {name} must be {bound_types[name]}'
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorate

@typeassert(path=str)
def format_to_module(path):
    """
    路径转换，把文件相对路径转换成python的import路径
    """
    format_path = ""
    if path.endswith(".py"):
        # [:-3]： 删除.py
        format_path = path.replace(os.sep, ".")[:-3]

    if format_path.startswith("."):
        format_path = format_path.replace(".", "", 1)

    return format_path

def check_file_exist(file, msg='file "{}" does not exist'):
    if not os.path.isfile(file):
        raise FileNotFoundError(msg.format(file))

