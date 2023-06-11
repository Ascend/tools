import aclruntime
import numpy as np
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
        device_id = 100
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        options = aclruntime.session_options()
        with pytest.raises(RuntimeError) as e:
            aclruntime.InferenceSession(model_path, device_id, options)
            print("when device_id invalid error msg is %s", e)

    def test_args_invalid_model_path(self):
        device_id = 0
        model_path = "xxx_invalid.om"
        options = aclruntime.session_options()
        with pytest.raises(RuntimeError) as e:
            aclruntime.InferenceSession(model_path, device_id, options)
            print("when om_path invalid error msg is %s", e)

    ## 待完善 增加 loopo 和 log_level的校验和判断 当前不完善

    # def test_args_invalid_acl_json(self):
    #     device_id = 0
    #     model_path = self.get_base_om_path()
    #     options = aclruntime.session_options()

    #     options.acl_json_path="xxx.invalid.json"
    #     with pytest.raises(RuntimeError) as e:
    #         aclruntime.InferenceSession(model_path, device_id, options)
    #         print("when acl.json invalid error msg is %s", e)

    def test_args_ok(self):
        device_id = 0
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        options = aclruntime.session_options()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [session.get_outputs()[0].name]
        feeds = {session.get_inputs()[0].name: tensor}

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        # summary inference throughput
        print(session.sumary())
