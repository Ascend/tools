import json
import os
import shutil

import pytest
from test_common import TestCommonClass


class TestClass:
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
        self.model_name = "resnet50"

    def test_args_invalid_device_id(self):
        invalid_device_ids = [-2, 100]
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        for i, device_id in enumerate(invalid_device_ids):
            cmd = "{} --model {} --device {}".format(TestCommonClass.cmd_prefix, model_path, device_id)
            print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret != 0

    def test_args_invalid_model_path(self):
        model_path = "xxx_invalid.om"
        cmd = "{} --model {} --device {}".format(TestCommonClass.cmd_prefix, model_path,
                                                 TestCommonClass.default_device_id)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret != 0

    def test_args_invalid_acl_json(self):
        """
        non-existent acl.json file
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        acl_json_path = "xxx_invalid.json"
        cmd = "{} --model {} --device {} --acl_json_path {} ".format(TestCommonClass.cmd_prefix, model_path,
                                                                     TestCommonClass.default_device_id, acl_json_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret != 0

    def test_args_invalid_acl_json_2(self):
        """
        wrong acl.json file
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        json_dict = {"profiler": {"wrong": "on", "aicpu": "on", "output": "", "aic_metrics": ""}}
        acl_json_path = os.path.join(TestCommonClass.base_path, "acl.json")

        with open(acl_json_path, "w") as f:
            json.dump(json_dict, f, indent=4, separators=(", ", ": "), sort_keys=True)
        cmd = "{} --model {} --device {} --acl_json_path {} ".format(TestCommonClass.cmd_prefix, model_path,
                                                                     TestCommonClass.default_device_id, acl_json_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0

    def test_args_ok(self):
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        cmd = "{} --model {} --device {}".format(TestCommonClass.cmd_prefix, model_path,
                                                 TestCommonClass.default_device_id)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0

    def test_args_invalid_loop(self):
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        loops = [-3, 0]
        for _, loop_num in enumerate(loops):
            cmd = "{} --model {} --device {} --loop {}".format(TestCommonClass.cmd_prefix, model_path,
                                                               TestCommonClass.default_device_id, loop_num)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret != 0

    def test_args_loop_ok(self):
        """
        'cost :' log record num = warmup  + loop
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        loops = [3, 300]
        warmup_num = 1
        log_path = os.path.join(TestCommonClass.base_path, "log.txt")
        for _, loop_num in enumerate(loops):
            cmd = "{} --model {} --device {} --loop {} --debug True > {}".format(TestCommonClass.cmd_prefix, model_path,
                                                                                 TestCommonClass.default_device_id,
                                                                                 loop_num, log_path)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0

            try:
                cmd = "cat {} |grep 'cost :' | wc -l".format(log_path)
                outval = os.popen(cmd).read()
            except Exception as e:
                raise Exception("raise an exception: {}".format(e))

            assert int(outval) == (loop_num + warmup_num)

    def test_args_debug_ok(self):
        """
        debug log record num > 1
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        log_path = os.path.join(TestCommonClass.base_path, "log.txt")
        cmd = "{} --model {} --device {} --debug True > {}".format(TestCommonClass.cmd_prefix, model_path,
                                                                   TestCommonClass.default_device_id, log_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0

        try:
            cmd = "cat {} |grep '[DEBUG]' | wc -l".format(log_path)
            outval = os.popen(cmd).read()
        except Exception as e:
            raise Exception("raise an exception: {}".format(e))

        assert int(outval) > 1

    def test_args_profiler_ok(self):
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        output_path = os.path.join(TestCommonClass.base_path, self.model_name, "output")
        TestCommonClass.prepare_dir(output_path)
        profiler_path = os.path.join(output_path, "profiler")
        TestCommonClass.prepare_dir(output_path)

        cmd = "{} --model {} --device {} --profiler true --output {}".format(TestCommonClass.cmd_prefix, model_path,
                                                                        TestCommonClass.default_device_id, output_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        #assert ret == 139

        assert os.path.exists(profiler_path)

        paths = os.listdir(profiler_path)
        sampale_json_path = os.path.join(profiler_path, paths[0],
                                         "device_{}/sample.json".format(TestCommonClass.default_device_id))

        assert os.path.isfile(sampale_json_path)

    def test_args_dump_ok(self):
        """
        dump folder existed. and  a sub-folder named with the format of date and time
        dump
        `-- 20220805053931
            `-- 0
                `-- pth_resnet50_bs1    # to verify
                    `-- 1
                        |-- 0
                        |-- 1
                        |-- 2
                        |-- 3
                        |-- 4
                        `-- 5
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        output_path = os.path.join(TestCommonClass.base_path, self.model_name, "output")
        TestCommonClass.prepare_dir(output_path)
        dump_path = os.path.join(output_path, "dump")

        cmd = "{} --model {} --device {} --dump true --output {}".format(TestCommonClass.cmd_prefix, model_path,
                                                                    TestCommonClass.default_device_id, output_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0
        assert os.path.exists(dump_path)
        base = os.path.basename(model_path)
        test_model_name = os.path.splitext(base)[0]
        paths = os.listdir(dump_path)
        dump_model_path = os.path.join(dump_path, paths[0], "{}".format(TestCommonClass.default_device_id),
                                       test_model_name)
        assert os.path.exists(dump_model_path)

    def test_args_output_ok(self):
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        output_path = os.path.join(TestCommonClass.base_path, self.model_name, "output")
        log_path = os.path.join(output_path, "log.txt")
        TestCommonClass.prepare_dir(output_path)
        cmd = "{} --model {} --device {}  --output {} > {}".format(TestCommonClass.cmd_prefix, model_path,
                                                               TestCommonClass.default_device_id, output_path, log_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0

        try:
            cmd = "cat {} |grep 'output path'".format(log_path)
            outval = os.popen(cmd).read()
        except Exception as e:
            raise Exception("grep action raises an exception: {}".format(e))

        result_path = os.path.join(output_path, outval.split(':')[1].replace('\n', ''))
        bin_path = os.path.join(result_path, "pure_infer_data_0.bin")
        assert os.path.exists(bin_path)
        os.remove(log_path)
        shutil.rmtree(result_path)

    def test_args_acljson_ok(self):
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        output_path = os.path.join(TestCommonClass.base_path, self.model_name, "output")
        TestCommonClass.prepare_dir(output_path)
        profiler_path = os.path.join(output_path, "profiler")
        TestCommonClass.prepare_dir(profiler_path)
        output_json_dict = {"profiler": {"switch": "on", "aicpu": "on", "output": "", "aic_metrics": ""}}
        output_json_dict["profiler"]["output"] = profiler_path
        out_json_file_path = os.path.join(TestCommonClass.base_path, "acl.json")

        with open(out_json_file_path, "w") as f:
            json.dump(output_json_dict, f, indent=4, separators=(", ", ": "), sort_keys=True)
        cmd = "{} --model {} --device {} --acl_json_path {} --output {}".format(TestCommonClass.cmd_prefix, model_path,
                                                                                TestCommonClass.default_device_id,
                                                                                out_json_file_path, output_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert os.path.exists(profiler_path)

        paths = os.listdir(profiler_path)
        assert len(paths) == 1
        sampale_json_path = os.path.join(profiler_path, paths[0],
                                         "device_{}/sample.json".format(TestCommonClass.default_device_id))

        assert os.path.isfile(sampale_json_path)

    def test_args_default_outfmt_ok(self):
        """test default output file suffix case
        there are two output files and one file with bin suffix in output folder path.
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        output_path = os.path.join(TestCommonClass.base_path, self.model_name, "output")
        TestCommonClass.prepare_dir(output_path)
        log_path = os.path.join(output_path, "log.txt")

        cmd = "{} --model {} --device {} --output {} > {}".format(TestCommonClass.cmd_prefix, model_path,
                                                             TestCommonClass.default_device_id,
                                                             output_path, log_path)
        print("run cmd:{}".format(cmd))
        ret = os.system(cmd)
        assert ret == 0

        try:
            cmd = "cat {} |grep 'output path'".format(log_path)
            outval = os.popen(cmd).read()
        except Exception as e:
            raise Exception("grep action raises an exception: {}".format(e))

        result_path = os.path.join(output_path, outval.split(':')[1].replace('\n', ''))
        bin_path = os.path.join(result_path, "pure_infer_data_0.bin")
        assert os.path.exists(bin_path)
        os.remove(log_path)
        shutil.rmtree(result_path)

    def test_args_outfmt_ok(self):
        """test supported output file suffix cases
        there are two output files and one file with given suffix in output folder path.
        2022_08_05-10_37_41
        |    |-- pure_infer_data_0.bin
        `-- 2022_08_05-10_37_41_summary.json
        """
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)

        output_file_suffixs = ["NPY", "BIN", "TXT"]

        for _, output_file_suffix in enumerate(output_file_suffixs):
            output_path = os.path.join(TestCommonClass.base_path, self.model_name, "output")
            log_path = os.path.join(output_path, "log.txt")
            TestCommonClass.prepare_dir(output_path)
            cmd = "{} --model {} --device {} --output {} --outfmt {} > {}".format(TestCommonClass.cmd_prefix,
                                                                             model_path,
                                                                             TestCommonClass.default_device_id,
                                                                             output_path, output_file_suffix, log_path)
            print("run cmd:{}".format(cmd))
            ret = os.system(cmd)
            assert ret == 0

            try:
                cmd = "cat {} |grep 'output path'".format(log_path)
                outval = os.popen(cmd).read()
            except Exception as e:
                raise Exception("grep action raises an exception: {}".format(e))

            result_path = os.path.join(output_path, outval.split(':')[1].replace('\n', ''))

            suffix_file_path = os.path.join(result_path, "pure_infer_data_0.{}".format(output_file_suffix.lower()))
            assert os.path.exists(suffix_file_path)
            shutil.rmtree(result_path)


if __name__ == '__main__':
    pytest.main(['test_args.py', '-vs'])
