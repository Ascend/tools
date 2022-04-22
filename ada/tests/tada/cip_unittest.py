import logging
import unittest
from unittest.mock import MagicMock
from ada import cip


class TestCip(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('hdfs.client').setLevel(logging.WARNING)

    def test_download_compile(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.UBUNTU, "x86_64"))
        c = cip.HisiHdfs()
        c.download_compile_packages("20210930_094741849_If6be636", "./", [cip.PackageType.ATC_ONETRACK, cip.PackageType.ACLLIB_ONETRACK])

    def test_download_newest0(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.UBUNTU, "x86_64"))
        c = cip.HisiHdfs()
        ret = c.download_newest("./packages", [cip.PackageType.ACLLIB_ONETRACK, cip.PackageType.COMPILER_CANN])
        self.assertTrue(ret[0].startswith("Ascend-acllib-"))
        self.assertTrue(ret[0].find('ubuntu') > 0)
        self.assertTrue(ret[0].find('x86_64') > 0)
        self.assertTrue(ret[1].startswith("CANN-compiler-"))
        self.assertTrue(ret[1].find('ubuntu') > 0)
        self.assertTrue(ret[1].find('x86_64') > 0)

    def test_download_newest1(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.LINUX, "x86_64"))
        c = cip.HisiHdfs()
        ret = c.download_newest("./packages", [cip.PackageType.RUNTIME_CANN, cip.PackageType.COMPILER_CANN])
        self.assertTrue(ret[0].startswith("CANN-runtime-"))
        self.assertTrue(ret[0].find('linux') > 0)
        self.assertTrue(ret[0].find('x86_64') > 0)
        self.assertTrue(ret[1].startswith("CANN-compiler-"))
        self.assertTrue(ret[1].find('linux') > 0)
        self.assertTrue(ret[1].find('x86_64') > 0)
