#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves generate onnx dump data function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
from msquickcmp.common.dump_data import DumpData


class OnnxDumpData(DumpData):
    def __init__(self, arguments):
        self.arguments = arguments

    def generate_dump_data(self):
        pass
