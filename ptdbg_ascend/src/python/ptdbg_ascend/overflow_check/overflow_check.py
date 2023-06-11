import os
import torch

from ..common.utils import print_warn_log, get_time, print_info_log
from ..dump.dump import forward_init_status, forward_acl_dump
from .utils import OverFlowUtil, dump_overflow
from ..dump.utils import DumpUtil, Const

try:
    import torch_npu
except ImportError:
    is_gpu = True
else:
    is_gpu = False

backward_init_status = False


def check_overflow_environment(pid):
    if not OverFlowUtil.get_overflow_check_switch():
        return False
    if pid != os.getpid():
        return False
    if is_gpu:
        print_warn_log("Overflow detection is not supported in the GPU environment.")
        return False
    global backward_init_status
    if backward_init_status or forward_init_status:
        return False
    return True

def check_data_overflow(x):
    if isinstance(x, (tuple, list)) and x:
        for i, item in enumerate(x):
            if True == check_data_overflow(item):
                return True
        return False
    else:
            if isinstance(x, torch.Tensor) and x.numel() != 0 and x.dtype != torch.bool:
                if len(x.shape) == 0:
                    tensor_max = x.cpu().detach().float().numpy().tolist()
                    tensor_min = tensor_max
                else:
                    tensor_max = torch._C._VariableFunctionsClass.max(x).cpu().detach().float().numpy().tolist()
                    tensor_min = torch._C._VariableFunctionsClass.min(x).cpu().detach().float().numpy().tolist()
                # inf
                if tensor_max == float('inf') or tensor_min == float('-inf'):
                    return True
                # nan
                elif tensor_max != tensor_max or tensor_min != tensor_min:
                    return True
                else:
                    return False
            elif isinstance(x, bool) or isinstance(x, int) or isinstance(x, float):
                if x == float('inf') or x == float('-inf') or x != x :
                    return True
                else:
                    return False
            else:
                return False

def overflow_check(name, **kwargs):
    if DumpUtil.dump_path:
        DumpUtil.dump_dir = os.path.dirname(DumpUtil.dump_path)
    else:
        DumpUtil.dump_dir = './'
    overflow_nums = kwargs.get('overflow_nums', 1)
    pid = kwargs.get('pid')
    dump_mode = kwargs.get('dump_mode', "api")
    DumpUtil.dump_config = kwargs.get('dump_config')
    if not pid:
        return RuntimeError("Not get the specified process pid.")

    def overflowcheck_hook(module, in_feat, out_feat):
        if not check_overflow_environment(pid):
            return
        module_name = name
        if hasattr(torch_npu._C, '_npu_is_support_inf_nan') and torch_npu._C._npu_is_support_inf_nan():
            # backward API endwith backward
            if module_name.endswith(Const.BACKWARD):
                check_feat = in_feat
            else:
                check_feat = out_feat
            module.has_overflow = check_data_overflow(check_feat)
        else:
            module.has_overflow = torch_npu._C._check_overflow_npu()
        if not module.has_overflow:
            if hasattr(module, 'input_args'):
                del module.input_args
            if hasattr(module, 'input_kwargs'):
                del module.input_kwargs
        if module.has_overflow and OverFlowUtil.check_overflow_dump_times(overflow_nums):
            OverFlowUtil.inc_overflow_dump_times()
            dump_file_name = os.path.join(DumpUtil.dump_dir,
                "Overflow_info_{}_{}.pkl".format(get_time(), OverFlowUtil.real_overflow_dump_times))
            dump_overflow(module_name, in_feat, out_feat, dump_file_name)

            print_warn_log("[overflow {} times]: module name :'{}' is overflow and dump file is saved in '{}'."
                           .format(OverFlowUtil.real_overflow_dump_times, module_name, os.path.realpath(dump_file_name)))
            if dump_mode == "acl":
                acl_dump(module, module_name)

            # clear overflow flag for the next check
            torch_npu._C._clear_overflow_npu()
            if not OverFlowUtil.check_overflow_dump_times(overflow_nums):
                raise ValueError("[overflow {} times]: dump file is saved in '{}'."
                                .format(OverFlowUtil.real_overflow_dump_times, os.path.realpath(dump_file_name)))
                return

    def acl_dump(module, module_name):
        if "forward" in module_name:
            forward_acl_dump(module, module_name)
        if "backward" in module_name:
            print_info_log("The overflow is caused by backward operator {}. "
                           "You can use reverse acl dump(mode='acl') to get operator dump data.".format(module_name))

    return overflowcheck_hook
