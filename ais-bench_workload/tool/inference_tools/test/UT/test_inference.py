import os
import sys
import numpy as np
import aclruntime
import pytest

class TestClass:
    def get_input_tensor_name(self):
        return "actual_input_1"

    def get_resnet_static_om_path(self, batchsize):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/resnet50_bs{}.om".format(batchsize))

    def get_resnet_dymbatch_om_path(self):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/resnet50_dymbatch.om")

    def get_resnet_dymhw_om_path(self):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/resnet50_dymhw.om")

    def get_resnet_dymdims_om_path(self):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/resnet50_dymdims.om")

    def get_resnet_dymshape_om_path(self):
        _current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(_current_dir, "../testdata/resnet50_dymshape.om")

    def test_infer_runcase_dict(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name ]
        feeds = { session.get_inputs()[0].name : tensor}

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_runcase_list(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name ]
        feeds = [ tensor ]

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_runcase_empty_outputname(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ ]
        feeds = [ tensor ]

        outputs = session.run(outnames, feeds)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_runcase_none_outputname(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = None
        feeds = [ tensor ]

        with pytest.raises(TypeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_runcase_split(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name ]
        feeds = { session.get_inputs()[0].name : tensor}

        session.run_setinputs(feeds)
        session.run_execute()
        outputs = session.run_getoutputs(outnames)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_runcase_split_list(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name ]
        feeds = [ tensor ]

        session.run_setinputs(feeds)
        session.run_execute()
        outputs = session.run_getoutputs(outnames)
        print("outputs:", outputs)

        for out in outputs:
            out.to_host()
        print(session.sumary())

    def test_infer_invalid_input_size(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize+128)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name ]
        feeds = { session.get_inputs()[0].name : tensor}

        with pytest.raises(RuntimeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_invalid_input_type(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)

        outnames = [ session.get_outputs()[0].name ]
        feeds = { session.get_inputs()[0].name : ndata}

        with pytest.raises(TypeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_invalid_outname(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)

        outnames = [ session.get_outputs()[0].name + "xxx" ]
        feeds = { session.get_inputs()[0].name : tensor}

        with pytest.raises(RuntimeError) as e:
            outputs = session.run(outnames, feeds)
            print("outputs:", outputs)

    def test_infer_invalid_device_id(self):
        device_id = 0
        options = aclruntime.session_options()
        model_path = self.get_resnet_static_om_path(1)
        session = aclruntime.InferenceSession(model_path, device_id, options)

        # create new numpy data according inputs info
        barray = bytearray(session.get_inputs()[0].realsize)
        ndata = np.frombuffer(barray)
        # convert numpy to pytensors in device
        tensor = aclruntime.Tensor(ndata)
        with pytest.raises(RuntimeError) as e:
            tensor.to_device(device_id+100)