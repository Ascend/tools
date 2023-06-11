#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import math
import os
import shutil

import aclruntime
import pytest
from test_common import TestCommonClass


class TestClass():
    @classmethod
    def setup_class(cls):
        """
        class level setup_class
        """
        cls.init(TestClass)

    @classmethod
    def teardown_class(cls):
        print('\n ---class level teardown_class')

    def init(self):
        self.model_name = self.get_model_name(self)
        self.model_base_path = self.get_model_base_path(self)
        self.output_file_num = 5

    def get_model_name(self):
        return "yolov3"

    def get_model_base_path(self):
        """
        supported model names as yolo, resnet50, resnet101,...。folder struct as follows
        testdata
         └── yolo   # model base
            ├── input
            ├── model
            └── output
        """
        return os.path.join(TestCommonClass.base_path, self.model_name)

    def get_dynamic_batch_om_path(self):
        return os.path.join(self.model_base_path, "model", "pth_yolov3_dymbatch.om")

    def get_dynamic_dim_om_path(self):
        return os.path.join(self.model_base_path, "model", "pth_yolov3_dymdim.om")

    def get_dynamic_wh_om_path(self):
        return os.path.join(self.model_base_path, "model", "pth_yolov3_dymwh.om")

    def test_pure_inference_normal_static_batch(self):
        """
        batch size 1,2,4,8
        """
        batch_list = [1, 2, 4, 8]

        for _, batch_size in enumerate(batch_list):
            model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
            cmd = "{} --model {} --device {}".format(TestCommonClass.cmd_prefix, model_path,
                                                     TestCommonClass.default_device_id)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0

    def test_pure_inference_normal_dynamic_batch(self):
        batch_list = [1, 2, 4, 8, 16]
        model_path = self.get_dynamic_batch_om_path()
        for _, dys_batch_size in enumerate(batch_list):
            cmd = "{} --model {} --device {} --dymBatch {}".format(TestCommonClass.cmd_prefix, model_path, TestCommonClass.default_device_id,
                                                                dys_batch_size)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0

    def test_general_inference_normal_static_batch(self):
        batch_size = 1
        static_model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
        input_size = TestCommonClass.get_model_inputs_size(static_model_path)[0]
        input_path = TestCommonClass.get_inputs_path(input_size, os.path.join(self.model_base_path, "input"),
                                                     self.output_file_num)
        batch_list = [1, 2, 4, 8, 16]
        base_output_path = os.path.join(self.model_base_path, "output")
        output_paths = []

        for i, batch_size in enumerate(batch_list):
            model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
            output_dirname = "{}_{}".format("static_batch", i)
            tmp_output_path = os.path.join(base_output_path, output_dirname)
            if os.path.exists(tmp_output_path):
                shutil.rmtree(tmp_output_path)
            os.makedirs(tmp_output_path)
            cmd = "{} --model {} --device {} --input {} --output {} --output_dirname {}".format(TestCommonClass.cmd_prefix, model_path,
                TestCommonClass.default_device_id, input_path, base_output_path, output_dirname)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0
            output_bin_file_num = len(os.listdir(tmp_output_path))
            assert(output_bin_file_num == 3 * self.output_file_num)
            output_paths.append(tmp_output_path)

        # compare different batchsize inference bin files
        base_compare_path = output_paths[0]
        for i, cur_output_path in enumerate(output_paths):
            if i == 0:
                continue
            cmd = "diff {}  {}".format(base_compare_path, cur_output_path)
            ret = os.system(cmd)
            assert ret == 0

        for output_path in output_paths:
            shutil.rmtree(output_path)

    def test_general_inference_normal_dynamic_batch(self):
        batch_size = 1
        static_model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
        input_size = TestCommonClass.get_model_inputs_size(static_model_path)[0]
        input_path = TestCommonClass.get_inputs_path(input_size, os.path.join(self.model_base_path, "input"),
                                                     self.output_file_num)
        batch_list = [1, 2, 4, 8, 16]
        base_output_path = os.path.join(self.model_base_path, "output")
        output_paths = []

        model_path = self.get_dynamic_batch_om_path()

        for i, dys_batch_size in enumerate(batch_list):
            output_dirname = "{}_{}".format("static_batch", i)
            tmp_output_path = os.path.join(base_output_path, output_dirname)
            if os.path.exists(tmp_output_path):
                shutil.rmtree(tmp_output_path)
            os.makedirs(tmp_output_path)
            cmd = "{} --model {} --device {} --input {} --output {} --output_dirname {} --dymBatch {}".format(TestCommonClass.cmd_prefix, model_path,
                TestCommonClass.default_device_id, input_path, base_output_path, output_dirname, dys_batch_size)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0
            output_bin_file_num = len(os.listdir(tmp_output_path))
            assert(output_bin_file_num == 3 * self.output_file_num)
            output_paths.append(tmp_output_path)

        # compare different batchsize inference bin files
        base_compare_path = output_paths[0]
        for i, cur_output_path in enumerate(output_paths):
            if i == 0:
                continue
            cmd = "diff {}  {}".format(base_compare_path, cur_output_path)
            ret = os.system(cmd)
            assert ret == 0

        for output_path in output_paths:
            shutil.rmtree(output_path)

    def test_general_inference_prformance_comparison_with_msame_static_batch(self):
        batch_size = 1
        input_file_num = 100
        static_model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
        input_size = TestCommonClass.get_model_inputs_size(static_model_path)[0]
        input_path = TestCommonClass.get_inputs_path(input_size, os.path.join(self.model_base_path, "input"),
                                                     input_file_num)

        output_path = os.path.join(self.model_base_path, "output")
        output_paths = []

        model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
        output_dir_name = "static_batch"
        output_dir_path = os.path.join(output_path, output_dir_name)
        if os.path.exists(output_dir_path):
            shutil.rmtree(output_dir_path)
        os.makedirs(output_dir_path)
        summary_json_path = os.path.join(output_path,  "{}_summary.json".format(output_dir_name))
        cmd = "{} --model {} --device {} --input {} --output {} --output_dirname {}".format(TestCommonClass.cmd_prefix, model_path,
            TestCommonClass.default_device_id, input_path, output_path, output_dir_name)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0

        with open(summary_json_path,'r',encoding='utf8') as fp:
            json_data = json.load(fp)
            ais_bench_inference_time_ms = json_data["NPU_compute_time"]["mean"]

        assert math.fabs(ais_bench_inference_time_ms) > TestCommonClass.EPSILON

        output_bin_file_num = len(os.listdir(output_dir_path))
        assert(output_bin_file_num == 3 * input_file_num)

        # get msame inference  average time without first time
        msame_infer_log_path = os.path.join(output_path, output_dir_name, "msame_infer.log")
        cmd = "{} --model {} --input {} > {}".format(TestCommonClass.msame_bin_path, model_path, input_path, msame_infer_log_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0
        assert os.path.exists(msame_infer_log_path)

        msame_inference_time_ms = 0
        with open(msame_infer_log_path) as f:
            for line in f:
                if "Inference average time without first time" not in line:
                    continue

                sub_str = line[(line.rfind(':') + 1):]
                sub_str = sub_str.replace('ms\n','')
                msame_inference_time_ms = float(sub_str)

        assert math.fabs(msame_inference_time_ms) > TestCommonClass.EPSILON
        # compare
        allowable_performance_deviation = 0.01
        assert math.fabs(msame_inference_time_ms - ais_bench_inference_time_ms)/msame_inference_time_ms < allowable_performance_deviation
        os.remove(msame_infer_log_path)
        shutil.rmtree(output_dir_path)

    def test_general_inference_batchsize_is_none_normal_static_batch(self):
        batch_list = [1, 2, 4, 8, 16]
        output_parent_path = os.path.join(self.model_base_path, "output")
        output_paths = []
        summary_paths = []

        for i, batch_size in enumerate(batch_list):
            model_path = TestCommonClass.get_model_static_om_path(batch_size, self.model_name)
            output_dirname = "{}_{}".format("static_batch", i)
            output_path = os.path.join(output_parent_path, output_dirname)
            log_path = os.path.join(output_path, "log.txt")
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            os.makedirs(output_path)
            summary_json_path = os.path.join(output_parent_path,  "{}_summary.json".format(output_dirname))
            cmd = "{} --model {} --device {}  --output {} --output_dirname {} > {}".format(TestCommonClass.cmd_prefix, model_path,
                TestCommonClass.default_device_id, output_parent_path, output_dirname, log_path)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0

            output_paths.append(output_path)
            summary_paths.append(summary_json_path)

            with open(log_path) as f:
                for line in f:
                    if "1000*batchsize" not in line:
                        continue

                    sub_str = line.split('/')[0].split('(')[1].strip(')')
                    cur_batchsize = int(sub_str)
                    assert batch_size == cur_batchsize
                    break

        for output_path in output_paths:
            shutil.rmtree(output_path)
        for summary_path in summary_paths:
            os.remove(summary_path)

    def test_pure_inference_batchsize_is_none_normal_dynamic_batch(self):
        batch_list = [1, 2, 4, 8, 16]
        output_parent_path = os.path.join(self.model_base_path, "output")
        output_paths = []
        summary_paths = []

        model_path = self.get_dynamic_batch_om_path()

        for i, dys_batch_size in enumerate(batch_list):
            output_dirname = "{}_{}".format("dynamic_batch", i)
            output_path = os.path.join(output_parent_path, output_dirname)
            log_path = os.path.join(output_path, "log.txt")
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            os.makedirs(output_path)
            summary_json_path = os.path.join(output_parent_path,  "{}_summary.json".format(output_dirname))
            cmd = "{} --model {} --device {} --output {} --output_dirname {} --dymBatch {} > {}".format(TestCommonClass.cmd_prefix, model_path,
                TestCommonClass.default_device_id, output_parent_path, output_dirname, dys_batch_size, log_path)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0
            output_paths.append(output_path)
            summary_paths.append(summary_json_path)

            with open(log_path) as f:
                for line in f:
                    if "1000*batchsize" not in line:
                        continue

                    sub_str = line.split('/')[0].split('(')[1].strip(')')
                    cur_batchsize = int(sub_str)
                    assert dys_batch_size == cur_batchsize
                    break

        for output_path in output_paths:
            shutil.rmtree(output_path)
        for summary_path in summary_paths:
            os.remove(summary_path)

    def test_pure_inference_batchsize_is_none_normal_dynamic_dim(self):
        dym_dims = ["images:1,3,224,224", "images:8,3,448,448"]
        batch_list = [1, 8]
        output_parent_path = os.path.join(self.model_base_path, "output")
        output_paths = []
        summary_paths = []

        model_path = self.get_dynamic_dim_om_path()

        for i, dym_dim in enumerate(dym_dims):
            output_dirname = "{}_{}".format("dim_batch", i)
            output_path = os.path.join(output_parent_path, output_dirname)
            log_path = os.path.join(output_path, "log.txt")
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            os.makedirs(output_path)
            summary_json_path = os.path.join(output_parent_path,  "{}_summary.json".format(output_dirname))
            cmd = "{} --model {} --device {} --output {} --output_dirname {} --dymDims {} > {}".format(TestCommonClass.cmd_prefix, model_path,
                TestCommonClass.default_device_id, output_parent_path, output_dirname, dym_dim, log_path)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0
            output_paths.append(output_path)
            summary_paths.append(summary_json_path)

            with open(log_path) as f:
                for line in f:
                    if "1000*batchsize" not in line:
                        continue

                    sub_str = line.split('/')[0].split('(')[1].strip(')')
                    cur_batchsize = int(sub_str)
                    assert batch_list[i] == cur_batchsize
                    break

        for output_path in output_paths:
            shutil.rmtree(output_path)
        for summary_path in summary_paths:
            os.remove(summary_path)

    def test_pure_inference_batchsize_is_none_normal_dynamic_wh(self):
        hw_list = ["224,224", "448,448"]
        batch_list = [1, 1]
        output_parent_path = os.path.join(self.model_base_path, "output")
        output_paths = []
        summary_paths = []

        model_path = self.get_dynamic_wh_om_path()

        for i, dym_wh in enumerate(hw_list):
            output_dirname = "{}_{}".format("wh_batch", i)
            output_path = os.path.join(output_parent_path, output_dirname)
            log_path = os.path.join(output_path, "log.txt")
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            os.makedirs(output_path)
            summary_json_path = os.path.join(output_parent_path,  "{}_summary.json".format(output_dirname))
            cmd = "{} --model {} --device {} --output {} --output_dirname {} --dymHW {} > {}".format(TestCommonClass.cmd_prefix, model_path,
                TestCommonClass.default_device_id, output_parent_path, output_dirname, dym_wh, log_path)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0
            output_paths.append(output_path)
            summary_paths.append(summary_json_path)

            with open(log_path) as f:
                for line in f:
                    if "1000*batchsize" not in line:
                        continue

                    sub_str = line.split('/')[0].split('(')[1].strip(')')
                    cur_batchsize = int(sub_str)
                    assert batch_list[i] == cur_batchsize
                    break

        for output_path in output_paths:
            shutil.rmtree(output_path)
        for summary_path in summary_paths:
            os.remove(summary_path)

if __name__ == '__main__':
    pytest.main(['test_infer_yolov3.py', '-vs'])
