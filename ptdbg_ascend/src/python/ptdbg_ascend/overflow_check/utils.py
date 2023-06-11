import json
import os
import stat
import torch

import numpy as np

from ..common.utils import Const
from ..dump.dump import dump_stack_info, get_scalar_data_info, dump_data
from ..dump.utils import DumpUtil, make_dump_data_dir


class OverFlowUtil(object):
    overflow_check_switch = None
    overflow_filter_switch = None
    real_overflow_dump_times = 0

    @staticmethod
    def set_overflow_check_switch(switch, filter_switch):
        OverFlowUtil.overflow_check_switch = switch
        OverFlowUtil.overflow_filter_switch = filter_switch

    @staticmethod
    def get_overflow_check_switch():
        if OverFlowUtil.overflow_check_switch is None:
            return True
        return OverFlowUtil.overflow_check_switch == "ON"

    @staticmethod
    def inc_overflow_dump_times():
        OverFlowUtil.real_overflow_dump_times += 1

    @staticmethod
    def check_overflow_dump_times(need_dump_times):
        return OverFlowUtil.real_overflow_dump_times < need_dump_times


def set_overflow_check_switch(switch, filter_switch=Const.ON):
    assert switch in ["ON", "OFF"], "Please set overflow switch with 'ON' or 'OFF'."
    assert filter_switch in ["ON", "OFF"], "Please set overflow filter_switch with 'ON' or 'OFF'."
    OverFlowUtil.set_overflow_check_switch(switch, filter_switch)


def dump_overflow(module_name, in_feat, out_feat, dump_file):
    name_template = f"{module_name}" + "_{}"
    DumpUtil.dump_data_dir = make_dump_data_dir(dump_file)
    dump_stack_info(name_template, dump_file)
    if "forward" in name_template:
        _dump_tensor_completely(in_feat, name_template.format("input"), dump_file)
        _dump_tensor_completely(out_feat, name_template.format("output"), dump_file)
    else:
        _dump_tensor_completely(in_feat, name_template.format("output"), dump_file)
        _dump_tensor_completely(out_feat, name_template.format("input"), dump_file)


def _dump_tensor_completely(x, prefix, dump_file_name):
    dump_flag = Const.DUMP_RATIO_MAX + 1
    if isinstance(x, (tuple, list)) and x:
        for i, item in enumerate(x):
            _dump_tensor_completely(item, "{}.{}".format(prefix, i), dump_file_name)
    elif isinstance(x, torch.Tensor):
        with os.fdopen(os.open(dump_file_name, os.O_RDWR | os.O_CREAT, stat.S_IWUSR | stat.S_IRUSR), "a") as f:
            if x.numel():
                output_path = os.path.join(DumpUtil.dump_data_dir, f'{prefix}.npy')
                save_tensor = x.contiguous().cpu().detach().numpy()
                np.save(output_path, save_tensor)
                json.dump([prefix, dump_flag, [], str(x.dtype), tuple(x.shape)], f)
            f.write('\n')
    elif OverFlowUtil.overflow_filter_switch == Const.OFF:
        data_info = get_scalar_data_info(x)
        dump_data(dump_file_name, dump_flag, prefix, data_info)
