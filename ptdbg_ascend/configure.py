#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves tf common function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2022
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess
import sys

_PYTORCH_VERSION_1_8 = "1.8"
_PYTORCH_VERSION_1_11 = "1.11"
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


def config_path(file_name):
    """config_path."""
    return os.path.join("tools", file_name)


def setup_python(env_path):
    """Get python install path."""
    default_python_bin_path = sys.executable
    ask_python_bin_path = ('Please specify the location of python with valid '
                           'pytorch 1.8/1.11 site-packages installed. [Default '
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
                'import distutils.sysconfig; import torch; print(torch.__version__ + "|" +'
                ' "|".join(torch.__path__) + "|" + distutils.sysconfig.get_python_inc())']).split("|")
            if (not compile_args[0].startswith(_PYTORCH_VERSION_1_8)) and \
                    (not compile_args[0].startswith(_PYTORCH_VERSION_1_11)):
                print('Currently supported Pytorch version is %s/%s, we got %s.'
                      % (_PYTORCH_VERSION_1_8, _PYTORCH_VERSION_1_11, compile_args[0]))
                continue
        except subprocess.CalledProcessError:
            print('Pytorch is not installed or does not work properly.')
            continue
        # Write tools/python_bin_path.sh
        with open(config_path('PYTHON_BIN_PATH'), 'w') as f:
            f.write(python_bin_path)
        with open(config_path('PYTORCH_INSTALLED_PATH'), 'w') as f:
            f.write(compile_args[1])
        break


def main():
    """main."""
    env_snapshot = dict(os.environ)
    setup_python(env_snapshot.get(_PYTHON_BIN_PATH_ENV))


if __name__ == '__main__':
    main()
