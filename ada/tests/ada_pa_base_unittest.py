import unittest
import os
import path_tools
import errno
import json
import csv


def get_test_file(name):
    log_file = os.path.join(path_tools.get_test_path("ada_pa"), name)
    if not os.path.isfile(log_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), log_file)
    return log_file


class AdaPaBaseUt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path_tools.clear_test_path("ada_pa")
        test_path = path_tools.get_test_path("ada_pa")
        data_path = os.path.join(path_tools.get_test_root_path(), "ada_perf_data", "data")
        path_tools.copy_all_files_to(data_path, test_path)

    @classmethod
    def tearDownClass(cls):
        path_tools.clear_test_path("ada_pa")
        pass

