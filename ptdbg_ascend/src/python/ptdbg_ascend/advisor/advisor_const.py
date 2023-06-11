#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2022-2023. Huawei Technologies Co., Ltd. All rights reserved.
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


class AdvisorConst:
    """
    Class for advisor const
    """

    # text symbol
    NEW_LINE = "\n"
    COLON = ": "

    # advisor summary key
    SUSPECT_NODES = "Suspect Nodes"
    LINE = "Line"
    ADVISOR_SUGGEST = "Expert Advice"

    NO_ERROR_API = "NA"

    # advisor message
    NO_ERR_SUGGEST = "All data in comparison result meets the accuracy requirements."
    FORWARD_INPUT_SUGGEST = "1. Analyze the model to view the input source.\n" \
                            "2. Check whether an inplace API causes the output result to overwrite the input result. That is, the fault is actually caused by a computation error.\n" \
                            "3. The fault may be caused by memory corruption and further analysis is required."
    FORWARD_OUTPUT_SUGGEST = "This is a forward API computation error. Check the computation implementation."
    BACKWARD_INPUT_SUGGEST = "Check whether the forward computation result is affected."
    BACKWARD_OUTPUT_SUGGEST = "This is a backward API computation error. Check the computation implementation."

    # cannot be fixed api
    BATCH_NORM = "batch_norm"

    # name keyword
    INPUT = "input"
    OUTPUT = "output"
    FORWARD = "forward"
    BACKWARD = "backward"
