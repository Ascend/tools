#!/usr/bin/env python
# coding=utf-8
"""
Function:
AicoreErrorParser class. This file mainly involves the parse function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import re
from typing import List
from ms_interface import utils
from ms_interface.constant import Constant


class AicErrorInfo:
    """
    AI core Error info
    """
    def __init__(self: any) -> None:
        self.dev_id = ""
        self.core_id = ""
        self.aic_error = ""
        self.aicerror_bit = []  # [1,2,3...]
        self.task_id = ""
        self.stream_id = ""
        self.node_name = ""
        self.kernel_name = ""
        self.start_pc = ""
        self.current_pc = ""
        self.input_output_addrs = []  # [OpInputOutput]
        self.instr = ""
        self.operator = ""
        self.extra_info = ""
        self.err_time_obj = None
        self.err_time = ""
        self.addr_overflow = []
        self.ifu_err_type = ""
        self.mte_err_type = ""
        self.args_num_in_json = None
        self.op_addr = ""
        self.args_addr = ""
        self.multi_args_addr = False
        self.dump_info = ""
        self.aval_addrs = []
        self.necessary_addr = {}

        self.ifu_key = "IFU_ERR_INFO"
        self.ccu_key = "CCU_ERR_INFO"
        self.biu_key = "BIU_ERR_INFO"
        self.cube_key = "CUBE_ERR_INFO"
        self.mte_key = "MTE_ERR_INFO"
        self.vec_key = "VEC_ERR_INFO"

    def analyse(self: any) -> str:
        """
        AI core error analyse
        """
        self.aicerror_bit = utils.hexstr_to_list_bin(self.aic_error)
        # 此步骤会解析出 mte_err_type ifu_err_type
        aicerror_info = self._get_aicerror_info()
        # 组织input output
        # input_output_addrs_str = self._get_input_output_addrs_str()

        addr_check_str = self._get_addr_check_str()

        args_addr_str = self.args_addr if not self.multi_args_addr \
            else self.args_addr + "  (multiple)"

        msg = """
***********************1. Basic information********************
error time   : %s
device id    : %s
core id      : %s
task id      : %s
stream id    : %s
node name    : %s
kernel name  : %s
op address   : %s
args address : %s

***********************2. AICERROR code***********************
code  : %s
error bits : 
%s

***********************3. Instructions************************
start   pc   : %s
current pc   : %s
%s

****************4. Input and output of node*******************
%s

***********************5. Op in graph*************************
%s

""" % (
    self.err_time, self.dev_id, self.core_id, self.task_id,
    self.stream_id, self.node_name, self.kernel_name, self.op_addr,
    args_addr_str, self.aic_error, aicerror_info, self.start_pc,
    self.current_pc, self.instr, addr_check_str, self.operator)
        if self.dump_info != "":
            msg += """
***********************6. Dump info*************************
%s
""" % self.dump_info

        # 0x800000 推断
        conclusion = ""
        if 23 in self.aicerror_bit and self.addr_overflow != []:
            conclusion = "Access ddr address out of boundary\n" + '\n'.join(
                self.addr_overflow)
        elif self.current_pc == "0x0":
            conclusion = "Memory of operator code has been overwrited " \
                         "falsely\n"
            if self.op_addr != "":
                conclusion += "The memory address is %s\n" % self.op_addr
        if conclusion != "":
            msg = "********************Root cause conclusion****************" \
                  "*****\n%s\n" % conclusion + msg
        else:
            msg = "********************Root cause conclusion****************" \
                  "*****\n%s\n" % "Not available" + msg
        return msg

    def _get_addr_check_str(self: any) -> str:
      result_str = ""
      used_addrs = self.necessary_addr
      ava_addr = self.aval_addrs
      if not used_addrs:
          input_params, output_params = [], []
      else:
          input_params = used_addrs.get("input_addr")
          output_params = used_addrs.get("output_addr")
      workspace = used_addrs.get("workspace")
      for input_param in input_params:
          index  = input_param.get("index")
          if input_param.get("invalid"):
              result_str += f"*[ERROR]input[{index}] is out of range\n"

      for output_param in output_params:
          index  = output_param.get("index")
          if output_param.get("invalid"):
              result_str += f"*[ERROR]output[{index}] is out of range\n"
      result_str += "\n"
      for input_param in input_params:
          index = int(input_param.get("index"))
          size = int(input_param.get("size"))
          addr = int(input_param.get("addr"))
          end_addr = addr + size
          result_str += f"input[{index}] addr: {hex(addr)} end_addr:{hex(end_addr)} size: {hex(size)}\n"

      for output_param in output_params:
          index = int(output_param.get("index"))
          size = int(output_param.get("size"))
          addr = int(output_param.get("addr"))
          end_addr = addr + size
          result_str += f"output[{index}] addr: {hex(addr)} end_addr:{hex(end_addr)} size: {hex(size)}\n"

      if workspace:
          result_str += f"workspace_bytes:{workspace}\n"

      result_str += "\navaliable addrs:\nstart_addr            end_addr              size\n"
      for alloc_addr in ava_addr:
          start_addr = int(alloc_addr[0], 16)
          size = int(alloc_addr[1])
          end_addr = start_addr + size
          result_str += f"{hex(start_addr)}        {hex(end_addr)}        {hex(size)}\n"
      
      return result_str

    def _get_input_output_addrs_str(self: any) -> str:
        input_output_addrs_str_list = []
        for i in self.input_output_addrs:
            has_nan_inf_str = "NaN/INF" if i.has_nan_inf else ""
            size_str = "size: %d" % i.size if i.size != 0 else ""
            actual_addr_str = " new addr: %s" % i.actual_addr \
                if i.actual_addr != "" else ""
            overflow_str = "OVERFLOW" if i.overflow else ""
            each_input_output_addrs_str = "%s  addr: %s  %s  %s  %s  %s\n" % (
                i.name, i.addr, size_str, actual_addr_str, overflow_str,
                has_nan_inf_str)
            input_output_addrs_str_list.append(each_input_output_addrs_str)
        input_output_addrs_str = "".join(input_output_addrs_str_list)
        if self.args_num_in_json is not None and self.input_output_addrs != [] \
                and len(self.input_output_addrs) != self.args_num_in_json:
            input_output_addrs_str += "\nWARNING: kernel args amount is " \
                                      "not equal to input/output amount"
        input_output_addrs_str = input_output_addrs_str.strip("\n")
        input_output_addrs_str += self._format_aval_addrs(self.aval_addrs)
        return input_output_addrs_str
    
    def _format_aval_addrs(self, addr_list:List) -> str:
        ret = "\navaliable addrs:\nstart_addr        size\n"
        for addr_range in addr_list:
            ret += str(addr_range[0]) + "    " + str(addr_range[1]) + "\n"
        return ret

    def _get_aicerror_info(self: any) -> str:
        aicerror_info_list = []
        handled_err_type = []
        for i in self.aicerror_bit:
            aicerr_info = Constant.AIC_ERROR_INFO_DICT.get(i)
            err_type = aicerr_info.split('_')[0].lower()
            if err_type in handled_err_type:
                continue
            handled_err_type.append(err_type)
            if err_type == "vec":
                aicerror_info_list.append("\nVEC_ERR_INFO: "
                                          + self._analyse_vec_errinfo())
            elif err_type == "ifu":
                aicerror_info_list.append("\nIFU_ERR_INFO: "
                                          + self._analyse_ifu_errinfo())
            elif err_type == "mte":
                aicerror_info_list.append("\nMTE_ERR_INFO: "
                                          + self._analyse_mte_errinfo(i))
            elif err_type == "cube":
                aicerror_info_list.append("\nCUBE_ERR_INFO: "
                                          + self._analyse_cube_errinfo())
            elif err_type == "ccu":
                aicerror_info_list.append("\nCCU_ERR_INFO: "
                                          + self._analyse_ccu_errinfo())
            elif err_type == "biu":
                aicerror_info_list.append("\nBIU_ERR_INFO: "
                                          + self._analyse_biu_errinfo())
            aicerror_info_list.append("\n\n")
        aicerror_info = "".join(aicerror_info_list).strip("\n")
        return aicerror_info

    # Error PC [9:2]
    def find_extra_pc(self: any) -> str:
        """
        find extra pc
        """
        ret = utils.hexstr_to_list_bin(self.aic_error)
        extra_err_key = ""
        key_map = {"vec": self.vec_key,
                   "mte": self.mte_key,
                   "cube": self.cube_key,
                   "ccu": self.ccu_key}
        for ret_a in ret:
            error_info = Constant.AIC_ERROR_INFO_DICT.get(ret_a)
            err_type = error_info.split('_')[0].lower()
            if err_type in key_map.keys():
                extra_err_key = key_map.get(err_type)
                break

        if extra_err_key == "":
            return ""
        regexp = extra_err_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return ""
        return utils.get_01_from_hexstr(ret[0], 7, 0)

    def _analyse_ifu_errinfo(self: any) -> str:
        regexp = self.ifu_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No IFU_ERR_INFO found"

        errinfo = ret[0]
        # ifu_err_type
        code = utils.get_01_from_hexstr(ret[0], 50, 48)
        self.ifu_err_type = code

        if code in Constant.SOC_ERR_INFO_DICT:
            info = Constant.SOC_ERR_INFO_DICT.get(code)
        else:
            info = "NA"
        errinfo += "\n    ifu_err_type bit[50:48]=%s  meaning:%s" % (
            code, info)

        # ifu_err_addr
        code = utils.get_01_from_hexstr(ret[0], 47, 2)
        info = "IFU Error Address [47:2]"
        # 补2位0，猜测值
        approximate = hex(int(code + "00", 2))
        errinfo += "\n    ifu_err_addr bit[47:2]=%s  meaning:%s  " \
                   "approximate:%s" % (code, info, approximate)
        return errinfo

    def _analyse_mte_errinfo(self: any, err_bit: any) -> str:
        regexp = self.mte_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No MTE_ERR_INFO found"

        errinfo = ret[0]
        # mte_err_type
        code = utils.get_01_from_hexstr(ret[0], 26, 24)
        self.mte_err_type = code

        if err_bit == 46:
            mte_dict = Constant.UNZIP_ERR_INFO_DICT
        elif err_bit == 34:
            mte_dict = Constant.FMC_ERR_INFO_DICT
        elif err_bit == 25:
            mte_dict = Constant.FMD_ERR_INFO_DICT
        elif err_bit == 23:
            mte_dict = Constant.SOC_ERR_INFO_DICT
        elif err_bit == 21:
            mte_dict = Constant.AIPP_ERR_INFO_DICT
        else:
            mte_dict = {}

        if code in mte_dict:
            info = mte_dict.get(code)
        else:
            info = "NA"
        errinfo += "\n    mte_err_type bit[26:24]=%s  meaning:%s" % (
            code, info)

        # mte_err_addr
        code = utils.get_01_from_hexstr(ret[0], 22, 8)
        info = "MTE Error Address [19:5]"
        # 补5位0，猜测值
        approximate = hex(int(code + "00000", 2))
        errinfo += "\n    mte_err_addr bit[22:8]=%s  meaning:%s " \
                   " approximate:%s" % (code, info, approximate)
        return errinfo

    def _analyse_biu_errinfo(self: any) -> str:
        regexp = self.biu_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No BIU_ERR_INFO found"

        errinfo = ret[0]
        # biu_err_addr
        code = utils.get_01_from_hexstr(ret[0], 24, 0)
        approximate = hex(int(code, 2))
        errinfo += "\n    biu_err_addr bit[24:0]=%s  in hex:%s" % (
            code, approximate)
        return errinfo

    def _analyse_ccu_errinfo(self: any) -> str:
        regexp = self.ccu_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No CCU_ERR_INFO found"

        errinfo = ret[0]
        # ccu_err_addr
        code = utils.get_01_from_hexstr(ret[0], 22, 8)
        info = "CCU Error Address [17:3]"
        # 补3位0，猜测值
        approximate = hex(int(code + "000", 2))
        errinfo += "\n    ccu_err_addr bit[22:8]=%s  meaning:%s " \
                   " approximate:%s" % (code, info, approximate)
        return errinfo

    def _analyse_cube_errinfo(self: any) -> str:
        regexp = self.cube_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No CUBE_ERR_INFO found"

        errinfo = ret[0]
        # cube_err_addr
        code = utils.get_01_from_hexstr(ret[0], 16, 8)
        info = "CUBE Error Address [17:9]"
        # 补9位0，猜测值
        approximate = hex(int(code + "000000000", 2))
        errinfo += "\n    cube_err_addr bit[16:8]=%s  meaning:%s  " \
                   "approximate:%s" % (code, info, approximate)
        return errinfo

    def _analyse_vec_errinfo(self: any) -> str:
        regexp = self.vec_key + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No VEC_ERR_INFO found"

        errinfo = ret[0]
        # vec_err_addr
        code = utils.get_01_from_hexstr(ret[0], 28, 16)
        info = "VEC Error Address [17:5]"
        # 补5位0，猜测值
        approximate = hex(int(code + "00000", 2))
        errinfo += "\n    vec_err_addr bit[28:16]=%s  meaning:%s  " \
                   "approximate:%s" % (code, info, approximate)

        # vec_err_rcnt
        code = utils.get_01_from_hexstr(ret[0], 15, 8)
        info = "VEC Error repeat count [7:0]"
        repeats = str(int(code, 2))
        errinfo += "\n    vec_err_rcnt bit[15:8]=%s  meaning:%s  " \
                   "repeats:%s" % (code, info, repeats)
        return errinfo
