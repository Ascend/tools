from op_test_frame.ut import OpUT, ReduceOpUT
from op_test_frame.ut import ReduceOpUT
from op_test_frame.common import precision_info
import numpy as np


def run_sample_case():
    ut_case = ReduceOpUT("ReduceSumD", None, None)

    case1 = {
        "params": [{"shape": (1, 11, 1, 15, 32), "dtype": "float16", "format": "ND", "ori_shape": (1, 11, 1, 15, 32),"ori_format": "ND", "param_type": "input","value":"/home/workspace/PycharmProjects/op-test/input/data/ReduceSumD/Ascend910A/ReduceSumD_static_shape_test_ReduceSumD_auto_case_name_1_input0.bin"},
                                              {"shape": (1, 15, 32), "dtype": "float16", "format": "ND", "ori_shape": (1, 15, 32),"ori_format": "ND", "param_type": "output"},
                                              (0,1)],
        "case_name": "test_reduce_mean_1",
        "bin_path": "/home/workspace/kernel_meta/ReduceSumD_static_shape_test_ReduceSumD_auto_case_name_1_ascend910a.o"
    }
    ut_case.add_direct_case(case1)
    ut_case.run("Ascend910A")

if __name__ == '__main__':
    run_sample_case()