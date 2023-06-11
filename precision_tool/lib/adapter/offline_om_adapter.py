# coding=utf-8
import os
import time
import pathlib
import shutil
from ..util.util import util
from ..util.constant import Constant
from ..config import config as cfg
from ..util.precision_tool_exception import PrecisionToolException


class OfflineOmAdapter(object):
    """自动解析om文件至GE图"""
    def __init__(self, file_name):
        self.file_name = file_name
        self.log = util.get_log()

    @staticmethod
    def validate(file_name):
        return os.path.isfile(file_name) and str(file_name).endswith(Constant.Suffix.OM)
    
    def run(self):
        self.log("To impl")
