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

import setuptools
from pathlib import Path
import stat
import os

VERSION = '2.3'

def generate_ptdbg_ascend_version():
      ptdbg_ascend_root = Path(__file__).parent
      version_path = ptdbg_ascend_root / "ptdbg_ascend" / "common" / "version.py"
      if version_path.exists():
            version_path.unlink()
      flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
      modes = stat.S_IWUSR | stat.S_IRUSR
      with os.fdopen(os.open(version_path, flags, modes), 'w') as f:
            f.write("__version__ = '{version}'\n".format(version = VERSION))

generate_ptdbg_ascend_version()

setuptools.setup(name='ptdbg_ascend',
      version=VERSION,
      description='This is a pytorch precision comparison tools',
      long_description='This is a pytorch precision comparison tools, include overflow detect tool',
      packages=setuptools.find_packages(),
      include_package_data=True,
      ext_modules=[],
      zip_safe=False)
