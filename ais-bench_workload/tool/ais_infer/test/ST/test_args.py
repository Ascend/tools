import os
import sys
import os
import pytest

class TestClass:
    def get_cmd_prefix(self):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return sys.executable + " " + os.path.join(_current_dir, " ../../ais_infer.py")

    def get_resnet_static_om_path(self, batchsize):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/pth_resnet50_bs{}.om".format(batchsize))

    def test_args_invalid_device_id(self):
        device_id = 100
        model_path = self.get_resnet_static_om_path(1)
        cmd = "{} --model {} --device_id {}".format(self.get_cmd_prefix(), model_path, device_id)
        ret = os.system(cmd)
        assert ret != 0

    def test_args_invalid_model_path(self):
        device_id = 0
        model_path = "xxx_invalid.om"
        cmd = "{} --model {} --device_id {}".format(self.get_cmd_prefix(), model_path, device_id)
        ret = os.system(cmd)
        assert ret != 0

    def test_args_invalid_acl_json(self):
        device_id = 0
        model_path = self.get_resnet_static_om_path(1)
        acl_json_path="xxx_invalid.json"
        cmd = "{} --model {} --device_id {}".format(self.get_cmd_prefix(), model_path, device_id)
        cmd = "{} --acl_json_path {}".format(cmd, acl_json_path)
        ret = os.system(cmd)
        assert ret != 0

    def test_args_ok(self):
        device_id = 0
        model_path = self.get_resnet_static_om_path(1)
        cmd = "{} --model {} --device_id {}".format(self.get_cmd_prefix(), model_path, device_id)
        ret = os.system(cmd)
        assert ret == 0