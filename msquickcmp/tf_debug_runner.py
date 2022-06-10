#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class is used to generate GUP dump data of the TensorFlow model.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2022
"""
import argparse
import sys
import os
import numpy as np
import tensorflow as tf
from tensorflow.python import debug as tf_debug
from common import utils, tf_common
if tf_common.check_tf_version(tf_common.VERSION_TF2X):
    import tfdbg_ascend as dbg
from common.utils import AccuracyCompareException


class TfDebugRunner(object):
    """
    This class is used to generate GUP dump data of the TensorFlow model.
    """

    def __init__(self, arguments):
        self.args = arguments
        self.global_graph = None
        self.input_shapes = utils.parse_input_shape(self.args.input_shape)
        self.input_path = self.args.input_path
        self.dump_root = os.path.realpath(self.args.out_path)

    def _dump_control(self):
        if tf_common.check_tf_version(tf_common.VERSION_TF2X):
            dbg.enable()
            dbg.set_dump_path(self.dump_root)

    def _load_graph(self):
        try:
            with tf.io.gfile.GFile(self.args.model_path, 'rb') as f:
                global_graph_def = tf.compat.v1.GraphDef.FromString(f.read())
            self.global_graph = tf.Graph()
            with self.global_graph.as_default():
                tf.import_graph_def(global_graph_def, name='')
        except Exception as err:
            utils.print_error_log("Failed to load the model %s. %s" % (self.args.model_path, err))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR)
        utils.print_info_log("Load the model %s successfully." % self.args.model_path)

    def _get_outputs_tensor(self):
        outputs_tensor = []
        for tensor_name in self.args.output_nodes.split(';'):
            tensor = self.global_graph.get_tensor_by_name(tensor_name)
            outputs_tensor.append(tensor)
        return outputs_tensor

    def _run_model(self, inputs_map, outputs_tensor):
        config = tf.compat.v1.ConfigProto(log_device_placement=False, allow_soft_placement=True)
        with tf.compat.v1.Session(graph=self.global_graph, config=config) as sess:
            if tf_common.check_tf_version(tf_common.VERSION_TF1X):
                sess = tf_debug.LocalCLIDebugWrapperSession(sess, ui_type="readline", dump_root=self.dump_root)
            return sess.run(outputs_tensor, feed_dict=inputs_map)

    def run(self):
        """
        Function description:
            run TensorFlow model
        """
        self._dump_control()
        self._load_graph()
        inputs_tensor = tf_common.get_inputs_tensor(self.global_graph, self.args.input_shape)
        inputs_map = tf_common.get_inputs_data(inputs_tensor, self.args.input_path)
        outputs_tensor = self._get_outputs_tensor()
        self._run_model(inputs_map, outputs_tensor)


def _make_dump_data_parser(parser):
    parser.add_argument("-m", "--model-path", dest="model_path", default="",
                        help="<Required> The original model (.pb) file path", required=True)
    parser.add_argument("-i", "--input-path", dest="input_path", default="",
                        help="<Required> The input data path of the model. Separate multiple inputs with commas(,)."
                             " E.g: input_0.bin,input_1.bin", required=True)
    parser.add_argument("-o", "--out-path", dest="out_path", default="", help="<Required> The output path")
    parser.add_argument("-s", "--input-shape", dest="input_shape", default="",
                        help="<Required> Shape of input shape. Separate multiple nodes with semicolons(;)."
                             " E.g: input_name1:1,224,224,3;input_name2:3,300")
    parser.add_argument("--output-nodes", dest="output_nodes", default="", required=True,
                        help="<Required> Output nodes designated by user. Separate multiple nodes with semicolons(;)."
                             " E.g: node_name1:0;node_name2:1;node_name3:0")


def main():
    """
   Function Description:
       main process function
   Exception Description:
       exit the program when an AccuracyCompare Exception  occurs
   """
    parser = argparse.ArgumentParser()
    _make_dump_data_parser(parser)
    args = parser.parse_args(sys.argv[1:])
    TfDebugRunner(args).run()


if __name__ == '__main__':
    main()
