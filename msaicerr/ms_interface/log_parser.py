from platform import node
import time
from abc import abstractmethod

import re

from ms_interface import utils
from ms_interface.constant import Constant


class LogParser:
    def __init__(self, collect_applog_path: str, collect_slog_path=None):
        self.collect_compile_path = None
        self.ai_core_error_list = []
        self.kernel_name_list = []
        self.node_name_list = []
        self.collect_applog_path = collect_applog_path
        self.collect_slog_path = collect_slog_path

    @abstractmethod
    def get_op_info(self: any) -> tuple:
        """
        _get_op_info
        """


class DeviceLogParser(LogParser):
    def _get_node_and_kernel_name_execute_command(self: any) -> any:
        grep_cmd = ['grep', 'PrintErrorInfo:.*?aicore kernel execute failed',
                    '-inrE', self.collect_applog_path]
        status, data = utils.execute_command(grep_cmd)
        if status != 0:
            utils.print_error_log("Failed to execute command: %s." % " ".join(grep_cmd))
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        return data

    @staticmethod
    def _get_the_latest_aicerr_form_ret(ret: list, err_time: any) -> int:
        max_i = -1
        max_time_obj = None
        for i, (time_str, _, _) in enumerate(ret):
            time_obj = utils.strplogtime(time_str)
            # 都找最迟的会找到同一个，加个条件时间要早于AICERROR时间，
            # 前提host、device时间同步。否则去掉and前的条件。
            if err_time >= time_obj and (
                    max_time_obj is None or time_obj > max_time_obj):
                max_time_obj = time_obj
                max_i = i
        if max_i == -1:
            for i, (time_str, _, _) in enumerate(ret):
                time_obj = utils.strplogtime(time_str)
                if max_time_obj is None or time_obj > max_time_obj:
                    max_time_obj = time_obj
                    max_i = i
        if max_i == -1:
            utils.print_error_log("Failed to get node and kernel name.")
            raise utils.AicErrException(Constant.MS_AICERR_FIND_DATA_ERROR)
        return max_i

    def _get_node_and_kernel_name(self: any, dev_id: any, task_id: any,
                                  stream_id: any, err_time: any) -> tuple:
        data = self._get_node_and_kernel_name_execute_command()
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?device_id=\d+\s*,\s*stream_id=" \
                 r"%s\s*.+?\s*task_id=%s\s*,\s*fault kernel_name=" \
                 r"[-\d_]{0,}(\S+?),\s*func_name=(\S+)__kernel\d+" % (
                     stream_id, task_id)
        ret = re.findall(regexp, data, re.M | re.S)
        if len(ret) == 0:
            utils.print_warn_log(
                "There is no node name and kernel name for dev id(%s) "
                "task id(%s) stream id(%s) in plog."
                % (dev_id, task_id, stream_id))
            return '', ''

        if len(ret) > 1:
            max_i = self._get_the_latest_aicerr_form_ret(ret, err_time)
            return ret[max_i][1:]
        return ret[0][1:]

    def get_op_info(self: any) -> tuple:
        grep_cmd = ['grep', '<exception_print>TIME.*4060006', '-nr', '-A',
                    '120', self.collect_slog_path]
        status, data = utils.execute_command(grep_cmd)
        if status != 0:
            utils.print_error_log("Failed to execute command: %s." % " ".join(grep_cmd))
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        ret = re.findall(Constant.EXCEPTION_PATTERN, data, re.M | re.S)
        if len(ret) == 0:
            utils.print_info_log("No AIC_ERROR found.")
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        for device_aic_err in ret:
            if len(device_aic_err) != Constant.AIC_ERROR_TUPLE_LEN:
                utils.print_info_log("The AIC_ERROR is not complete.")
                raise utils.AicErrException(
                    Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
            log_time = device_aic_err[0]
            dev_id = device_aic_err[1]
            stream_id = device_aic_err[2]
            task_id = device_aic_err[3]
            err_time = utils.strplogtime(log_time)
            node_name, kernel_name = self._get_node_and_kernel_name(
                dev_id, task_id, stream_id, err_time)
            if node_name == '' and kernel_name == '':
                continue
            self.ai_core_error_list.append(device_aic_err)
            self.node_name_list.append(node_name)
            self.kernel_name_list.append(kernel_name)
        if len(self.ai_core_error_list) == 0:
            utils.print_error_log(
                "The AIC_ERROR of device does not match the host.")
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        return self.ai_core_error_list, self.node_name_list, self.kernel_name_list


class HostLogParser(LogParser):
    def _get_node_and_kernel_name_execute_command(self: any) -> any:
        grep_cmd = ['grep', 'PrintErrorInfo:.*?aicore kernel execute failed',
                    '-inrE', self.collect_applog_path]
        status, data = utils.execute_command(grep_cmd)
        if status != 0:
            utils.print_error_log("Failed to execute command: %s." % " ".join(grep_cmd))
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        return data

    @staticmethod
    def _get_the_latest_aicerr_form_ret(ret: list, err_time: any) -> int:
        max_i = -1
        max_time_obj = None
        for i, (time_str, _, _, _, _) in enumerate(ret):
            time_obj = utils.strplogtime(time_str)
            # 都找最迟的会找到同一个，加个条件时间要早于AICERROR时间，
            # 前提host、device时间同步。否则去掉and前的条件。
            if err_time >= time_obj and (
                    max_time_obj is None or time_obj > max_time_obj):
                max_time_obj = time_obj
                max_i = i
        if max_i == -1:
            for i, (time_str, _, _, _, _) in enumerate(ret):
                time_obj = utils.strplogtime(time_str)
                if max_time_obj is None or time_obj > max_time_obj:
                    max_time_obj = time_obj
                    max_i = i
        if max_i == -1:
            utils.print_error_log("Failed to get node and kernel name.")
            raise utils.AicErrException(Constant.MS_AICERR_FIND_DATA_ERROR)
        return max_i

    def _get_node_and_kernel_name(self: any, dev_id: any, err_time: any) -> tuple:
        data = self._get_node_and_kernel_name_execute_command()
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?device_id=\d+\s*,\s*stream_id=" \
                 r"(\d+)\s*.+?\s*task_id=(\d+)\s*,.*?fault kernel_name=" \
                 r"[-\d_]{0,}(\S+?),\s*func_name=(\S+),"
        ret = re.findall(regexp, data, re.M | re.S)
        if len(ret) == 0:
            utils.print_error_log(
                "There is no node name and kernel name for dev id(%s) in plog."
                % dev_id)
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)

        if len(ret) > 1:
            max_i = self._get_the_latest_aicerr_form_ret(ret, err_time)
            result = ret[max_i][1:]
        result = ret[0][1:]

        kernel_name_list = result[3].split('_')
        if "" in kernel_name_list:
            kernel_name_list.remove("")
        kernel_name_list = kernel_name_list[:-1]
        kernel_name = '_'.join(kernel_name_list)

        node_name = self._get_node_name_by_kernel_name(kernel_name)
        result_list = list(result)
        result_list[2] =  node_name
        result_list[3] = kernel_name
        return result_list

    def _get_node_name_by_kernel_name(self: any, kernel_name: any) -> str:
        """
        get node name by kernel name
        :param kernel_name:
        :return:  node_name  
        """
        node_name = ''
        aic_info_cmd = ['grep', '-r',  '-C', '7',  "\[AIC_INFO\] dev_func:{}".format(kernel_name),
                        self.collect_applog_path]
        _, aic_info = utils.execute_command(aic_info_cmd)
        aic_info_dev_func_regex = r"\[AIC_INFO\]\snode_name:(.*?),"
        aic_info_dev_func_ret = re.findall(aic_info_dev_func_regex, aic_info)
        if len(aic_info_dev_func_ret) == 0:
            utils.print_warn_log("Failed to get node name by kernel name.")
            return node_name
        node_name = aic_info_dev_func_ret[0]
        return node_name


    def _get_air_error_execute_command(self):
        grep_cmd = ['grep', 'PrintCoreErrorInfo:.*?there is an aicore error',
                    '-inrE', self.collect_applog_path]
        status, data = utils.execute_command(grep_cmd)
        if status != 0:
            utils.print_error_log("Failed to execute command: %s.Maybe rts break when report Core log to host." %
                                  " ".join(grep_cmd))
            raise utils.AicErrException(Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        return data

    @staticmethod
    def _get_aicerror_args(data):
        regexp = r"(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+).+?device\((\d+)\),.*?core id is (\d+),\s+error code = (\S+)," \
                 r".*?pc start:\s(\S+),\scurrent:\s(\S+),\svec error info:\s(\S+),\smte error info:\s(\S+)," \
                 r"\sifu error info:\s(\S+),\sccu error info:\s(\S+),\scube error info:\s(\S+)," \
                 r"\sbiu error info:\s(\S+),\saic error mask:\s(\S+),\spara base:\s(\S+)."
        ret = re.findall(regexp, data, re.M | re.S)
        if len(ret) == 0:
            utils.print_warn_log(
                "aic error info does not match in  plog \"aicore kernel execute failed\"")
            return None
        return ret

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

    def get_op_info(self: any) -> tuple:
        data = self._get_air_error_execute_command()
        ret = self._get_aicerror_args(data)
        for aic_err in ret:
            log_time = aic_err[0]
            dev_id = aic_err[1]
            err_time = utils.strplogtime(log_time)
            stream_id, task_id, node_name, kernel_name = self._get_node_and_kernel_name(
                dev_id, err_time)
            if node_name == '' and kernel_name == '':
                continue

            # 适配原开发过程中的device_aic_err
            device_aic_err = [None] * 9
            device_aic_err[0] = aic_err[0]  # err time
            device_aic_err[1] = aic_err[1]  # dev id
            device_aic_err[2] = stream_id  # stream id
            device_aic_err[3] = task_id  # task id
            device_aic_err[4] = aic_err[2]  # core id
            device_aic_err[5] = aic_err[3]  # aic error code
            device_aic_err[6] = aic_err[4]  # start pc
            device_aic_err[7] = self._get_extra_info(aic_err)  # extra_info
            device_aic_err[8] = aic_err[5]  # current pc

            self.ai_core_error_list.append(device_aic_err)
            self.node_name_list.append(node_name)
            self.kernel_name_list.append(kernel_name)
        if len(self.ai_core_error_list) == 0:
            utils.print_error_log(
                "The AIC_ERROR of device does not match the host.")
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
        return self.ai_core_error_list, self.node_name_list, self.kernel_name_list
