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
file util module
"""
import os
import stat


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    DATA_DIR_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP


# 'pylint: disable=unused-argument,invalid-name,unused-variable
def _mkdir_without_file_exist_err(dir_path, mode):
    try:
        os.mkdir(dir_path, mode)
    except FileExistsError as err:
        pass


def makedirs(path, mode=Constant.DATA_DIR_MODES):
    """
    like sheel makedir
    :param path: dirs path
    :param mode: dir mode
    :return: None
    """

    def _rec_makedir(dir_path):
        parent_dir = os.path.dirname(dir_path)
        if parent_dir == dir_path:
            # root dir, not need make
            return
        if not os.path.exists(parent_dir):
            _rec_makedir(parent_dir)
            _mkdir_without_file_exist_err(dir_path, mode)
        else:
            _mkdir_without_file_exist_err(dir_path, mode)

    path = os.path.realpath(path)
    _rec_makedir(path)


def read_file(file_path: str, size_limit: int = 134217728) -> bytes:
    """
    read file

    Parameters
    ----------
    file_path : str
        Path to the file
    size_limit : int, option
        Raise an Exception if the file is too large

    Returns
    -------
    data_content : bytes
        The data content
    """
    if not isinstance(size_limit, int):
        raise TypeError("size_limit needs to be an integer, not %s" % str(type(size_limit)))
    file_path = os.path.realpath(file_path)
    if not os.path.exists(file_path):
        raise IOError("file_path is not exist.")
    file_size = os.stat(file_path, follow_symlinks=True).st_size
    if file_size > size_limit:
        raise IOError("File is too large! Size of % exceeds the limit: %d") % (file_path, size_limit)
    with open(file_path, "rb") as ff:
        file_content = ff.read(-1)
    return file_content
