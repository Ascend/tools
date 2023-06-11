# coding=utf-8
import unittest
from ptdbg_ascend.dump import utils as hooks


class TestUtilsMethods(unittest.TestCase):

    def test_set_dump_switch_only_set_switch_as_on(self):
        dump_count = hooks.dump_count
        dump_util = hooks.DumpUtil
        switch_on = "ON"
        mode_all = "all"
        hooks.set_dump_switch(switch_on)
        self.assertEqual(dump_util.dump_switch, switch_on)
        self.assertEqual(dump_util.dump_switch_mode, mode_all)
        self.assertTrue(dump_util.dump_init_enable)
        self.assertEqual(dump_util.dump_switch_scope, [])
        self.assertEqual(dump_util.dump_api_list, [])
        self.assertEqual(dump_util.dump_filter_switch, switch_on)
        self.assertEqual(dump_count, 0)

    def test_set_dump_switch_mode_is_list(self):
        scope_list = ["Tensor_permute_1_forward", "Tensor_transpose_2_forward"]
        dump_util = hooks.DumpUtil
        hooks.set_dump_switch("ON", mode="list", scope=scope_list)
        self.assertEqual(dump_util.dump_switch_mode, "list")
        self.assertEqual(dump_util.dump_switch_scope, scope_list)

    def test_set_dump_switch_mode_is_range(self):
        scope_list = ["Tensor_permute_1_forward", "Tensor_transpose_3_forward"]
        dump_util = hooks.DumpUtil
        hooks.set_dump_switch("ON", mode="range", scope=scope_list)
        self.assertEqual(dump_util.dump_switch_mode, "range")
        self.assertEqual(dump_util.dump_switch_scope, scope_list)

    def test_set_dump_switch_mode_is_stack(self):
        scope_list = ["Tensor_abs_1_forward", "Tensor_transpose_3_forward"]
        dump_util = hooks.DumpUtil
        hooks.set_dump_switch("ON", mode="stack", scope=scope_list)
        self.assertEqual(dump_util.dump_switch_mode, "stack")
        self.assertEqual(dump_util.dump_switch_scope, scope_list)

    def test_set_dump_switch_mode_is_api_list(self):
        api_list = ["Transpose", "Relu", "triu"]
        lower_api_list = ["transpose", "relu", "triu"]
        dump_util = hooks.DumpUtil
        hooks.set_dump_switch("ON", mode="api_list", api_list=api_list)
        self.assertEqual(dump_util.dump_switch_mode, "api_list")
        self.assertEqual(dump_util.dump_api_list, lower_api_list)

    def test_set_dump_switch_mode_is_acl(self):
        scope_list = ["Tensor_transpose_3_backward"]
        replace_scope = ["Tensor_transpose_3_forward"]
        dump_util = hooks.DumpUtil
        hooks.set_dump_switch("ON", mode="acl", scope=scope_list)
        self.assertEqual(dump_util.dump_switch_mode, "acl")
        self.assertEqual(dump_util.dump_switch_scope, replace_scope)

    def test_set_dump_filter_switch_off(self):
        dump_util = hooks.DumpUtil
        hooks.set_dump_switch("ON", filter_switch="OFF")
        self.assertEqual(dump_util.dump_filter_switch, "OFF")
