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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import sys

_TENSORFLOW_VERSION_2_4 = "2.4"
_TENSORFLOW_VERSION_2_6 = "2.6"
_PYTHON_BIN_PATH_ENV = "ADAPTER_TARGET_PYTHON_PATH"
_ASCEND_INSTALLED_PATH_ENV = "ASCEND_INSTALLED_PATH"


def run_command(cmd):
    """run_command."""
    output = subprocess.check_output(cmd)
    return output.decode('UTF-8').strip()


def get_input(question):
    """get_input."""
    try:
        try:
            answer = raw_input(question)
        except NameError:
            answer = input(question)
    except EOFError:
        answer = ''
    return answer


def real_config_path(file):
    """real_config_path."""
    return os.path.join("tools", file)


def setup_python(env_path):
    """Get python install path."""
    default_python_bin_path = sys.executable
    ask_python_bin_path = ('Please specify the location of python with valid '
                           'tensorflow 2.4/2.6 site-packages installed. [Default '
                           'is %s]\n(You can make this quiet by set env '
                           '[ADAPTER_TARGET_PYTHON_PATH]): ') % default_python_bin_path
    custom_python_bin_path = env_path
    while True:
        if not custom_python_bin_path:
            python_bin_path = get_input(ask_python_bin_path)
        else:
            python_bin_path = custom_python_bin_path
            custom_python_bin_path = None
        if not python_bin_path:
            python_bin_path = default_python_bin_path
            pass
        # Check if the path is valid
        if os.path.isfile(python_bin_path) and os.access(python_bin_path, os.X_OK):
            pass
        elif not os.path.exists(python_bin_path):
            print('Invalid python path: %s cannot be found.' % python_bin_path)
            continue
        else:
            print('%s is not executable.  Is it the python binary?' % python_bin_path)
            continue

        try:
            compile_args = run_command([
                python_bin_path, '-c',
                'import distutils.sysconfig; import tensorflow as tf; print(tf.__version__ + "|" + tf.sysconfig.get_lib('
                ') + "|" + "|".join(tf.sysconfig.get_compile_flags()) + "|" + distutils.sysconfig.get_python_inc())'
            ]).split("|")
            if (not compile_args[0].startswith(_TENSORFLOW_VERSION_2_4)) and \
                (not compile_args[0].startswith(_TENSORFLOW_VERSION_2_6)):
                print('Invalid python path: %s compat tensorflow version is %s/%s,'
                      ' we got %s.' % (python_bin_path, _TENSORFLOW_VERSION_2_4, _TENSORFLOW_VERSION_2_6,
                                    compile_args[0]))
                continue
        except subprocess.CalledProcessError:
            print('Invalid python path: %s tensorflow not installed.' %
                  python_bin_path)
            continue
        # Write tools/python_bin_path.sh
        with open(real_config_path('PYTHON_BIN_PATH'), 'w') as f:
            f.write(python_bin_path)
        with open(real_config_path('COMPILE_FLAGS'), 'w') as f:
            for flag in compile_args[2:-1]:
                f.write("".join([flag, '\n']))
            f.write("".join(["-I", compile_args[-1], '\n']))
        with open(real_config_path('TF_INSTALLED_PATH'), 'w') as f:
            f.write(compile_args[1])
        break


def setup_ascend(env_path):
    """Get ascend install path."""
    default_ascend_path = os.path.realpath("/usr/local/Ascend")
    ask_ascend_path = ('Please specify the location of ascend. [Default is '
                       '%s]\n(You can make this quiet by set env [ASCEND_INSTALLED_PATH]): ') % default_ascend_path
    custom_ascend_path = env_path
    while True:
        if not custom_ascend_path:
            ascend_path = get_input(ask_ascend_path)
        else:
            ascend_path = custom_ascend_path
            custom_ascend_path = None
        if not ascend_path:
            ascend_path = default_ascend_path
        # Check if the path is valid
        if os.path.isdir(ascend_path) and os.access(ascend_path, os.X_OK):
            break
        elif not os.path.exists(ascend_path):
            print('Invalid ascend path: %s cannot be found.' % ascend_path)

    with open(real_config_path('ASCEND_INSTALLED_PATH'), 'w') as f:
        f.write(ascend_path)


def main():
    """main."""
    env_snapshot = dict(os.environ)
    setup_python(env_snapshot.get(_PYTHON_BIN_PATH_ENV))


if __name__ == '__main__':
    main()
