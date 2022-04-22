import unittest
import logging
from ada import eo


class TestEo(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.handle = eo.AscendShell.create_ssh("10.138.254.157", "root", "root")

    def test_file_exists(self):
        self.assertTrue(self.handle.file_exists("/home/shengnan/packages/Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run"))
        self.assertFalse(self.handle.file_exists("/home/shengnan/packages/Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run1"))
        self.assertTrue(self.handle.file_exists("packages/Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run"))
        self.assertFalse(self.handle.file_exists("packages/Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run1"))

    def test_install(self):
        self.handle.install("/home/shengnan/packages/0929_newest/Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run")

    def test_install_multiple(self):
        self.handle.install("/home/shengnan/packages/0929_newest/Ascend-acllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run")
        self.handle.install("/home/shengnan/packages/0929_newest/Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run")
        self.handle.install("/home/shengnan/packages/0929_newest/Ascend-fwkacllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run")
        self.handle.install("/home/shengnan/packages/0929_newest/Ascend-opp-1.79.t30.0.b300-ubuntu18.04.x86_64.run")
        self.handle.install("/home/shengnan/packages/0929_newest/Ascend-toolkit-1.79.t30.0.b300-ubuntu18.04.x86_64.run")
