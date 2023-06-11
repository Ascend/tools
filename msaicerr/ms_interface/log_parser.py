#!/usr/bin/env python
# coding=utf-8
"""
Function:
This file mainly involves the common function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""
from ms_interface import utils
from ms_interface.constant import Constant


class HostLogParser:
    def __init__(self, collect_plog_path: str):
        self.ai_core_error_list = []
        self.kernel_name_list = []
        self.node_name_list = []
        self.collect_plog_path = collect_plog_path

    def _get_node_and_kernel_name(self: any) -> list:
        # 获取kernel_name
        kernel_name_cmd = ['grep', '\[AIC_INFO\] dev_func:', '-inrE', self.collect_plog_path]
        kernel_name_regexp = r".+?dev_func:([a-zA-Z0-9_]{0,})"
        kernel_name_ret = utils.get_inquire_result(kernel_name_cmd, kernel_name_regexp)
        if not kernel_name_ret:
            utils.print_error_log("Failed to get kernel name.")
            raise utils.AicErrException(Constant.MS_AICERR_FIND_DATA_ERROR)
        kernel_name_list = kernel_name_ret[0].split('__')
        kernel_name = kernel_name_list[0]

        # 获取node_name、stream_id、task_id
        node_name_cmd = ['grep', '\[AIC_INFO\] node_name:', '-inrE', self.collect_plog_path]
        regexp = r".+?node_name:(.*?),.*stream_id:(\d+)\s*.+?\s*task_id:(\d+)\s*"
        result = utils.get_inquire_result(node_name_cmd, regexp)
        if not result:
            utils.print_error_log("Failed to get node name, stream id and task id.")
            raise utils.AicErrException(Constant.MS_AICERR_FIND_DATA_ERROR)
        result_list = [''] * 4
        result_list[0] = result[0][1]
        result_list[1] = result[0][2]
        result_list[2] = result[0][0]
        result_list[3] = kernel_name
        return result_list

    @staticmethod
    def _get_extra_info(aic_error):
        '''
         为兼容原device log框架生成一个extra info参数
        :param aic_error: 正则匹配结果
        :return: 返回的extra info
        '''

        result = "extra info:\n"
        result += "IFU_ERR_INFO={}\n".format(aic_error[8])
        result += "CCU_ERR_INFO={}\n".format(aic_error[9])
        result += "BIU_ERR_INFO={}\n".format(aic_error[11])
        result += "CUBE_ERR_INFO={}\n".format(aic_error[10])
        result += "MTE_ERR_INFO={}\n".format(aic_error[7])
        result += "VEC_ERR_INFO={}\n".format(aic_error[6])
        return result

    
    def _get_v300_error_code(self: any) -> list:
        cmd = ['grep', 'The extend info: errcode:', '-nr', self.collect_plog_path]
        regexp = r"\(([0-9xa-eA-E]+),\s*([0-9xa-eA-E]+),\s*([0-9xa-eA-E]+)\)"
        ret = utils.get_inquire_result(cmd, regexp)
        new_codes = []
        for _, (code0, code1, code2) in enumerate(ret):
            code0_int = utils.get_hexstr_value(code0)
            code1_int = utils.get_hexstr_value(code1)
            code1_int = code1_int << 64
            code2_int = utils.get_hexstr_value(code2) 
            code2_int = (((code2_int >> 32) << 17) & (code2_int & 0x1FFFF)) << 128
            new_code = code0_int | code1_int | code2_int
            new_codes.append(hex(new_code))
        return new_codes


    def get_op_info(self: any) -> tuple:
        aicore_err_cmd = ['grep', 'there is an aicore error|there is an .*aivec.* error exception', '-inrE', 
                          self.collect_plog_path]
        aicore_err_regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?device\(([a-zA-Z0-9\s,:]{1,})\),\s" \
                            r"[a-zA-Z0-9\s,]{1,},\score id is (\d+),\s+error code = (\S+),.*?pc start:\s(\S+)," \
                            r"\scurrent:\s(\S+),\svec error info:\s(\S+),\smte error info:\s(\S+)," \
                            r"\sifu error info:\s(\S+),\sccu error info:\s(\S+),\scube error info:\s(\S+)," \
                            r"\sbiu error info:\s(\S+),\saic error mask:\s(\S+),\spara base:\s(\S+)."
        aic_err_ret = utils.get_inquire_result(aicore_err_cmd, aicore_err_regexp)
        if not aic_err_ret:
            utils.print_error_log("aic error info does not match in plog \"aicore error exception\"")
            raise utils.AicErrException(Constant.MS_AICERR_FIND_DATA_ERROR)
        if len(aic_err_ret) > 1:
            utils.print_error_log("Find more than one aicore error, choose first one to analysis")
            aic_err_ret = (aic_err_ret[0],)
        new_codes = []
        if aic_err_ret[0][3] == "0" or aic_err_ret[0][3] == "0x0":
            new_codes = self._get_v300_error_code()
        for aic_err in aic_err_ret:
            stream_id, task_id, node_name, kernel_name = self._get_node_and_kernel_name()
            extra_info = self._get_extra_info(aic_err)
            if node_name == '' and kernel_name == '':
                continue
            
            # 适配原开发过程中的device_aic_err
            device_aic_err = [None] * 9
            device_aic_err[0] = aic_err[0]  # err time
            device_aic_err[1] = aic_err[1]  # dev id
            device_aic_err[2] = stream_id  # stream id
            device_aic_err[3] = task_id  # task id
            device_aic_err[4] = aic_err[2]  # core id
            if len(new_codes) > 0:
                device_aic_err[5] = new_codes[0]  # aic error code
            else:
                device_aic_err[5] = aic_err[3]  # aic error code
            device_aic_err[6] = aic_err[4]  # start pc
            device_aic_err[7] = extra_info  # extra_info
            device_aic_err[8] = aic_err[5]  # current pc

            self.ai_core_error_list.append(device_aic_err)
            self.node_name_list.append(node_name)
            self.kernel_name_list.append(kernel_name)
        return self.ai_core_error_list, self.node_name_list, self.kernel_name_list
