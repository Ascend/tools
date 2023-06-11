import os

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

    def get_input_tensor_name(self):
        return "actual_input_1"

    def get_resnet_dymshape_om_path(self):
        return os.path.join(TestCommonClass.base_path, self.model_name, "model", "pth_resnet50_dymshape.om")

    def test_infer_dynamicshape(self):
        device_id = 0
        options = aclruntime.session_options()
        input_tensor_name = self.get_input_tensor_name()
        model_path = self.get_resnet_dymshape_om_path()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # only need call this functon compare infer_simple
        session.set_dynamic_shape(input_tensor_name+":1,3,224,224")
        session.set_custom_outsize([10000])

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
        print(session.sumary())

    def test_infer_dynamicshape_case1(self):
        device_id = 0
        options = aclruntime.session_options()
        options.log_level = 1
        input_tensor_name = self.get_input_tensor_name()
        model_path = self.get_resnet_dymshape_om_path()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # only need call this functon compare infer_simple
        session.set_dynamic_shape(input_tensor_name+":4,3,224,224")
        session.set_custom_outsize([20000])

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
        print(session.sumary())

    def test_infer_dynamicshape_case2(self):
        device_id = 0
        options = aclruntime.session_options()
        input_tensor_name = self.get_input_tensor_name()
        model_path = self.get_resnet_dymshape_om_path()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # only need call this functon compare infer_simple
        session.set_dynamic_shape(input_tensor_name+":8,3,300,200")
        session.set_custom_outsize([80000])

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
        print(session.sumary())

    def test_infer_no_set_dynamicshape(self):
        device_id = 0
        options = aclruntime.session_options()
        input_tensor_name = self.get_input_tensor_name()
        model_path = self.get_resnet_dymshape_om_path()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        session.set_custom_outsize([10000])

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [session.get_outputs()[0].name]
        feeds = {session.get_inputs()[0].name: tensor}

        with pytest.raises(RuntimeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_no_set_outsize(self):
        device_id = 0
        options = aclruntime.session_options()
        input_tensor_name = self.get_input_tensor_name()
        model_path = self.get_resnet_dymshape_om_path()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # only need call this functon compare infer_simple
        session.set_dynamic_shape(input_tensor_name+":1,3,224,224")

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name ]
        feeds = { session.get_inputs()[0].name : tensor}

        with pytest.raises(RuntimeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_get_input_info(self):
        device_id = 0
        options = aclruntime.session_options()
        input_tensor_name = self.get_input_tensor_name()
        model_path = self.get_resnet_dymshape_om_path()
        session = aclruntime.InferenceSession(model_path, device_id, options)

        session.set_dynamic_shape(input_tensor_name+":1,3,112,112")
        session.set_custom_outsize([80000])
        basesize = session.get_inputs()[0].realsize

        session.set_dynamic_shape(input_tensor_name+":1,3,224,224")
        basesize1 = session.get_inputs()[0].realsize
        assert basesize1 == basesize*4

        session.set_dynamic_shape(input_tensor_name+":2,3,224,224")
        basesize2 = session.get_inputs()[0].realsize
        assert basesize2 == basesize1*2

        session.set_dynamic_shape(input_tensor_name+":8,3,224,224")
        basesize3 = session.get_inputs()[0].realsize
        assert basesize3 == basesize2*4
