#!/usr/bin/env python
# coding=utf-8
"""
Function:
AicoreErrorParser class. This file mainly involves the parse function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import re
from ms_interface import utils
import struct
from ms_interface.constant import Constant


class AicErrorInfo:
    """
    AI core Error info
    """

    def __init__(self: any) -> None:
        self.dev_id = ""
        self.core_id = ""
        self.aic_error = ""  # err_code
        self.aicerror_bit = []  # [1,2,3...]
        self.task_id = ""
        self.stream_id = ""
        self.node_name = ""
        self.kernel_name = ""
        self.start_pc = ""
        self.current_pc = ""
        self.instr = ""
        self.operator = ""
        self.extra_info = ""
        self.err_time_obj = None
        self.err_time = ""
        self.ifu_err_type = ""
        self.mte_err_type = ""
        self.args_num_in_json = None
        self.dump_info = ""
        self.aval_addrs = []
        self.necessary_addr = {}
        self.atomic_add_err = False
        self.single_op_test_result = True
        self.data_dump_result = True
        self.atomic_clean_check = True
        self.args_before_list = []
        self.args_after_list = []
        self.addr_valid = True

    def analyse(self: any) -> str:
        """
        AI core error analyse
        """
        # 此步骤会解析出 mte_err_type ifu_err_type
        aicerror_info = self._get_aicerror_info()

        addr_check_str = self._get_addr_check_str()
        tiling_str = self._get_tiling_str()
        single_op_test_result = "No Error" if self.single_op_test_result else "Aicore Error"

        analysis_result = "Analysis result: success."
        conclusion = self._get_conclusion()

        msg = f"""{analysis_result}

"**********************Root cause conclusion******************"
{conclusion}

***********************1. Basic information********************
error time   : {self.err_time}
device id    : {self.dev_id}
core id      : {self.core_id}
task id      : {self.task_id}
stream id    : {self.stream_id}
node name    : {self.node_name}
kernel name  : {self.kernel_name}

***********************2. AICERROR code***********************
error code  : {self.aic_error}
error bits : 
{aicerror_info}

***********************3. Instructions************************
start   pc   : {self.start_pc}
current pc   : {self.current_pc}
instruction  : {self.instr}

****************4. Input and output of node*******************
{addr_check_str}
args before excute: {self._get_args_str(self.args_before_list)}
args after  excute: {self._get_args_str(self.args_after_list)}

***********************5. Dump info*************************
{tiling_str}
{self.dump_info}

********************6. Single Op Test***********************
{single_op_test_result}

***********************7. Op in graph*************************
{self.operator}

"""
        return msg

    def _get_conclusion(self: any) -> str:
        conclusion = ""
        if not self.atomic_clean_check:
            conclusion = "Op need atomic clean. However, no memset or atomic_clean op launched.\n"
        elif not self.data_dump_result:
            conclusion = "Dump data failed in exception dump! Address of input or output is error!"
        elif self.current_pc == "0x0":
            conclusion = "Memory of operator code has been over write falsely\n"
        elif self.atomic_add_err:
            conclusion = "\"dha status 1\" found in log. It means Atomic accumulation exception, "\
                          "please check the input data and network accuracy.\n"\
                          "Attention please,  if multiple tasks are running on the same device at the same time, "\
                          "false positives may be generated. You are advised to pull up only one task and collect it ."
        elif "data invalid" in self.dump_info:
            conclusion = "Input data is abnormal. Check the network accuracy.\n"
        elif not self.single_op_test_result:
            conclusion = "Single op test aicore error, please check op.\n"
        elif not self._check_args():
            conclusion = "The args of op is diffrerent before and after excute, args may be overwrited by other op."\
                         "Please use oom to continue debug.\n"
        elif not self.addr_valid:
            conclusion = "Please check addrs. The addr of input/output is used but not alloc, "\
                         "details in \"4. Input and output of node\"\n"
        else:
            conclusion = "There's no obvious known error, so I can't determine what the error is.\n"
        return conclusion

    def _check_args(self: any) -> bool:
        for args_after in self.args_after_list:
            for args_before in self.args_before_list:
                if args_after == args_before:
                    return True
            return False

    def _get_args_str(self: any, input_list: list) -> str:
        args_str = ""
        for args in input_list:
            hex_str = ", ".join([hex(i) for i in args])
            args_str += f"[{hex_str}],"
        return f"[{args_str[:-1]}]"

    def _get_tiling_str(self: any) -> str:
        result_str = ""
        tiling_datas = self.necessary_addr["tiling"]
        if len(tiling_datas) < 3:
            utils.print_info_log("Tiling data incomplete!")
            return ""
        tiling_data = tiling_datas[1]
        result_str += f"tiling data: {tiling_data}\n"
        result_str += "tiling data in int32: "

        return result_str + "\n"

    def _get_tiling_str(self: any) -> str:
        result_str = ""
        tiling_datas = self.necessary_addr["tiling"][1]
        int32_size = struct.calcsize('i')
        int64_size = struct.calcsize('q')
        float16_size = struct.calcsize('e')

        def parse_data(data, size, format):
            try:
                result = [struct.unpack(format, data[i:i + size])[0] for i in range(0, len(data), size)]
            except Exception as e:
                result = "Cannot decode in this dtype"
            return result

        int32_values = parse_data(tiling_datas, int32_size, 'i')
        result_str += "tiling data in int32: "
        result_str += f"tiling data: {int32_values}\n"

        int64_values = parse_data(tiling_datas, int64_size, 'q')
        result_str += "tiling data in int64: "
        result_str += f"tiling data: {int64_values}\n"

        float16_values = parse_data(tiling_datas, float16_size, 'e')
        result_str += "tiling data in float16: "
        result_str += f"tiling data: {float16_values}\n"

        return result_str + "\n"

    def _get_addr_check_str(self: any) -> str:
        result_str = ""
        used_addrs = self.necessary_addr

        if not used_addrs:
            input_params, output_params = [], []
        else:
            input_params = used_addrs.get("input_addr")
            output_params = used_addrs.get("output_addr")

        for input_param in input_params:
            index = input_param.get("index")
            if not input_param.get("in_range"):
                result_str += f"*[ERROR]input[{index}] is out of range\n"
                self.addr_valid = False

        for output_param in output_params:
            index = output_param.get("index")
            if not output_param.get("in_range"):
                result_str += f"*[ERROR]output[{index}] is out of range\n"
                self.addr_valid = False
        result_str += "\n"
        for input_param in input_params:
            index = int(input_param.get("index"))
            size = int(input_param.get("size"))
            if input_param.get("addr").startswith("0x"):
                addr = int(input_param.get("addr"), 16)
            else:
                addr = int(input_param.get("addr"))
            end_addr = addr + size
            result_str += f"input[{index}] addr: {hex(addr)} end_addr:{hex(end_addr)} size: {hex(size)}\n"

        for output_param in output_params:
            index = int(output_param.get("index"))
            size = int(output_param.get("size"))
            if output_param.get("addr").startswith("0x"):
                addr = int(output_param.get("addr"), 16)
            else:
                addr = int(output_param.get("addr"))
            end_addr = addr + size
            result_str += f"output[{index}] addr: {hex(addr)} end_addr:{hex(end_addr)} size: {hex(size)}\n"
        
        fault_arg_indexes = used_addrs.get("fault_arg_index")
        need_check_args = used_addrs.get("need_check_args")
        if fault_arg_indexes:
            for arg_index in fault_arg_indexes:
              result_str += f"arg[{arg_index}][0x{need_check_args[arg_index]:X}] need be checked \n"

        workspace = used_addrs.get("workspace")
        if workspace:
            result_str += f"workspace_bytes:{workspace}\n"

        return result_str

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
                aicerror_info_list.append("\nVEC_ERR_INFO: " + self._analyse_vec_errinfo())
            elif err_type == "ifu":
                aicerror_info_list.append("\nIFU_ERR_INFO: " + self._analyse_ifu_errinfo())
            elif err_type == "mte":
                aicerror_info_list.append("\nMTE_ERR_INFO: " + self._analyse_mte_errinfo(i))
            elif err_type == "cube":
                aicerror_info_list.append("\nCUBE_ERR_INFO: " + self._analyse_cube_errinfo())
            elif err_type == "ccu":
                aicerror_info_list.append("\nCCU_ERR_INFO: " + self._analyse_ccu_errinfo())
            elif err_type == "biu":
                aicerror_info_list.append("\nBIU_ERR_INFO: " + self._analyse_biu_errinfo())
            aicerror_info_list.append(f"\n{aicerr_info}")
            aicerror_info_list.append("\n\n")
        aicerror_info = "".join(aicerror_info_list).strip("\n")
        return aicerror_info

    # Error PC [9:2]
    def find_extra_pc(self: any) -> str:
        """
        find extra pc
        """
        ret = utils.hexstr_to_list_bin(self.aic_error)
        if not ret:
            ret = [0]
        self.aicerror_bit = ret
        extra_err_key = ""
        key_map = {
            "vec": Constant.VEC_KEY,
            "mte": Constant.MTE_KEY,
            "cube": Constant.CUBE_KEY,
            "ccu": Constant.CCU_KEY,
            "biu": Constant.BIU_KEY,
            "ifu": Constant.IFU_KEY
        }
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
        regexp = Constant.IFU_KEY + r"=(\S+)"
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
        errinfo += f"\nifu_err_type bit[50:48]={code}  meaning:{info}"

        # ifu_err_addr
        code = utils.get_01_from_hexstr(ret[0], 47, 2)
        info = "IFU Error Address [47:2]"
        # 补2位0，猜测值
        approximate = hex(int(code + "00", 2))
        errinfo += f"\nifu_err_addr bit[47:2]={code}  meaning:{info}  approximate:{approximate}"
        return errinfo

    def _analyse_mte_errinfo(self: any, err_bit: any) -> str:
        regexp = Constant.MTE_KEY + r"=(\S+)"
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
        errinfo += f"\nmte_err_type bit[26:24]={code}  meaning:{info}"

        # mte_err_addr
        code = utils.get_01_from_hexstr(ret[0], 22, 8)
        info = "MTE Error Address [19:5]"
        # 补5位0，猜测值
        approximate = hex(int(code + "00000", 2))
        errinfo += f"\nmte_err_addr bit[22:8]={code}  meaning:{info}  approximate:{approximate}"
        return errinfo

    def _analyse_biu_errinfo(self: any) -> str:
        regexp = Constant.BIU_KEY + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No BIU_ERR_INFO found"

        errinfo = ret[0]
        # biu_err_addr
        code = utils.get_01_from_hexstr(ret[0], 24, 0)
        approximate = hex(int(code, 2))
        errinfo += f"\nbiu_err_addr bit[24:0]={code}  in hex:{approximate}"
        return errinfo

    def _analyse_ccu_errinfo(self: any) -> str:
        regexp = Constant.CCU_KEY + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No CCU_ERR_INFO found"

        errinfo = ret[0]
        # ccu_err_addr
        code = utils.get_01_from_hexstr(ret[0], 22, 8)
        info = "CCU Error Address [17:3]"
        # 补3位0，猜测值
        approximate = hex(int(code + "000", 2))
        errinfo += f"\nccu_err_addr bit[22:8]={code}  meaning:{info}  approximate:{approximate}"
        return errinfo

    def _analyse_cube_errinfo(self: any) -> str:
        regexp = Constant.CUBE_KEY + r"=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if len(ret) == 0:
            return "No CUBE_ERR_INFO found"

        errinfo = ret[0]
        # cube_err_addr
        code = utils.get_01_from_hexstr(ret[0], 16, 8)
        info = "CUBE Error Address [17:9]"
        # 补9位0，猜测值
        approximate = hex(int(code + "000000000", 2))
        errinfo += f"\ncube_err_addr bit[16:8]={code}  meaning:{info}  approximate:{approximate}"
        return errinfo

    def _analyse_vec_errinfo(self: any) -> str:
        regexp = f"{Constant.VEC_KEY}=(\S+)"
        ret = re.findall(regexp, self.extra_info, re.M)
        if not ret:
            return "No VEC_ERR_INFO found"

        errinfo = ret[0]
        # vec_err_addr
        code = utils.get_01_from_hexstr(ret[0], 28, 16)
        info = "VEC Error Address [17:5]"
        # 补5位0，猜测值
        approximate = hex(int(code + "00000", 2))
        errinfo += f"\nvec_err_addr bit[28:16]={code}  meaning:{info}  approximate:{approximate}"

        # vec_err_rcnt
        code = utils.get_01_from_hexstr(ret[0], 15, 8)
        info = "VEC Error repeat count [7:0]"
        repeats = str(int(code, 2))
        errinfo += f"\nvec_err_rcnt bit[15:8]={code}  meaning:{info}  repeats:{repeats}"
        return errinfo
