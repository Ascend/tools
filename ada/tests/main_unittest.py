import unittest
from unittest.mock import MagicMock
import ada_cmd
from ada import cip
from ada import local_machine


class TestMain(unittest.TestCase):
    def test_parse_args_default(self):
        args = ada_cmd.parse_args(['-i'])
        self.assertIsNone(args.newest)
        self.assertIsNone(args.compile)
        self.assertTrue(args.install)
        self.assertTrue(args.wait)
        self.assertIsNone(args.directory)

    def test_parse_args_dir(self):
        args = ada_cmd.parse_args(['-i', '-d', "./"])
        self.assertTrue(args.install)
        self.assertEqual(args.directory, './')

    def test_parse_args_download_and_install(self):
        args = ada_cmd.parse_args(['-i', '-n', 'atc,acllib', '-d', "./"])
        self.assertIsNone(args.compile)
        self.assertTrue(args.install)
        self.assertEqual(args.directory, './')
        self.assertEqual(args.newest, 'atc,acllib')

    def test_parse_args_download_compile_and_install(self):
        args = ada_cmd.parse_args(['-i', '-c', 'atc,acllib', '-d', "./"])
        self.assertIsNone(args.newest)
        self.assertTrue(args.install)
        self.assertEqual(args.directory, './')
        self.assertEqual(args.compile, 'atc,acllib')

    def test_download_newest(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.UBUNTU, "x86_64"))
        args = ada_cmd.parse_args(['-n', 'atc,acllib', '-d', 'tada/packages'])
        names = ada_cmd.download(args)

    def test_download_compile(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.EULEROS, "x86_64"))
        args = ada_cmd.parse_args(['-c', '20211021_213524994_I2466ff9,fwkacllib,acllib', '-d', 'tada/packages'])
        names = ada_cmd.download(args)
        self.assertEqual(set([name.split('-')[1] for name in names]), {'fwkacllib', 'acllib'})

    def test_download_compile_and_newest(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.UBUNTU, "x86_64"))
        args = ada_cmd.parse_args(['-c', '20210930_094741849_If6be636,atc,acllib', '-n', 'toolkit,opp,fwkacllib,tfplugin', '-d', 'tada/packages'])
        names = ada_cmd.download(args)
        self.assertEqual(set([name.split('-')[1] for name in names]), {'atc', 'acllib', 'toolkit', 'opp', 'fwkacllib', 'tfplugin'})

    def test_download_and_install_newest(self):
        cip.get_env = MagicMock(return_value=(cip.OsType.UBUNTU, "x86_64"))
        args = ada_cmd.parse_args(['-n', 'atc,acllib', '-d', 'tada/packages'])
        names = ada_cmd.download(args)
        ada_cmd.install("tada/packages", names)
