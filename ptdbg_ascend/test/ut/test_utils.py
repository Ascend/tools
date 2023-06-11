import unittest
import ptdbg_ascend.common.utils as utils


class TestUtilsMethods(unittest.TestCase):
    def test_get_api_name_from_matcher(self):
        normal_name = "Functional_relu__1_output"
        unusual_name = "Functional_norm_layer_1_output"
        error_name = "Tensor_onnx::connect_1_input"
        api_name_1 = utils.get_api_name_from_matcher(normal_name)
        api_name_2 = utils.get_api_name_from_matcher(unusual_name)
        api_name_3 = utils.get_api_name_from_matcher(error_name)
        self.assertEqual(api_name_1, "relu")
        self.assertEqual(api_name_2, "norm_layer")
        self.assertEqual(api_name_3, "")

