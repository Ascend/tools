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
logger
"""
import sys
import inspect
import traceback
from datetime import datetime


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    LOG_LEVEL = "INFO"


def set_logger_level(level):
    """
    set logger level
    :param level: level
    :return: None
    """

    Constant.LOG_LEVEL = level


def log(level, file_name, line, msg):
    """
    print log
    :param level: level
    :param file: file_name
    :param line: line
    :param msg: msg
    :return: None
    """

    def _get_time_str():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    print("[%s] %s [File \"%s\", line %d] %s" % (level, _get_time_str(), file_name, line, msg))


def log_warn(msg):
    """
    log warn
    :param msg: log msg
    :return: None
    """
    WARN = "WARN"
    caller = inspect.stack()[1]
    log(WARN, caller.filename, caller.lineno, msg)


def log_debug(msg):
    """
    log debug
    :param msg: log msg
    :return: None
    """
    DEBUG = "DEBUG"
    if Constant.LOG_LEVEL not in ("DEBUG",):
        return
    caller = inspect.stack()[1]
    log(DEBUG, caller.filename, caller.lineno, msg)


def log_info(msg):
    """
    log info
    :param msg: log msg
    :return: None
    """
    INFO = "INFO"
    if Constant.LOG_LEVEL not in ("DEBUG", "INFO"):
        return
    caller = inspect.stack()[1]
    log(INFO, caller.filename, caller.lineno, msg)


def log_err(msg, print_trace=False):
    """
    log err
    :param msg: log msg
    :return: None
    """
    ERROR = "ERROR"
    caller = inspect.stack()[1]
    log(ERROR, caller.filename, caller.lineno, msg)
    if print_trace:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace_info = traceback.format_exception(exc_type, exc_value, exc_traceback)
        if trace_info:
            print("".join(trace_info))
