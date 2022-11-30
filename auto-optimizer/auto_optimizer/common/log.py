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

import logging
import sys

from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
from typing import Union


class LogLevel:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


def setup_logging(level: Union[int, str] = None, log_file: str = None) -> None:
    """
    Setup logger
    """
    logger = logging.getLogger("auto-optimizer")

    logger.propagate = False

    fmt = "%(asctime)s | %(levelname)-8s | %(funcName)s:<%(module)s>:%(lineno)d - %(message)s"
    formatter = Formatter(fmt=fmt)

    console_handler = StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is not None:
        file_handler = RotatingFileHandler(
            filename=log_file, maxBytes=100 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if level is not None:
        logger.setLevel(level if isinstance(level, int) else level.upper())
