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

    def test_infer_runcase_dict(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
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
        print(session.sumary())

    def test_infer_runcase_list(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [session.get_outputs()[0].name]
        feeds = [tensor]

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_runcase_empty_outputname(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = []
        feeds = [tensor]

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_runcase_none_outputname(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = None
        feeds = [tensor]

        with pytest.raises(TypeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_runcase_split(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
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
        print(session.sumary())

    def test_infer_runcase_split_list(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [session.get_outputs()[0].name]
        feeds = [tensor]

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_invalid_input_size(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize+128)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [session.get_outputs()[0].name]
        feeds = {session.get_inputs()[0].name: tensor}

        with pytest.raises(RuntimeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_invalid_input_type(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)

        outnames = [session.get_outputs()[0].name]
        feeds = {session.get_inputs()[0].name: ndata}

        with pytest.raises(TypeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_invalid_outname(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [session.get_outputs()[0].name + "xxx"]
        feeds = {session.get_inputs()[0].name: tensor}

        with pytest.raises(RuntimeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_invalid_device_id(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = TestCommonClass.get_model_static_om_path(1, self.model_name)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        with pytest.raises(RuntimeError) as e:
            tensor.to_device(device_id+100)
