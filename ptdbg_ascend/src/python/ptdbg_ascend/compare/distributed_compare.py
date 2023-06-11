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
import re
from ..common.utils import print_error_log, CompareException
from .acc_compare import compare


def compare_distributed(npu_dump_dir, bench_dump_dir, output_path, **kwargs):
    def check_and_return_dir_contents(dump_dir, prefix):
        contents = os.listdir(dump_dir)
        pattern = re.compile(f'^{prefix}[0-9]+$')
        for name in contents:
            match = pattern.match(name)
            if match is None:
                msg = (f"dump_dir contains '{name}'. Expected '{prefix}'. This name is not in the format of dump output. "
                        f"Please check and delete irrelevant files in {dump_dir} and try again.")
                print_error_log(msg)
                raise CompareException(CompareException.INVALID_PATH_ERROR)
        return contents

    def extract_pkl_and_data_dir(dirname):
        pkl_path, dump_data_dir, pkl_name, dump_data_dirname = '', '', '', ''
        for fname in os.listdir(dirname):
            full_path = os.path.join(dirname, fname)
            if os.path.isdir(full_path):
                dump_data_dir = full_path
                dump_data_dirname = fname
            else:
                pkl_path = full_path
                pkl_name = fname
        # Provide robustness on invalid directory inputs
        if not pkl_path:
            print_error_log(f'No file is found in dump dir {dirname}. ')
            raise CompareException(CompareException.NO_DUMP_FILE_ERROR)
        if dump_data_dir == '':
            print_error_log(f'No directory is found in dump dir {dirname}. ')
            raise CompareException(CompareException.NO_DUMP_FILE_ERROR)
        name_body, ext = os.path.splitext(pkl_name)
        pattern = re.compile(f'{name_body}$')
        match = pattern.match(dump_data_dirname)
        if match is None:
            print_error_log('The names of pkl and directory do not match! '
                f'Please check the names and remove irrelevant files in {dirname}. ')
            raise CompareException(CompareException.INVALID_FILE_ERROR)
        return pkl_path, dump_data_dir


    # get the ranks and match by order
    npu_ranks = sorted(check_and_return_dir_contents(npu_dump_dir, 'rank'))
    bench_ranks = sorted(check_and_return_dir_contents(bench_dump_dir, 'rank'))
    if len(npu_ranks) != len(bench_ranks):
        print_error_log('The number of ranks in the two runs are different. '
            'Unable to match the ranks. Please use another folder to compare '
            'or use compare() api and manually match the ranks.')
        raise CompareException(CompareException.INVALID_PATH_ERROR)
    for nr, br in zip(npu_ranks, bench_ranks):
        n_dir = os.path.join(npu_dump_dir, nr)
        b_dir = os.path.join(bench_dump_dir, br)
        npu_pkl_path, npu_dump_data_dir = extract_pkl_and_data_dir(n_dir)
        bench_pkl_path, bench_dump_data_dir = extract_pkl_and_data_dir(b_dir)
        dump_result_param = {
            'npu_pkl_path': npu_pkl_path,
            'bench_pkl_path': bench_pkl_path,
            'npu_dump_data_dir': npu_dump_data_dir,
            'bench_dump_data_dir': bench_dump_data_dir,
            'is_print_compare_log':True
        }
        compare(dump_result_param, output_path, suffix=f'_{nr}-{br}', **kwargs)
