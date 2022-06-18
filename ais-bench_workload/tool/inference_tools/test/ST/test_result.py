import os
import sys
import os
import pytest

class TestClass:
    def get_cmd_prefix(self):
        return sys.executable + " ../../frontend/main.py"

    def get_resnet_static_om_path(self, batchsize):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/resnet50_bs{}.om".format(batchsize))

    def test_args_ok(self):
        device_id = 0
        model_path = self.get_resnet_static_om_path(1)
        cmd = "{} --model {} --device_id {}".format(self.get_cmd_prefix(), model_path, device_id)
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        cmd = "{} --output {}".format(cmd, _current_dir)
        ret = os.system(cmd)
        assert ret == 0