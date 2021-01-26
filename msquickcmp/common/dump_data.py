#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves generate dump data function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
from abc import abstractmethod


class DumpData(object):
    @abstractmethod
    def generate_dump_data(self):
        pass
