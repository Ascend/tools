#!/usr/bin/env python
# coding=utf-8
"""
Function:
AicoreErrorParser class. This file mainly involves the parse function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""
import re
import os
import time
import json
import platform
import shutil
from functools import reduce
from ms_interface import utils
from ms_interface.constant import Constant
from ms_interface.aic_error_info import AicErrorInfo
from ms_interface.dump_data_parser import DumpDataParser


class OpInputOutput:
    """
    Op input and output info
    """

    def __init__(self: any) -> None:
        self.name = ""  # input[0]
        self.idx = ""  # 0
        self.is_input = True
        self.dtype = ""  # DT_FLOAT
        self.has_nan_inf = False
        self.size = 0  # in terms of bytes
        self.addr = ""
        self.actual_addr = ""
        self.overflow = False

    def get_name(self: any) -> str:
        """
        get input/output name
        """
        return self.name

    def get_dtype(self: any) -> str:
        """
        get input/output dtype
        """
        return self.dtype


class AicoreErrorParser:
    """
    The AicoreErrorParser class, parse aicore error info
    """

    def __init__(self: any, collection: any, output_path: str, collect_time: any) -> None:
        self.collection = collection
        self.output_path = output_path
        self.collect_time = collect_time

    def _get_all_error_log(self: any) -> None:
        error_log_file = os.path.join(self.output_path, "error.log")
        utils.print_info_log('Start to analyze error slog.')
        cmd = ['grep', r'\[ERROR\]', '-nr', self.collection.collect_slog_path]
        status, data = utils.execute_command(cmd)
        if status != 0:
            utils.print_error_log(
                "Failed to execute command: %s. %s" % (" ".join(cmd), " ".join(data)))
            raise utils.AicErrException(
                Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
        utils.write_file(error_log_file, data)
        utils.print_info_log('The error slog is saved in %s.' % error_log_file)

    def _get_imas_log(self: any) -> None:
        imas_log_file = os.path.join(self.output_path, "imas.log")
        cmd = ['grep', 'IMAS', '-nr', self.collection.collect_applog_path]
        utils.print_info_log('Start to analyze IMAS log.')
        status, data = utils.execute_command(cmd)
        if status == 1:
            utils.print_warn_log(
                "There is no IMAS log in %s" % self.output_path)
            return
        if status != 0:
            utils.print_error_log(
                "Failed to execute command: %s. %s" % (" ".join(cmd), " ".join(data)))
            raise utils.AicErrException(
                Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
        utils.write_file(imas_log_file, data)
        utils.print_info_log('The IMAS log is saved in %s.' % imas_log_file)

    def _get_graph_file(self: any) -> any:
        match_list = []
        for top, _, files in os.walk(self.collection.collect_compile_path):
            for name in files:
                file_name_pattern = re.compile(
                    Constant.BUILD_PROTO_FILE_PATTERN)
                pattern_match = file_name_pattern.match(name)
                if pattern_match:
                    match_list.append(
                        (pattern_match.group(1), os.path.join(top, name)))
        if len(match_list) == 0:
            utils.print_warn_log('There is no graph file in %s.'
                                 % self.collection.collect_compile_path)
            return ''
        new_match_list = sorted(match_list, key=lambda s: s[0], reverse=True)
        choose_file = new_match_list[0][1]
        utils.print_info_log('Choose %s to read op info.' % choose_file)
        return choose_file

    @staticmethod
    def _get_op_by_graph(graph_file: str, info: any) -> None:
        if graph_file == '':
            return
        try:
            with open(graph_file, 'r') as graph:
                text = graph.read()
                regexp = r'(op\s+\{\s+name:\s+"%s".+?%s.+?\})\s+' \
                         r'op\s+\{' % (info.node_name, info.kernel_name)
                ret = re.findall(regexp, text, re.M | re.S)
                if len(ret) == 0:
                    utils.print_warn_log(
                        'Failed to get op for node(%s) kernel(%s).'
                        % (info.node_name, info.kernel_name))
                    return
                info.operator = ret[0]
        except IOError as io_error:
            utils.print_error_log(
                'Failed to open file %s. %s' % (graph_file, io_error))
            raise utils.AicErrException(Constant.MS_AICERR_OPEN_FILE_ERROR)
        finally:
            pass

    def _write_summary_file(self: any, summary_info_list: list) -> None:
        summary = """本次信息收集发生于%s，共收集到%d个AICERROR，概要如下：
***************************************************************************************************
%s
***************************************************************************************************
建议选择最近发生的AICERROR，查看其中的info.txt

注意：
1、只有在device挂起后收集到的算子输入才是正确的，所以请忽略非device挂起情况下info.txt提示的“NaN/INF”
2、err.log中收集了日志目录下所有ERROR级别的日志
3、imas.log中收集了GE的IMAS日志

""" % (time.strftime("%Y-%m-%d %H:%M:%S", self.collect_time),
       len(self.collection.ai_core_error_list), "\n".join(summary_info_list))
        summary_file = os.path.join(self.output_path, "README.txt")
        utils.write_file(summary_file, summary)
        utils.print_info_log('The summary info is saved in %s' % summary_file)

        utils.print_info_log('Analysis finished, please check %s, you can '
                             'view README.txt first.' % self.output_path)

    def _get_alloc_addr(self: any) -> list:
        #  DevMalloc: Succ, size=512, type=2, ptr=0x108040014000
        cmd = ['grep', 'DevMalloc: Succ,', '-nr',
               self.collection.collect_applog_path]
        _, data = utils.execute_command(cmd)
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?size\s*=\s*([" \
                 r"\d]+).+?ptr\s*=\s*([\da-zA-Z]+)"
        ret = re.findall(regexp, data, re.M)
        alloc_addr = []
        for _, (_, size, addr) in enumerate(ret):
            alloc_addr.append((addr, int(size)))
        return alloc_addr
  

    def _remove_first_found_addr(self, addr, addr_list):
        for i, ava_addr_item in enumerate(addr_list):
            if addr == ava_addr_item[0]:
                addr_list.pop(i)
                break
        return addr_list



    def _get_available_addrs(self: any, occur_time: str) -> list:
        '''
        获取occur_time时刻可用的地址
        :param occur_time: aicore error发生的时间
        :return: 可用空间的list
        '''
        alloc_cmd = ['grep', 'DevMalloc: Succ,', '-nr',
                     self.collection.collect_applog_path]
        _, alloc_data = utils.execute_command(alloc_cmd)
        alloc_regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?size\s*=\s*([" \
                       r"\d]+).+?ptr\s*=\s*([\da-zA-Z]+)"
        alloc_ret = re.findall(alloc_regexp, alloc_data, re.M)

        free_cmd = ['grep', 'DevFree: mem', '-nr',
                    self.collection.collect_applog_path]
        _, free_data = utils.execute_command(free_cmd)
        free_regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?mem\s*=\s*([\da-zA-Z]+)"
        free_ret = re.findall(free_regexp, free_data, re.M)
        avl_addr = []
        occur_time_obj = utils.strplogtime(occur_time)
        for _, (alloc_time, size, addr) in enumerate(alloc_ret):
            alloc_time_obj = utils.strplogtime(alloc_time)

            if alloc_time_obj < occur_time_obj:
                avl_addr.append((addr, int(size)))

        for _, (free_time, addr) in enumerate(free_ret):
            free_time_obj = utils.strplogtime(free_time)
            if free_time_obj < occur_time_obj:
                avl_addr = self._remove_first_found_addr(addr, avl_addr)
        utils.print_info_log("get available addr: {}".format(avl_addr))
        return avl_addr

    def _get_necessary_addrs(self: any, kernal_name: str) -> list:
        '''
        获取occur_time时刻可用的地址
        :param kernal_name: 发生aicore error的kernal_name
        :return: 需要的空间
        '''
        result = {}
        aic_info_cmd = ['grep', '-r',  '-C', '7',  "\[AIC_INFO\] dev_func:{}".format(kernal_name),
                        self.collection.collect_applog_path]
        _, aic_info = utils.execute_command(aic_info_cmd)
        utils.print_info_log("===============================\n{}\n==================================".format(aic_info))
        aic_info_all_regexp = r"\[AIC_INFO\]\snode_name:(.*?),\snode_type:(.*?),\sstream_id:(\d+),\stask_id:(\d+)"
        aic_info_all_ret = re.findall(aic_info_all_regexp, aic_info, re.M)
        if len(aic_info_all_ret) == 0:
            utils.print_warn_log(
                "Failed to get [AIC_INFO]\snode_name(.*?),\snode_tye(.*?),\sstream_id:(\d+),\stask_id:(\d+)")
            return
        node_name = aic_info_all_ret[0][0]
        node_type = aic_info_all_ret[0][1]
        stream_id = aic_info_all_ret[0][2]
        task_id = aic_info_all_ret[0][3]

        aic_info_input_regexp = r"\[AIC_INFO\]\sinput:(.*?);shape:(.*?);format:(.*?);dtype:(.*?);addr:(.*?)$"
        aic_info_input_ret = re.findall(aic_info_input_regexp, aic_info, re.M)
        if len(aic_info_input_ret) == 0:
            utils.print_warn_log(
                "Failed to get [AIC_INFO]\sinput:(.*?);shape(.*?);format:(.*?);dtype(.*?);addr:(.*?)")
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
            utils.print_warn_log(
                "Failed to get [AIC_INFO]\soutput:(.*?);shape(.*?);format:(.*?);dtype(.*?);addr:(.*?)")
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
        if len(aic_info_blockdim_ret) == 0:
            utils.print_warn_log(f"Failed to get {aic_info_blockdim_regexp}")
        elif len(aic_info_blockdim_ret[0]) == 0:
            utils.print_info_log(f"get {aic_info_blockdim_regexp} is null")
            block_dim = ""
        else:
            block_dim = int(aic_info_blockdim_ret[0][0])
        
        aic_info_workspace_regex = r"\[AIC_INFO\]\sworkspace_bytes:(.*?)"
        aic_info_workspace_ret = re.findall(aic_info_workspace_regex, aic_info, re.M)
        if len(aic_info_workspace_ret) == 0:
            utils.print_warn_log(f"Failed to get {aic_info_workspace_regex}")
        elif len(aic_info_workspace_ret[0]) == 0:
            utils.print_info_log(f"get {aic_info_workspace_regex} is null")
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

        if len(aic_info_tiling_data_ret) == 0:
            utils.print_warn_log(f"Failed to get {aic_info_tiling_data_regex}")
        elif len(aic_info_tiling_data_ret[0]) == 0:
            utils.print_info_log(f"get {aic_info_tiling_data_regex} is null")
            tiling_data = ""
        else:
            tiling_data = bytes(aic_info_tiling_data_ret[0][0], encoding="utf-8")

        aic_info_op_file_path_regex = r"\[AIC_INFO\]\sop_file_path:(.*?)"
        aic_info_op_file_path_ret = re.findall(aic_info_op_file_path_regex, aic_info, re.M)

        result["input_addr"] = input_params
        result["output_addr"] = output_params
        result["workspace"] = workspace
        return result

    def _cal_shape_size(self, shape_str):
        utils.print_info_log("shape_str is {}".format(shape_str))
        if shape_str == "":
            return 1
        shape_str_list = shape_str.replace("[", "").replace("]", "").split(",")
        return reduce(lambda x, y: int(x)* int(y), shape_str_list)

    def _check_addr_in_range(self, addr, ranges):
        if not isinstance(addr,int):
            addr_int = int(addr)
        else:
            addr_int = addr
       
        for addr_range in ranges:
            range_left = utils.get_hexstr_value(addr_range[0])
            range_right = utils.get_hexstr_value(addr_range[0]) + addr_range[1]
            if range_left <= addr_int < range_right:
                return True
        return  False

    def _check_addr(self, avaliable_addrs, used_addrs):
        input_params = used_addrs.get("input_addr")
        output_params = used_addrs.get("output_addr")
        workspace = used_addrs.get("workspace")
        for input_param in input_params:
            start_addr = int(input_param.get("addr"))
            shape_size = self._cal_shape_size(input_param.get("shape"))
            size_of_dtype = Constant.SIZE_OF_DTYPE.get(input_param.get("dtype"))
            end_addr = int(start_addr) + int(shape_size) * int(size_of_dtype)
            ret = self._check_addr_in_range(start_addr, avaliable_addrs)
            utils.print_info_log(f"shape_size is {shape_size}, size_of_dtype is {size_of_dtype}")
            input_param["size"] = int(shape_size) * int(size_of_dtype)
            if not ret:
                utils.print_error_log("input_addr not avaliable, input_start_addr:%#x" % start_addr)
                input_param["invalid"] = True
            ret = self._check_addr_in_range(end_addr, avaliable_addrs)
            if not ret:
                utils.print_error_log("input_addr not avaliable, input_end_addr:%#x" % end_addr)
                input_param["invalid"] = True

        for output_param in output_params:
            start_addr = int(output_param.get("addr"))
            shape_size = self._cal_shape_size(output_param.get("shape"))
            size_of_dtype = Constant.SIZE_OF_DTYPE.get(output_param.get("dtype"))
            end_addr = int(output_param.get("addr")) + int(shape_size) * int(size_of_dtype)
            ret =  self._check_addr_in_range(start_addr, avaliable_addrs)
            utils.print_info_log(f"shape_size is {shape_size}, size_of_dtype is {size_of_dtype}")
            output_param["size"] = int(shape_size) * int(size_of_dtype)
            if not ret:
                utils.print_error_log("output_addr not avaliable, output_start_addr:%#x" % start_addr)
                output_param["invalid"] = True
            ret = self._check_addr_in_range(end_addr, avaliable_addrs)
            if not ret:
                utils.print_error_log("output_addr not avaliable, output_end_addr:%#x" % end_addr)
                output_param["invalid"] = True


    def _get_actual_addr(self: any) -> dict:
        # 获取真实地址
        cmd = ['grep', '[ZCPY] Copy Blobs', '-nr',
               self.collection.collect_slog_path]
        _, data = utils.execute_command(cmd)
        regexp = r'(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?Copy Blobs.+?addr:\s*([' \
                 r'\da-zA-Z]+).+?data:' \
                 r'\s*([\da-zA-Z]+)'
        ret = re.findall(regexp, data, re.M)
        actual_addr = {}
        for _, (time_str, old_addr, new_addr) in enumerate(ret):
            time_obj = utils.strplogtime(time_str)
            if old_addr in actual_addr:
                # 取最迟的
                if time_obj > actual_addr.get(old_addr)[1]:
                    actual_addr[old_addr] = [new_addr, time_obj]
            else:
                actual_addr[old_addr] = [new_addr, time_obj]
        for old_addr in actual_addr:
            actual_addr[old_addr] = actual_addr.get(old_addr)[0]
        return actual_addr

    def _get_addr_overflow_cloud(self: any) -> list:
        cmd = ['grep', 'previous alloced start_va', '-nr',
               self.collection.collect_slog_path]
        _, data = utils.execute_command(cmd)
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?va=([\da-zA-Z]+)\s+previous " \
                 r"alloced start_va=([\da-zA-Z]+), end_va=([\da-zA-Z]+),"
        ret = re.findall(regexp, data, re.M)
        for i, (time_str, value, start, end) in enumerate(ret):
            ret[i] = "%s %s is out of range [%s, %s]" % (
                time_str, value, start, end)
        return ret

    def _get_addr_overflow_mini(self: any) -> list:
        cmd = ['grep', 'devmm_page_fault_d2h_query_flag', '-nr',
               self.collection.collect_slog_path]
        _, data = utils.execute_command(cmd)
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?va=([\da-zA-Z]+)"
        ret = re.findall(regexp, data, re.M)
        for i, (time_str, value) in enumerate(ret):
            ret[i] = "%s %s is out of range" % (time_str, value)
        return ret

    def _get_addr_overflow_diff_incorrect_device(self: any) -> list:
        cmd = ['grep', 'devmm_svm_get_vaflgs_by_pid', '-nr',
               self.collection.collect_slog_path]
        _, data = utils.execute_command(cmd)
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?addr is mapped.+va=" \
                 r"([\da-zA-Z]+).devid=(\d+),bitmap=([\da-zA-Z]+)"
        ret = re.findall(regexp, data, re.M)
        for i, (time_str, value, devid, bitmap) in enumerate(ret):
            # bitmap 的  【31:26】 标明 该地址在哪个device上分配
            code = utils.get_01_from_hexstr(bitmap, 31, 26)
            allocated_dev_id = str(int(code, 2))
            ret[i] = "%s %s, allocated for device %s, is visited on wrong " \
                     "device whose id is %s" % (
                         time_str, value, allocated_dev_id, devid)
        return ret

    def _get_addr_overflow(self: any) -> list:
        ret_all = []
        # cloud
        ret = self._get_addr_overflow_cloud()
        ret_all.extend(ret)

        # mini
        ret = self._get_addr_overflow_mini()
        ret_all.extend(ret)

        # 场景：分配了addr，有物理地址，但是在不正确的device上访问
        ret = self._get_addr_overflow_diff_incorrect_device()
        ret_all.extend(ret)
        return ret_all

    @staticmethod
    def _get_max_hisi_file_path(ret: list) -> str:
        max_time = 0
        max_hisi_file_path = ""
        for _, (hisi_file_path, time1, time2) in enumerate(ret):
            time_add = int(time1 + time2)
            if time_add > max_time:
                max_time = time_add
                max_hisi_file_path = hisi_file_path
        return max_hisi_file_path

    def _get_hisi_log(self: any, info: any, err_i_folder: str) -> None:
        hisi_log_devid_path = os.path.join(
            self.collection.collect_bbox_path, Constant.DIR_BBOX,
            "device-" + info.dev_id)
        if not os.path.exists(hisi_log_devid_path):
            utils.print_warn_log(
                'There is no hisi log for device_id(%s), the path=%s.'
                % (info.dev_id, hisi_log_devid_path))
            return

        key_word = "device_id=%s, stream_id=%s, task_id=%s" % (
            info.dev_id, info.stream_id, info.task_id)
        cmd = ['grep', key_word, '-nr', self.collection.collect_bbox_path]
        _, data = utils.execute_command(cmd)
        regexp = r"(%s.+?(\d+)-(\d+).+%s)" % (
            self.collection.collect_bbox_path, 'ts.txt')
        ret = re.findall(regexp, data, re.M)
        if len(ret) == 0:
            utils.print_warn_log(
                "Failed to get hisi log for device_id(%s) stream_id(%s) "
                "task_id(%s), you may reboot and try again." % (
                    info.dev_id, info.stream_id, info.task_id))
            return

        # find the last time(max time)
        max_hisi_file_path = self._get_max_hisi_file_path(ret)
        utils.copy_file(max_hisi_file_path,
                        os.path.join(err_i_folder, "ts.log"))

    @staticmethod
    def _get_args_addr_late(op_addr: str, ret: list) -> (str, bool):
        time_obj_late = None
        args_addr_late = ""  # 取最迟的
        # funcAddr和args成对出现，根据funcAddr找args可能找到不同args，是否有不同的args addr
        multi_args_addr = False
        for _, (time_str, func_addr, args_addr) in enumerate(ret):
            if func_addr.lower() == op_addr.lower():
                if args_addr_late not in ("", args_addr):
                    multi_args_addr = True
                time_obj = utils.strplogtime(time_str)
                if time_obj_late is None or time_obj > time_obj_late:
                    time_obj_late = time_obj
                    args_addr_late = args_addr
        return args_addr_late, multi_args_addr

    def _get_op_and_args_addr(self: any, pc_start: str) -> tuple:
        # pc_start低48位有效
        code = utils.get_01_from_hexstr(pc_start, 47, 0)
        op_addr = hex(int(code, 2))
        match_pattern = "ToCommandBody: funcAddr=%s" % (str(op_addr).upper())

        cmd = ['grep', match_pattern, '-nr',
               self.collection.collect_applog_path]
        _, data = utils.execute_command(cmd)
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?funcAddr=([\da-zA-Z]+).+?args=([\da-zA-Z]+)"
        ret = re.findall(regexp, data, re.M)
        args_addr_late, multi_args_addr = self._get_args_addr_late(op_addr,
                                                                   ret)
        return op_addr, args_addr_late, multi_args_addr

    def _get_input_output_addrs_cmd_process(self: any, info: any, err_i_folder: str) -> list:
        cmd = ['grep', "memaddr", '-nr', self.collection.collect_applog_path]
        _, data = utils.execute_command(cmd)
        tmp_file = os.path.join(err_i_folder, 'tmp.txt')
        utils.write_file(tmp_file, data)
        cmd = ['grep', info.node_name, '-nr', tmp_file]
        _, data = utils.execute_command(cmd)
        utils.rm_path(tmp_file, self.output_path)
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?\[IMAS\].+(input\[\d+\]|" \
                 r"output\[\d+\]) *memaddr\[(\S+)\]"
        ret = re.findall(regexp, data, re.M)
        return ret

    def _get_input_output_addrs(self: any, info: any, err_i_folder: str,
                                alloc_addr: str, actual_addr: str) -> list:
        ret = self._get_input_output_addrs_cmd_process(info, err_i_folder)
        if len(ret) == 0:
            utils.print_warn_log('Failed to get input address and output '
                                 'address for %s.' % info.node_name)
            return []

        # get the last value
        flags = {}
        for _, (time_str, flag, addr) in enumerate(ret):
            time_obj = utils.strplogtime(time_str)
            if flag in flags and time_obj <= flags.get(flag)[0]:
                continue
            flags[flag] = [time_obj, flag, addr]
        input_output_addrs = []
        for _, (time_obj, flag, addr) in enumerate(flags.values()):
            op_io = OpInputOutput()
            op_io.name = flag  # 'input[0]'
            op_io.addr = addr
            op_io.idx = int(flag[flag.find('[') + 1:flag.find(']')])
            op_io.is_input = flag.lower().startswith("input")
            input_output_addrs.append(op_io)

            # 获取真实地址
            if addr in actual_addr:
                op_io.actual_addr = actual_addr[addr]

        # 分析图op信息
        self._analyse_op_graph(info, input_output_addrs)

        # 检查地址是否越界
        if len(alloc_addr) > 0:
            self._analyse_alloc_addr_range(alloc_addr, input_output_addrs)

        return input_output_addrs

    @staticmethod
    def _analyse_op_graph(info: any, input_output_addrs: list) -> None:
        # 分析图op信息
        if info.operator:
            regexp = r'input_desc\s+\{\s+dtype:\s+(\S+).+?\s+size:\s+(\d+)'
            input_ret = re.findall(regexp, info.operator, re.M | re.S)

            regexp = r'output_desc\s+\{\s+dtype:\s+(\S+).+?\s+size:\s+(\d+)'
            output_ret = re.findall(regexp, info.operator, re.M | re.S)

            if len(input_ret) + len(output_ret) != len(input_output_addrs):
                utils.print_warn_log(
                    'The number(%d) of input/output in logs does not match with'
                    ' that(%d) in graph.' % (len(input_output_addrs),
                                             len(input_ret) + len(output_ret)))
            for i in input_output_addrs:
                ret = input_ret if i.is_input else output_ret
                if i.idx <= len(ret) - 1:
                    rec = ret[i.idx]
                    i.dtype = rec[0]  # DT_FLOAT
                    i.size = int(rec[1])  # bytes

    @staticmethod
    def _get_alloc_addr_range(alloc_addr: any) -> list:
        alloc_addr_range = []
        for alloc in alloc_addr:
            begin_alloc = int(alloc[0], 16)
            end_alloc = begin_alloc + alloc[1] - 1 \
                if alloc[1] > 0 else begin_alloc
            alloc_addr_range.append((begin_alloc, end_alloc))
        return alloc_addr_range

    @staticmethod
    def _check_addr_in_alloc(alloc_addr_range: list, alloc_addr: int) -> bool:
        alloc_in_range = False
        for _, (begin_alloc, end_alloc) in enumerate(alloc_addr_range):
            if begin_alloc <= alloc_addr <= end_alloc:
                alloc_in_range = True
                break
        return alloc_in_range

    def _analyse_alloc_addr_range(self: any, alloc_addr: any, input_output_addrs: list) -> None:
        alloc_addr_range = self._get_alloc_addr_range(alloc_addr)
        for i in input_output_addrs:
            begin_addr = int(i.addr, 16)
            end_addr = begin_addr + i.size - 1 if i.size > 0 else begin_addr
            begin_in_range = self._check_addr_in_alloc(alloc_addr_range, begin_addr)
            if begin_in_range is False:
                i.overflow = True
                continue
            end_in_range = self._check_addr_in_alloc(alloc_addr_range, end_addr)
            if end_in_range is False:
                i.overflow = True
            # check actual addr
            self._check_actual_addr(i, alloc_addr_range)

    @staticmethod
    def _check_actual_addr(i: any, alloc_addr_range: list) -> None:
        # check actual addr
        if i.actual_addr != "":
            actual_addr = int(i.actual_addr, 16)
            actual_in_range = False
            for _, (begin_alloc, end_alloc) in enumerate(
                    alloc_addr_range):
                if begin_alloc <= actual_addr <= end_alloc:
                    actual_in_range = True
                    break
            if actual_in_range is False:
                i.overflow = True

    def _get_info_for_decompile(self: any, info: any) -> tuple:
        info.instr = ""
        # 最后一条指令
        current_pc5 = '0' + info.current_pc[-5:]
        start_pc5 = '0' + info.start_pc[-5:]
        current_pc5_value = utils.get_hexstr_value(current_pc5)
        start_pc5_value = utils.get_hexstr_value(start_pc5)
        diff_str = hex(current_pc5_value - start_pc5_value)[2:]

        # 估算err pc
        err_pc = self._get_err_pc(info, current_pc5_value, start_pc5_value)

        return diff_str, err_pc

    @staticmethod
    def _get_decompile_status(o_file: str, decompile_file: str) -> int:
        flags = "dav-m100"
        cmd = [Constant.OBJ_DUMP_FILE, '-d', '-mcpu=' + flags, '-line-numbers', o_file]
        status, _ = utils.execute_command(cmd, file_out=decompile_file)
        return status

    def _decompile(self: any, kernel_info: list, dir_path: str, info: any) -> bool:
        kernel_name = kernel_info[0]
        kernel_meta_path = kernel_info[1]
        diff_str, err_pc = self._get_info_for_decompile(info)

        # decompile .o file
        cce_file = os.path.join(kernel_meta_path, kernel_name + ".cce")
        if os.path.exists(cce_file) is False:
            utils.print_warn_log(".cce file %s not exist" % cce_file)
        else:
            utils.copy_file(cce_file, os.path.join(dir_path, kernel_name + ".cce"))

        # decompile .o file
        o_file = os.path.join(kernel_meta_path, kernel_name + ".o")
        if os.path.exists(o_file) is False:
            utils.print_warn_log(".o file %s not exist" % o_file)
            return False

        utils.copy_file(o_file, os.path.join(dir_path, kernel_name + ".o"))

        utils.copy_file(o_file, os.path.join(dir_path, kernel_name + ".json"))

        decompile_file_name = kernel_name + ".o.txt"
        decompile_file = os.path.join(dir_path, decompile_file_name)

        status = self._get_decompile_status(o_file, decompile_file)
        if status != 0:
            utils.print_error_log(
                "Failed to decompile %s, you can fix problem according to the "
                "message above, or copy %s and %s to another host and execute : "
                "%s -d -mcpu=%s %s > %s" % (o_file, Constant.OBJ_DUMP_FILE, o_file,
                                            Constant.OBJ_DUMP_FILE, "dav-m100",
                                            kernel_name + ".o",
                                            decompile_file_name))
            return False

        loc_json_file = os.path.join(kernel_meta_path,
                                     kernel_name + "_loc.json")
        self._get_cce_tbe_code_number(decompile_file, loc_json_file,
                                      err_pc, info)
        self._get_occur_before_mark(decompile_file, diff_str, info)

        return True

    @staticmethod
    def _get_err_pc(info: any, current_pc5_value: int, start_pc5_value: int) -> str:
        # 估算err pc
        extra_pc = info.find_extra_pc()  # [9:2]
        err_pc = ""
        if extra_pc != "":
            ori_pc = bin(current_pc5_value)[2:]
            if len(ori_pc) == 1:
                new_pc_bin = extra_pc + '0' + ori_pc
            elif len(ori_pc) <= 10:
                new_pc_bin = extra_pc + ori_pc[-2:]
            else:
                new_pc_bin = ori_pc[:-10] + extra_pc + ori_pc[-2:]
            new_pc_value = int(new_pc_bin, 2)
            if new_pc_value > current_pc5_value:
                new_pc_value -= 1024
            err_pc = hex(new_pc_value - start_pc5_value)[2:]
            info.instr += "\nError occured most likely at line: %s\n\n" % err_pc

        return err_pc

    @staticmethod
    def _read_decompile_file(decompile_file: str, err_pc: str, info: any) -> str:
        with open(decompile_file, 'r') as fo_file:
            cce_code = ""
            cce_code_num = ""
            for line in fo_file.readlines():
                regexp = r"cce:(\d+)"
                ret = re.findall(regexp, line, re.M)
                if len(ret) > 0:
                    cce_code = line
                    cce_code_num = ret[0]
                elif err_pc + ':' in line:
                    info.instr += "%s:%s\n" % (fo_file.name, err_pc)
                    break
            info.instr += "%s" % cce_code
        return cce_code_num

    @staticmethod
    def _read_loc_json_file(loc_json_file: str, cce_code_num: str, info: any) -> None:
        with open(loc_json_file, 'r') as load_f:
            load_dict = json.load(load_f)
            for line in load_dict[0]['cce_line2loc']:
                if str(line['cce_line']) == cce_code_num \
                        and line['loc'][0] != "":
                    info.instr += "%s:%s\n" % (line['loc'][0], line['loc'][1])

    def _get_cce_tbe_code_number(self: any, decompile_file: str, loc_json_file: str,
                                 err_pc: str, info: any) -> bool:
        # txt code to cce number
        if os.path.exists(decompile_file) is False:
            utils.print_error_log("The decompile file does not exist.")
            return False

        if err_pc != "":
            cce_code_num = self._read_decompile_file(decompile_file,
                                                     err_pc, info)
            # cce to tbe code number
            if os.path.exists(loc_json_file) is False:
                utils.print_warn_log("file %s not exist" % loc_json_file)
                return False
            self._read_loc_json_file(loc_json_file, cce_code_num, info)
        return True

    @staticmethod
    def _get_occur_before_mark(decompile_file: str, diff_str: str, info: any) -> bool:
        #      504:    04c20000    ST.b64         X1, [X0], #0
        with open(decompile_file, "r") as fo_file:
            text = fo_file.read()

        regexp = r'(^\s+(\S+):\s+\S+\s+\S.+$)'
        ret = re.findall(regexp, text, re.M)
        find_i = -1
        for i, (_, line_diff) in enumerate(ret):
            if line_diff == diff_str:
                find_i = i
                break

        if find_i == -1:
            utils.print_warn_log(
                "Get fault instruction failed, file(%s) diff(%s)"
                % (decompile_file, diff_str))
            return False

        begin_i = 0 if find_i < 9 else find_i - 9
        instr_str_list = []
        for i in range(begin_i, find_i + 1):
            instr_str_list.append(ret[i][0] + "\n")
        instr_str = "".join(instr_str_list).strip("\n")

        info.instr += "\nrelated instructions (error occured before the mark *):\n\n"
        info.instr += instr_str[:instr_str.rfind('\n') + 1] + '*'
        info.instr += instr_str[instr_str.rfind('\n') + 2:]
        info.instr += "\n\nFor complete instructions, please view %s" % decompile_file

        return True

    @staticmethod
    def _write_errorinfo_file(err_i_folder: str, info: any, index: int) -> None:
        info_file = os.path.join(err_i_folder, "info.txt")
        utils.write_file(info_file, info.analyse())
        utils.print_info_log('The ai core error info for No.%s is saved '
                             'in %s' % (index, info_file))

    def _aicore_error_data(self: any) -> list:
        aicore_error_data_list = []
        # get all error log
        self._get_all_error_log()
        # get all IMAS log
        self._get_imas_log()
        # 地址越界检测
        addr_overflow = self._get_addr_overflow()

        # 获取分配的device地址
        alloc_addr = self._get_alloc_addr()

        # 获取真实地址
        actual_addr = self._get_actual_addr()

        # get graph file
        graph_file = self._get_graph_file()
        aicore_error_data_list.extend([addr_overflow, alloc_addr,
                                       actual_addr, graph_file])
        return aicore_error_data_list

    def parse(self: any) -> None:
        """
        parse by collection info
        """
        utils.print_info_log('******************Analysis******************')
        aicore_error_data_list = self._aicore_error_data()
        utils.print_info_log('Start to analyze each ai core error.')
        summary_info_list = []

        # decompile
        if "aarch64" in platform.machine():
            obj_dump_file = "cce-objdump_aarch64"
        else:
            obj_dump_file = "cce-objdump"

        obj_dump_file = os.path.join(os.getcwd(), "tools", obj_dump_file)
        if os.path.exists(obj_dump_file):
            os.system("chmod 755 " + obj_dump_file)
            os.environ["PATH"] = os.path.join(os.getcwd(), "tools") + ":" + os.environ["PATH"]
        else:
            cce_dump = shutil.which("cce-objdump")
            if not cce_dump:
                # guess where is cce-objdump
                parent_path = "aarch64-linux" if "aarch64" in platform.machine() else "x86_64-linux"
                cce_dump_guess = os.path.join("usr/local/Ascend/latest", parent_path, "ccec_compiler/bin/cce-objdump")
                if os.path.exists(cce_dump_guess):
                    cce_dump = cce_dump_guess
                
            if not cce_dump:
                 utils.print_error_log('Cannot find  cce-objdump! please add cce-objdump path in env PATH.')
                 raise utils.AicErrException(Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
        for i, current_pc in enumerate(self.collection.ai_core_error_list):
            # parser aic error by slog
            info = AicErrorInfo()
            info.err_time, info.dev_id, info.stream_id, info.task_id, \
            info.core_id, info.aic_error, info.start_pc, info.extra_info, \
            info.current_pc = current_pc

            utils.print_info_log("******************No.%d %s******************"
                                 % (i, info.err_time))
            info.err_time_obj = utils.strplogtime(info.err_time)
            err_i_folder_name = "aicerror_%d_%s" % (
                i, time.strftime("%Y%m%d%H%M%S", info.err_time_obj.timetuple()))
            err_i_folder = os.path.join(self.output_path, err_i_folder_name)
            utils.check_path_valid(err_i_folder, isdir=True, output=True)
            info.node_name = self.collection.node_name_list[i]
            info.kernel_name = self.collection.kernel_name_list[i]
            # get hisi log
            self._get_hisi_log(info, err_i_folder)
            # get op info in build proto file
            self._get_op_by_graph(aicore_error_data_list[Constant.GRAPH_FILE], info)
            kernel_meta_path = os.path.join(
                self.collection.collect_compile_path, 'kernel_meta')
            if os.path.exists(kernel_meta_path):
                # 反编译  出错指令
                result = self._decompile([info.kernel_name, kernel_meta_path],
                                         err_i_folder, info)
                if result is False:
                    utils.print_warn_log("decompile kernel_meta file %s failed." %
                                         os.path.join(kernel_meta_path, info.kernel_name + ".o"))
            else:
                utils.print_warn_log(
                    "kernel_meta path %s not exist" % kernel_meta_path)
            try:
                # input output address
                info.aval_addrs = self._get_available_addrs(info.err_time)
                info.necessary_addr = self._get_necessary_addrs(info.kernel_name)
                self._check_addr(info.aval_addrs, info.necessary_addr)
                # self.print_summary(avl_addr, necessary_addr)
            except BaseException as e:
                import logging
                logging.exception(e)
                print("Check addr error failed")


            info.input_output_addrs = self._get_input_output_addrs(
                info, err_i_folder, aicore_error_data_list[Constant.ALLOC_ADDR],
                aicore_error_data_list[Constant.ACTUAL_ADDR])

            # 地址越界信息收集
            info.addr_overflow = aicore_error_data_list[Constant.ADDR_OVERFLOW]
            # 算子代码地址，args地址
            info.op_addr, info.args_addr, info.multi_args_addr = \
                self._get_op_and_args_addr(info.start_pc)

            # parse dump
            if self.collection.collect_dump_path:
                parser = DumpDataParser(self.collection.collect_dump_path,
                                        info.node_name, info.kernel_name)
                info.dump_info = parser.parse()

            # write info file
            self._write_errorinfo_file(err_i_folder, info, i)

            summary_info_list.append(
                "%s   %s   device_id=%s   core_id=%s   task_id=%s   node=%s   "
                "kernel=%s" % (err_i_folder_name, info.aic_error, info.dev_id,
                               info.core_id, info.task_id, info.node_name,
                               info.kernel_name))
        utils.print_info_log('Finish to analyze each ai core error.')
        # write summary info
        self._write_summary_file(summary_info_list)

    def get_output_path(self: any) -> str:
        """
        get output path
        """
        return self.output_path
