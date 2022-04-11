import ast
import os
import re
import shutil
import time
import numpy as np
import json
from sympy import Sum
from ms_interface import utils
from ms_interface.constant import Constant
from ms_interface.single_op_test_frame.ut import OpUT


class SingleOpCase:

    @staticmethod
    def _str2Hump(text):
        """
        下划线转大驼峰
        """
        arr = filter(None, text.lower().split('_'))
        res = ''
        for i in arr:
            res = res + i[0].upper() + i[1:]
        return res

    def __init__(self, collection, output_path, collect_time) -> None:
        self.collection = collection
        self.output_path = output_path
        self.collect_time = collect_time

    def _get_op_param(self, kernel_name) -> list:
        get_param_cmd = [
            'grep', f'BuildSingleOp Prebuilding op: kernelName\[{kernel_name}\]', '-hr', '-A', '3',
            self.collection.collect_applog_path
        ]
        _, get_param_data = utils.execute_command(get_param_cmd)
        purified_data = re.sub(r"\[INFO\].*?\[fusion_op.cc:\d+?\].*?\s", "", get_param_data)
        purified_data = re.sub(r"[\n]", "", purified_data)
        get_param_regexp = r"op inputs:\s*\((.*?)\),\s*outputs:\s*\((.*?)\),\s*attrs:\s*\((.*?)\)\."
        get_param_ret = re.findall(get_param_regexp, purified_data, re.M)
        if len(get_param_ret) == 0:
            utils.print_error_log(f"Fail to get op params of kernel [{kernel_name}] in host log .")
            raise utils.AicErrException(Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
        input_str, output_str, attr_str = get_param_ret[0]

        result_list = []
        input_list = ast.literal_eval("[" + input_str + "]")
        for (index, input_item) in enumerate(input_list):
            input_item["param_type"] = "input"
            input_item["run_shape"] = input_item.get("shape")
            data_file = os.path.join(self.collection.collect_dump_path,
                                     ".".join([kernel_name, "input", str(index), "npy"]))

            input_item["value"] = np.load(data_file)
            x_range = []
            for i in input_item.get("shape"):
                x_range.append((i, i))
            input_item["range"] = x_range
        result_list.extend(input_list)

        output_list = ast.literal_eval("[" + output_str + "]")
        for output_item in output_list:
            output_item["param_type"] = "output"
            output_item["run_shape"] = output_item.get("shape")
            y_range = []
            for i in output_item.get("shape"):
                y_range.append((i, i))
            output_item["range"] = y_range
        result_list.extend(output_list)

        attr_list_ori = ast.literal_eval("[" + attr_str + "]")
        for attr_item in attr_list_ori:
            if isinstance(attr_item, dict):
                result_list.append(attr_item.get("value"))
        return result_list

    def _get_module_str(self, kernel_name) -> str:
        get_module_cmd = ['grep', rf'kernel\[{kernel_name}\].*module\[', '-hr', self.collection.collect_applog_path]
        _, get_module_data = utils.execute_command(get_module_cmd)
        get_module_regexp = rf"kernel\[{kernel_name}\].*?module\[(.*?)\]"
        get_module_ret = re.findall(get_module_regexp, get_module_data, re.M)
        if len(get_module_ret) == 0:
            utils.print_error_log(f"Fail to get op module of kernel [{kernel_name}] in host log .")
            raise utils.AicErrException(Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
        return get_module_ret[0]

    def _get_tiling_info(self, kernel_name) -> list:
        aic_info_cmd = [
            'grep', '-r', '-C', '7', "\[AIC_INFO\] dev_func:{}".format(kernel_name), self.collection.collect_applog_path
        ]
        _, aic_info = utils.execute_command(aic_info_cmd)

        aic_info_blockdim_regexp = r"\[AIC_INFO\]\sblock_dim:(\d+)"
        aic_info_blockdim_ret = re.findall(aic_info_blockdim_regexp, aic_info, re.M)
        if len(aic_info_blockdim_ret) == 0:
            utils.print_warn_log(f"Failed to get {aic_info_blockdim_regexp}")
        elif len(aic_info_blockdim_ret[0]) == 0:
            utils.print_info_log(f"get {aic_info_blockdim_regexp} is null")
            block_dim = ""
        else:
            block_dim = int(aic_info_blockdim_ret[0][0])

        aic_info_tiling_data_regex = r"\[AIC_INFO\]\stiling_data:(.*?)"
        aic_info_tiling_data_ret = re.findall(aic_info_tiling_data_regex, aic_info, re.M)
        if len(aic_info_tiling_data_ret) == 0:
            utils.print_warn_log(f"Failed to get {aic_info_tiling_data_regex}")
        elif len(aic_info_tiling_data_ret[0]) == 0:
            utils.print_info_log(f"get {aic_info_tiling_data_regex} is null")
            tiling_data = ""
        else:
            tiling_data = bytes(aic_info_tiling_data_ret[0][0], encoding="utf-8")

        return (block_dim, tiling_data)

    def _get_op_impl_type(self, params: list, module_name: str) -> str:
        has_dynamic_shape = False
        for para_item in params:
            if not isinstance(para_item, dict) or para_item.get("param_type") != "input":
                continue
            for i in para_item.get("shape"):
                if i < 0:
                    has_dynamic_shape = True
                    break
            if has_dynamic_shape:
                break

        if ".dynamic." in module_name:
            if has_dynamic_shape:
                return "dynamic"
            else:
                return "static"
        else:
            if has_dynamic_shape:
                utils.print_error_log("There is dynamic shape in param, but call static impl")
                raise utils.AicErrException(Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
            else:
                return "pre-static"

    def _get_summary_path(self, i):
        err_time = self.collection.ai_core_error_list[i][0]
        err_time_obj = utils.strplogtime(err_time)
        err_i_folder_name = "aicerror_%d_%s" % (i, time.strftime("%Y%m%d%H%M%S", err_time_obj.timetuple()))
        err_i_folder = os.path.join(self.output_path, err_i_folder_name)
        return err_i_folder

    def _add_summary_to_info(self, err_i_folder, result, test_case_file):
        info_file = os.path.join(err_i_folder, "info.txt")
        single_op_result = f"""
***********************7. result of single_op_test*************************
{result}
Running single op test \"python3 {test_case_file}\" can reprocessing."
"""
        utils.write_file(info_file, single_op_result, "a")
        utils.print_info_log(f"Write summary {info_file}")

    def _gen_single_op(self, sum_path, op_case: OpUT, test_case: dict, kernel_name):
        i = 0
        for param in test_case.get("params"):
            if isinstance(param, dict) and param.get("param_type") == "input":

                npy_file = ".".join([kernel_name, "input", str(i), "npy"])
                param["value"] = f'start_flag_np.load(os.path.join(dump_path, "{npy_file}"))_end_flag'
                i += 1
        test_case["bin_path"] = f'start_flag_os.path.join(compile_path, "{kernel_name}.o")_end_flag'
        test_case_str = json.dumps(test_case, indent=4)
        test_case_str = test_case_str.replace("\"start_flag_", "").replace("_end_flag\"", "").replace("\\\"","\"")
        template_file = """
import os
import numpy as np
from ms_interface.single_op_test_frame.ut import OpUT

def run_sample_case():
    file_path = os.path.dirname(__file__)
    info_path = os.path.dirname(os.path.dirname(file_path))
    dump_path = os.path.join(info_path, "collection", "dump")
    compile_path = os.path.join(info_path, "collection", "compile", "kernel_meta")

    op_case = OpUT("{op_type}", "{op_module}", "{func_name}")
    test_case = {test_case}
    op_case.add_direct_case(test_case)
    op_case.run()

if __name__ == '__main__':
    run_sample_case()
""".format(op_type=str(op_case.op_type),
           op_module=str(op_case.op_module_name),
           func_name=str(op_case.op_func_name),
           test_case=str(test_case_str))
        test_case_dir = os.path.join(sum_path, "single_op_test")
        if not os.path.exists(test_case_dir):
            os.makedirs(test_case_dir)
        test_case_file = os.path.join(test_case_dir, test_case.get("case_name") + ".py")
        utils.write_file(test_case_file, template_file)
        src_frame_dir = os.path.join(os.path.dirname(__file__), "single_op_test_frame")

        dst_parent_dir = os.path.join(test_case_dir, "ms_interface")
        if not os.path.exists(dst_parent_dir):
            os.makedirs(dst_parent_dir)
        dst_frame_dir = os.path.join(dst_parent_dir, "single_op_test_frame")

        shutil.copytree(src_frame_dir, dst_frame_dir)
        utils.print_info_log(f"op test case created! Test command \"python3 {test_case_file}\"")
        return test_case_file

    def run(self) -> bool:
        """
        run single op case
        """

        for i, aicerr_kernel in enumerate(self.collection.kernel_name_list):
            params = self._get_op_param(kernel_name=aicerr_kernel)
            op_module = self._get_module_str(kernel_name=aicerr_kernel)
            op_imply_type = self._get_op_impl_type(params, op_module)
            op_type = self._str2Hump(op_module.split(".")[-1])
            bin_path = os.path.join(self.collection.collect_compile_path, 'kernel_meta')
            block_dim, tiling_data = self._get_tiling_info(kernel_name=aicerr_kernel)
            utils.print_info_log(f"Create op case\nop_type:{op_type}\nop_module:{op_module}\nparams:{params}")

            op_case = OpUT(op_type, op_module, None)
            test_case = {
                "params": params,
                "case_name": aicerr_kernel + "_test",
                "bin_path": os.path.join(bin_path, aicerr_kernel + ".o"),
                "op_imply_type": op_imply_type,
                "block_dim": block_dim,
                "tiling_data": tiling_data
            }
            op_case.add_direct_case(test_case)
            result = op_case.run()
            sum_path = self._get_summary_path(i)
            case_file = self._gen_single_op(sum_path, op_case, test_case, aicerr_kernel)
            
            self._add_summary_to_info(sum_path, result, case_file)