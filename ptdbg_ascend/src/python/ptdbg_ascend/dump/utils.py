import os
import shutil
import sys
from pathlib import Path

from ..common.utils import print_error_log, CompareException, Const, get_time, print_info_log, \
    check_mode_valid, get_api_name_from_matcher

from ..common.version import __version__

dump_count = 0
range_begin_flag, range_end_flag = False, False


class DumpUtil(object):
    dump_data_dir = None
    dump_path = None
    dump_switch = None
    dump_switch_mode = Const.ALL
    dump_switch_scope = []
    dump_init_enable = False
    dump_api_list = []
    dump_filter_switch = None
    dump_mode = Const.ALL
    backward_input = {}
    dump_dir_tag = 'ptdbg_dump'

    @staticmethod
    def set_dump_path(save_path):
        DumpUtil.dump_path = save_path
        DumpUtil.dump_init_enable = True

    @staticmethod
    def set_dump_config(dump_config):
        DumpUtil.dump_config = dump_config

    @staticmethod
    def set_dump_switch(switch, mode, scope, api_list, filter_switch, dump_mode):
        DumpUtil.dump_switch = switch
        DumpUtil.dump_switch_mode = mode
        DumpUtil.dump_init_enable = True
        DumpUtil.dump_switch_scope = scope
        DumpUtil.dump_api_list = [api.lower() for api in api_list]
        DumpUtil.dump_filter_switch = filter_switch
        DumpUtil.dump_mode = dump_mode
        if mode == Const.ACL:
            DumpUtil.dump_switch_scope = [api_name.replace("backward", "forward") for api_name in scope]

    def check_list_or_acl_mode(name_prefix):
        global dump_count
        for item in DumpUtil.dump_switch_scope:
            if name_prefix.startswith(item):
                dump_count = dump_count + 1
                return True

    def check_range_mode(name_prefix):
        global range_begin_flag
        global range_end_flag
        if name_prefix.startswith(DumpUtil.dump_switch_scope[0]):
            range_begin_flag = True
            return True
        if name_prefix.startswith(DumpUtil.dump_switch_scope[1]):
            range_end_flag = True
            return True
        if range_begin_flag and not range_end_flag:
            return True
        return False

    def check_stack_mode(name_prefix):
        if len(DumpUtil.dump_switch_scope) == 0:
            return True
        elif len(DumpUtil.dump_switch_scope) == 1:
            return name_prefix.startswith(DumpUtil.dump_switch_scope[0])
        elif len(DumpUtil.dump_switch_scope) == 2:
            return DumpUtil.check_range_mode(name_prefix)
        else:
            print_error_log("dump scope is invalid, Please set the scope mode in"
                            " set_dump_switch with 'all', 'list', 'range', 'stack', 'acl', 'api_list'!")
        return False

    check_mapper = {
        Const.LIST: check_list_or_acl_mode,
        Const.ACL: check_list_or_acl_mode,
        Const.RANGE: check_range_mode,
        Const.STACK: check_stack_mode
    }

    @staticmethod
    def check_switch_scope(name_prefix):
        if DumpUtil.dump_switch_mode in DumpUtil.check_mapper:
            check_func = DumpUtil.check_mapper[DumpUtil.dump_switch_mode]
            return check_func(name_prefix)
        return False

    @staticmethod
    def get_dump_path():
        if DumpUtil.dump_path:
            return DumpUtil.dump_path

        if DumpUtil.dump_switch_mode == Const.ALL:
            raise RuntimeError("get_dump_path: the file path is empty,"
                               " you must use set_dump_path to set a valid dump path!!!")
        else:
            dir_path = os.path.realpath("./")
            dump_file_name = "scope_dump_{}_{}_{}.pkl".format(
                DumpUtil.dump_switch_mode, DumpUtil.dump_switch_scope[0], get_time())
            DumpUtil.dump_path = os.path.join(dir_path, dump_file_name)
            return DumpUtil.dump_path

    @staticmethod
    def get_dump_switch():
        return DumpUtil.dump_switch == "ON"


def set_dump_path(fpath=None, dump_tag='ptdbg_dump'):
    if fpath is None:
        raise RuntimeError("set_dump_path '{}' error, please set a valid filename".format(fpath))
        return
    real_path = os.path.realpath(fpath)
    if os.path.isdir(real_path):
        print_error_log("set_dump_path '{}' error, please set a valid filename.".format(real_path))
        raise CompareException(CompareException.INVALID_PATH_ERROR)
    DumpUtil.set_dump_path(real_path)
    DumpUtil.dump_dir_tag = dump_tag


def set_dump_switch(switch, mode=Const.ALL, scope=[], api_list=[], filter_switch=Const.ON, dump_mode=Const.ALL):
    global dump_count
    if mode == Const.LIST and switch == "ON":
        dump_count = 0
    if mode == Const.LIST and switch == "OFF":
        print_info_log("The number of matched dump is {}".format(dump_count))
    try:
        check_mode_valid(mode)
        assert switch in ["ON", "OFF"], "Please set dump switch with 'ON' or 'OFF'."
        assert filter_switch in ["ON", "OFF"], "Please set filter_switch with 'ON' or 'OFF'."
        assert dump_mode in ["all", "forward", "backward"], "Please set dump_mode with 'all' or 'forward' or 'backward'."
        if mode == Const.RANGE:
            assert len(scope) == 2, "set_dump_switch, scope param set invalid, it's must be [start, end]."
        if mode == Const.LIST:
            assert len(scope) != 0, "set_dump_switch, scope param set invalid, it's should not be an empty list."
        if mode == Const.STACK:
            assert len(scope) <= 2, "set_dump_switch, scope param set invalid, it's must be [start, end] or []."
        if mode == Const.ACL:
            assert len(scope) == 1, "set_dump_switch, scope param set invalid, only one api name is supported in acl mode."
        if mode == Const.API_LIST:
            assert isinstance(api_list, list) and len(api_list) >= 1, \
                "Current dump mode is 'api_list', but the content of api_list parameter is empty or valid."
    except (CompareException, AssertionError) as err:
        print_error_log(str(err))
        sys.exit()
    DumpUtil.set_dump_switch(switch, mode=mode, scope=scope, api_list=api_list, filter_switch=filter_switch, dump_mode=dump_mode)


def _set_dump_switch4api_list(name):
    if DumpUtil.dump_api_list:
        api_name = get_api_name_from_matcher(name)
        DumpUtil.dump_switch = "ON" if api_name in DumpUtil.dump_api_list else "OFF"


def set_backward_input(backward_input):
    for index, api_name in enumerate(DumpUtil.dump_switch_scope):
        DumpUtil.backward_input[api_name] = backward_input[index]


def make_dump_data_dir(dump_file_name):
    dump_path, file_name = os.path.split(os.path.realpath(dump_file_name))
    name_body, name_extension = os.path.splitext(file_name)
    output_dir = os.path.join(dump_path, f"{name_body}")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir, mode=0o750)
    else:
        shutil.rmtree(output_dir, ignore_errors=True)
        os.mkdir(output_dir, mode=0o750)
    return output_dir


def make_dump_dirs(rank):
    if DumpUtil.dump_path is not None:
        dump_root_dir, dump_file_name = os.path.split(DumpUtil.dump_path)
        dump_file_name_body, _ = os.path.splitext(dump_file_name)
    else:
        dump_root_dir, dump_file_name, dump_file_name_body = './', 'anonymous.pkl', 'anonymous'
    tag_dir = os.path.join(dump_root_dir, DumpUtil.dump_dir_tag + f'_v{__version__}')
    Path(tag_dir).mkdir(mode=0o750, parents=True, exist_ok=True)
    rank_dir = os.path.join(tag_dir, 'rank' + str(rank))
    if not os.path.exists(rank_dir):
        os.mkdir(rank_dir, mode=0o750)
    DumpUtil.dump_dir = rank_dir
    dump_file_path = os.path.join(rank_dir, dump_file_name)
    if os.path.exists(dump_file_path) and not os.path.isdir(dump_file_path):
        os.remove(dump_file_path)
    DumpUtil.set_dump_path(dump_file_path)
