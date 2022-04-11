import argparse
from datetime import datetime
import os
import re
import stat
import subprocess
import sys
import logging
import tempfile
from functools import reduce

SIZE_OF_DTYPE = {"DT_FLOAT": 4, "DT_FLOAT16": 2, "DT_INT8": 1, "DT_INT16": 2,
                 "DT_UINT16": 2, "DT_UINT8": 1, "DT_INT32": 4, "DT_INT64": 8,
                 "DT_UINT32": 4, "DT_UINT64": 8, "DT_BOOL": 1, "DT_DOUBLE": 8,
                 "DT_STRING, -1}, {DT_DUAL_SUB_INT8": 1, "DT_DUAL_SUB_UINT8": 1, "DT_COMPLEX64": 8,
                 "DT_COMPLEX128, 16}, {DT_QINT8": 1, "DT_QINT16": 2, "DT_QINT32": 4,
                 "DT_QUINT8": 1, "DT_QUINT16": 2, "DT_RESOURCE": -1, "DT_STRING_REF": -1,
                 "DT_DUAL": 5}


class Utils:
    @staticmethod
    def get_hexstr_value(hexstr: str) -> int:
        """
        get hex by string
        """
        return int(hexstr, 16)

    @staticmethod
    def strplogtime(str_time: str):
        temp_list = str_time.split(".")
        if len(temp_list) != 3:
            print("[WARN]str_time[{}] does not match %Y-%m-%d-%H:%M:%S.%f1.%f2, please check".format(str_time))
            return datetime.strptime(str_time, '%Y-%m-%d-%H:%M:%S')
        new_str = "{}.{}{}".format(temp_list[0], temp_list[1], temp_list[2])
        return datetime.strptime(new_str, '%Y-%m-%d-%H:%M:%S.%f')

    @staticmethod
    def execute_command(cmd: list, file_out: str = None) -> (int, str):
        """
        execute command
        :param cmd: the command to execute
        :param file_out: the stdout file
        :return: status and data
        """
        try:
            with tempfile.SpooledTemporaryFile() as out_temp:
                file_no = out_temp.fileno()
                if file_out is None:
                    process = subprocess.Popen(cmd, shell=False, stdout=file_no,
                                               stderr=file_no)
                else:
                    with os.fdopen(os.open(file_out, os.O_WRONLY | os.O_CREAT,
                                           stat.S_IWUSR | stat.S_IRUSR),
                                   'w') as output_file:
                        process = subprocess.Popen(cmd, shell=False,
                                                   stdout=output_file,
                                                   stderr=file_no)
                        os.chmod(file_out, stat.S_IRUSR)
                process.wait()
                status = process.returncode
                out_temp.seek(0)
                data = out_temp.read().decode('utf-8')
            return status, data
        except (FileNotFoundError,) as error:
            print('[ERROR]Failed to execute cmd %s. %s' % (cmd, error))
        finally:
            pass


def _get_time_and_kernel_name_execute_command() -> any:
    grep_cmd = ['grep', 'PrintErrorInfo:.*?aicore kernel execute failed',
                '-inrE', applog_path]
    status, data = Utils.execute_command(grep_cmd)
    if status != 0:
        print("[ERROR]Failed to execute command: %s." % grep_cmd)
    return data


def _get_the_latest_aicerr_form_ret(ret: list) -> int:
    max_i = -1
    max_time_obj = None
    for i, (time_str, _, _, _, _) in enumerate(ret):
        time_obj = Utils.strplogtime(time_str)
        # 都找最迟的会找到同一个，加个条件时间要早于AICERROR时间，
        # 前提host、device时间同步。否则去掉and前的条件。
        if max_time_obj is None or time_obj > max_time_obj:
            max_time_obj = time_obj
            max_i = i
    if max_i == -1:
        for i, (time_str, _, _, _, _) in enumerate(ret):
            time_obj = Utils.strplogtime(time_str)
            if max_time_obj is None or time_obj > max_time_obj:
                max_time_obj = time_obj
                max_i = i
    if max_i == -1:
        print("[ERROR]Failed to get node and kernel name.")
    return max_i


def _get_time_and_kernel_name() -> tuple:
    data = _get_time_and_kernel_name_execute_command()
    regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?device_id=(\d+)\s*,\s*stream_id=" \
             r"(\d+)\s*.+?\s*task_id=(\d+)\s*,.*?fault kernel_name=" \
             r"([-\d_]{0,}(\S+?)),\s*func_name=(\S+)__kernel\d+"
    ret = re.findall(regexp, data, re.M | re.S)
    if len(ret) == 0:
        print("[WARN]There is no ai core error time and kernel name in plog.")
        return '', ''
    print(f"ret is {ret}")
    if len(ret) > 1:
        max_i = _get_the_latest_aicerr_form_ret(ret)
        return ret[max_i][0], ret[max_i][6]
    return ret[0][0], ret[0][6]


def _get_alloc_addr() -> list:
    #  DevMalloc: Device memory alloc ok, size=512, type=2, ptr=0x108040014000
    cmd = ['grep', 'Device memory alloc ok', '-nr',
           applog_path]
    _, data = Utils.execute_command(cmd)
    regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?size\s*=\s*([" \
             r"\d]+).+?ptr\s*=\s*([\da-zA-Z]+)"
    ret = re.findall(regexp, data, re.M)
    alloc_addr = []
    for _, (_, size, addr) in enumerate(ret):
        alloc_addr.append((addr, int(size)))
    return alloc_addr


def _remove_first_found_addr(addr, addr_list):
    for i, ava_addr_item in enumerate(addr_list):
        if addr == ava_addr_item[0]:
            addr_list.pop(i)
            break
    return addr_list


def _get_available_addrs(occur_time: str) -> list:
    '''
    获取occur_time时刻可用的地址
    :param occur_time: aicore error发生的时间
    :return: 可用空间的list
    '''
    alloc_cmd = ['grep', 'Device memory alloc ok', '-nr',
                 applog_path]
    _, alloc_data = Utils.execute_command(alloc_cmd)
    alloc_regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?size\s*=\s*([" \
                   r"\d]+).+?ptr\s*=\s*([\da-zA-Z]+)"
    alloc_ret = re.findall(alloc_regexp, alloc_data, re.M)

    free_cmd = ['grep', 'Device memory free', '-nr',
                applog_path]
    _, free_data = Utils.execute_command(free_cmd)
    free_regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?mem\s*=\s*([\da-zA-Z]+)"
    free_ret = re.findall(free_regexp, free_data, re.M)
    avl_addr = []
    occur_time_obj = Utils.strplogtime(occur_time)
    for _, (alloc_time, size, addr) in enumerate(alloc_ret):
        alloc_time_obj = Utils.strplogtime(alloc_time)

        if alloc_time_obj < occur_time_obj:
            avl_addr.append((addr, int(size)))

    for _, (free_time, addr) in enumerate(free_ret):
        free_time_obj = Utils.strplogtime(free_time)
        if free_time_obj < occur_time_obj:
            avl_addr = _remove_first_found_addr(addr, avl_addr)

    return avl_addr


def _get_necessary_addrs(kernal_name: str) -> list:
    '''
    获取occur_time时刻可用的地址
    :param kernal_name: 发生aicore error的kernal_name
    :return: 需要的空间
    '''
    result = {}
    aic_info_cmd = ['grep', '-r', '-C', '7', "\[AIC_INFO\] dev_func:{}".format(kernal_name),
                    applog_path]
    _, aic_info = Utils.execute_command(aic_info_cmd)
    print("[INFO]===============================\n{}\n==================================".format(aic_info))
    aic_info_all_regexp = r"\[AIC_INFO\]\snode_name:(.*?),\snode_type:(.*?),\sstream_id:(\d+),\stask_id:(\d+)"
    aic_info_all_ret = re.findall(aic_info_all_regexp, aic_info, re.M)
    if len(aic_info_all_ret) == 0:
        print("[WARN]Failed to get [AIC_INFO]\snode_name(.*?),\snode_tye(.*?),\sstream_id:(\d+),\stask_id:(\d+)")
        return
    node_name = aic_info_all_ret[0][0]
    node_type = aic_info_all_ret[0][1]
    stream_id = aic_info_all_ret[0][2]
    task_id = aic_info_all_ret[0][3]

    aic_info_input_regexp = r"\[AIC_INFO\]\sinput:(.*?);shape:(.*?);format:(.*?);dtype:(.*?);addr:(.*?)$"
    aic_info_input_ret = re.findall(aic_info_input_regexp, aic_info, re.M)
    if len(aic_info_input_ret) == 0:
        print("[WARN]Failed to get [AIC_INFO]\sinput:(.*?);shape(.*?);format:(.*?);dtype(.*?);addr:(.*?)")
        return
    input_params = []

    for input_info in aic_info_input_ret:
        input_param = {}
        input_param["index"] = input_info[0]
        input_param["shape"] = input_info[1]
        input_param["format"] = input_info[2]
        input_param["dtype"] = input_info[3]
        input_param["addr"] = input_info[4]
        input_params.append(input_param)

    aic_info_output_regexp = r"\[AIC_INFO\]\soutput:(.*?);shape:(.*?);format:(.*?);dtype:(.*?);addr:(.*?)$"
    aic_info_output_ret = re.findall(aic_info_output_regexp, aic_info, re.M)
    if len(aic_info_output_ret) == 0:
        print("[WARN]Failed to get [AIC_INFO]\soutput:(.*?);shape(.*?);format:(.*?);dtype(.*?);addr:(.*?)")
        return
    output_params = []
    for output_info in aic_info_output_ret:
        output_param = {}
        output_param["index"] = output_info[0]
        output_param["shape"] = output_info[1]
        output_param["format"] = output_info[2]
        output_param["dtype"] = output_info[3]
        output_param["addr"] = output_info[4]
        output_params.append(output_param)

    aic_info_blockdim_regexp = r"\[AIC_INFO\]\sblock_dim:(\d+)"
    aic_info_blockdim_ret = re.findall(aic_info_blockdim_regexp, aic_info, re.M)
    aic_info_workspace_regex = r"\[AIC_INFO\]\sworkspace_bytes:(.*?)"
    aic_info_workspace_ret = re.findall(aic_info_workspace_regex, aic_info, re.M)
    if len(aic_info_workspace_ret) == 0:
        print(f"[WARN]Failed to get {aic_info_workspace_regex}")
    elif len(aic_info_workspace_ret[0]) == 0:
        print(f"[INFO]get {aic_info_workspace_regex} is null")
        workspace = "0"
    else:
        workspace = aic_info_workspace_ret[0][0]

    aic_info_dev_func_regex = r"\[AIC_INFO\]\sdev_func:(.*?)"
    aic_info_dev_func_ret = re.findall(aic_info_dev_func_regex, aic_info, re.M)
    aic_info_tvm_magic_regex = r"\[AIC_INFO\]\stvm_magic:(.*?)"
    aic_info_tvm_magic_ret = re.findall(aic_info_tvm_magic_regex, aic_info, re.M)
    aic_info_kernel_info_regex = r"\[AIC_INFO\]\skernel_info:(.*?)"
    aic_info_kernel_info_ret = re.findall(aic_info_kernel_info_regex, aic_info, re.M)
    aic_info_tiling_key_regex = r"\[AIC_INFO\]\stiling_key:(.*?)"
    aic_info_tiling_key_ret = re.findall(aic_info_tiling_key_regex, aic_info, re.M)
    aic_info_tiling_data_regex = r"\[AIC_INFO\]\stiling_data:(.*?)"
    aic_info_tiling_data_ret = re.findall(aic_info_tiling_data_regex, aic_info, re.M)
    aic_info_op_file_path_regex = r"\[AIC_INFO\]\sop_file_path:(.*?)"
    aic_info_op_file_path_ret = re.findall(aic_info_op_file_path_regex, aic_info, re.M)

    result["input_addr"] = input_params
    result["output_addr"] = output_params
    result["workspace"] = workspace
    return result


def _cal_shape_size(shape_str):
    print("[WARN]shape_str is {}".format(shape_str))
    if shape_str == "":
        return 1
    shape_str_list = shape_str.replace("[", "").replace("]", "").split(",")
    return reduce(lambda x, y: int(x) * int(y), shape_str_list)


def _check_addr_in_range(addr, ranges):
    if not isinstance(addr, int):
        addr_int = int(addr)
    else:
        addr_int = addr

    for addr_range in ranges:
        range_left = Utils.get_hexstr_value(addr_range[0])
        range_right = Utils.get_hexstr_value(addr_range[0]) + addr_range[1]
        if range_left <= addr_int < range_right:
            return True
    return False


def _check_addr(avaliable_addrs, used_addrs):
    input_params = used_addrs.get("input_addr")
    output_params = used_addrs.get("output_addr")
    workspace = used_addrs.get("workspace")
    for input_param in input_params:
        start_addr = int(input_param.get("addr"))
        shape_size = _cal_shape_size(input_param.get("shape"))
        size_of_dtype = SIZE_OF_DTYPE.get(input_param.get("dtype"))
        end_addr = int(start_addr) + shape_size * size_of_dtype
        ret = _check_addr_in_range(start_addr, avaliable_addrs)
        print(f"shape_size is {shape_size}, size_of_dtype is {size_of_dtype}")
        input_param["size"] = shape_size * size_of_dtype
        if not ret:
            print("*[ERROR]input_addr not avaliable, input_start_addr:%#x" % start_addr)
            input_param["invalid"] = True
        ret = _check_addr_in_range(end_addr, avaliable_addrs)
        if not ret:
            print("*[ERROR]input_addr not avaliable, input_end_addr:%#x" % end_addr)
            input_param["invalid"] = True

    for output_param in output_params:
        start_addr = int(output_param.get("addr"))
        shape_size = _cal_shape_size(output_param.get("shape"))
        size_of_dtype = SIZE_OF_DTYPE.get(output_param.get("dtype"))
        end_addr = int(output_param.get("addr")) + shape_size * size_of_dtype
        ret = _check_addr_in_range(start_addr, avaliable_addrs)
        output_param["size"] = shape_size * size_of_dtype
        if not ret:
            print("*[ERROR]output_addr not avaliable, output_start_addr:%#x" % start_addr)
            output_param["invalid"] = True
        ret = _check_addr_in_range(end_addr, avaliable_addrs)
        if not ret:
            print("*[ERROR]output_addr not avaliable, output_end_addr:%#x" % end_addr)
            output_param["invalid"] = True


def print_summary(ava_addr, used_addrs):
    '''
    打印结论
    ava_addr 分配的空间
    used_addrs 输入输出申请的空间
    '''
    print("\n\n\n============================================================"
          "======Summary======================================================")
    input_params = used_addrs.get("input_addr")
    output_params = used_addrs.get("output_addr")
    workspace = used_addrs.get("workspace")
    for input_param in input_params:
        index  = input_param.get("index")
        if input_param.get("invalid"):
            print(f"*[ERROR]input[{index}] is out of range")

    for output_param in output_params:
        index  = output_param.get("index")
        if output_param.get("invalid"):
            print(f"*[ERROR]output[{index}] is out of range")
    print("\n")
    for input_param in input_params:
        index = int(input_param.get("index"))
        size = int(input_param.get("size"))
        addr = int(input_param.get("addr"))
        end_addr = addr + size
        print(f"input[{index}] addr: {hex(addr)} end_addr:{hex(end_addr)} size: {hex(size)}")

    for output_param in output_params:
        index = int(output_param.get("index"))
        size = int(output_param.get("size"))
        addr = int(output_param.get("addr"))
        end_addr = addr + size
        print(f"output[{index}] addr: {hex(addr)} end_addr:{hex(end_addr)} size: {hex(size)}")

    if workspace:
        print(f"workspace_bytes:{workspace}")

    print("\navaliable addrs:\nstart_addr            end_addr              size\n")
    for alloc_addr in ava_addr:
        start_addr = int(alloc_addr[0], 16)
        size = int(alloc_addr[1])
        end_addr = start_addr + size
        print(f"{hex(start_addr)}        {hex(end_addr)}        {hex(size)}\n")

    print("\n\n\n============================================================"
          "======Summary======================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--plog_path", dest="plog_path", default="/root/ascend/log/plog",
                        help="<Required> the plog path",
                        required=True)
    if len(sys.argv) <= 1:
        parser.print_usage()
    args = parser.parse_args(sys.argv[1:])
    applog_path = args.plog_path
    try:
        # input output address
        err_time, kernel_name = _get_time_and_kernel_name()
        print(f"[INFO]err_time:{err_time}, kernel_name:{kernel_name}")
        avl_addr = _get_available_addrs(err_time)
        necessary_addr = _get_necessary_addrs(kernel_name)
        _check_addr(avl_addr, necessary_addr)
        print_summary(avl_addr, necessary_addr)
    except BaseException as e:
        logging.exception(e)
        print("Check addr error failed")
