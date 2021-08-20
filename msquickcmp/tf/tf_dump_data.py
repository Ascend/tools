#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class is used to generate GUP dump data of the TensorFlow model.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2021
"""
import re
import sys
import readline
import pexpect
import time
import os
import numpy as np
import tensorflow as tf
from common.dump_data import DumpData
from common import utils
from common.utils import AccuracyCompareException


class TfDumpData(DumpData):
    """
    This class is used to generate GUP dump data of the TensorFlow model.
    """

    def __init__(self, arguments):
        self.args = arguments
        output_path = os.path.realpath(self.args.out_path)
        self.data_dir = os.path.join(output_path, "input")
        self.tf_dump_data_dir = os.path.join(output_path, "dump_data/tf")
        self.tmp_dir = os.path.join(output_path, "tmp")
        self.global_graph = None
        self.input_path = self.args.input_path

    def _create_dir(self):
        # create input directory
        utils.create_directory(self.data_dir)

        # create dump_data/tf directory
        utils.create_directory(self.tf_dump_data_dir)

        # create tmp directory
        utils.create_directory(self.tmp_dir)

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

    def _make_inputs_data(self, inputs_tensor):
        if "" == self.args.input_path:
            input_path_list = []
            for index, tensor in enumerate(inputs_tensor):
                input_data = np.random.random(utils.convert_tensor_shape(tensor.shape)) \
                    .astype(utils.convert_to_numpy_type(tensor.dtype))
                input_path = os.path.join(self.data_dir, "input_" + str(index) + ".bin")
                input_path_list.append(input_path)
                try:
                    input_data.tofile(input_path)
                except Exception as err:
                    utils.print_error_log("Failed to generate data %s. %s" % (input_path, err))
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
                utils.print_info_log("file name: {}, shape: {}, dtype: {}".format(
                    input_path, input_data.shape, input_data.dtype))
                self.input_path = ','.join(input_path_list)
        else:
            input_path = self.args.input_path.split(",")
            if len(inputs_tensor) != len(input_path):
                utils.print_error_log("the number of model inputs tensor is not equal the number of "
                                      "inputs data, inputs tensor is: {}, inputs data is: {}".format(
                    len(inputs_tensor), len(input_path)))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)

    def _run_model(self, outputs_tensor):
        tf_debug_runner_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "tf_debug_runner.py")
        cmd = '%s %s -m %s -i %s --output-nodes %s -o %s' \
              % (sys.executable, tf_debug_runner_path, self.args.model_path, self.input_path,
                 ";".join(outputs_tensor), os.path.join(self.tmp_dir, "tf_dbg"))
        if self.args.input_shape:
            cmd += " -s " + self.args.input_shape
        self._run_tf_dbg_dump(cmd)

    def _make_pt_command(self, tensor_name_path):
        pt_command_list = []
        with open(tensor_name_path) as tensor_name_file:
            # skip 3 line
            next(tensor_name_file)
            next(tensor_name_file)
            next(tensor_name_file)
            # start to convert tensor to pt command
            for line in tensor_name_file:
                new_line = line.strip()
                tensor_name = new_line[new_line.rfind(' ') + 1:]
                npy_file_name = "%s.%s.npy" % (tensor_name.replace("/", "_").replace(":", "."),
                                               str(round(time.time() * 1000000)))
                pt_command_list.append("pt %s -n 0 -w %s" %
                                       (tensor_name, os.path.join(self.tf_dump_data_dir, npy_file_name)))
        return pt_command_list

    def _run_tf_dbg_dump(self, cmd_line):
        """Run tf debug with pexpect, should set tf debug ui_type='readline'"""
        tf_dbg = pexpect.spawn(cmd_line)
        tf_dbg.logfile = sys.stdout.buffer
        try:
            tf_dbg.expect('tfdbg>', timeout=utils.TF_DEBUG_TIMEOUT)
            utils.print_info_log("Start to run. Please wait....")
            tf_dbg.sendline('run')
            tf_dbg.expect('tfdbg>', timeout=utils.TF_DEBUG_TIMEOUT)
        except Exception as ex:
            tf_dbg.sendline('exit')
            utils.print_error_log("Failed to run command: %s. %s" % (cmd_line, ex))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_COMMAND_ERROR)
        tensor_name_path = os.path.join(self.tmp_dir, 'tf_tensor_names.txt')
        tf_dbg.sendline('lt > %s' % tensor_name_path)
        tf_dbg.expect('tfdbg>', timeout=utils.TF_DEBUG_TIMEOUT)
        if not os.path.exists(tensor_name_path):
            tf_dbg.sendline('exit')
            utils.print_error_log("Failed to save tensor name to file.")
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_COMMAND_ERROR)
        utils.print_info_log("Save tensor name to %s successfully." % tensor_name_path)
        pt_command_list = self._make_pt_command(tensor_name_path)
        utils.print_info_log("Start to run %d pt commands. Please wait..." % len(pt_command_list))
        for cmd in pt_command_list:
            tf_dbg.sendline(cmd.strip())
            tf_dbg.expect('tfdbg>', timeout=utils.TF_DEBUG_TIMEOUT)
        tf_dbg.sendline('exit')
        utils.print_info_log('Finish dump tf data.')

    def _get_all_node_and_input_node(self):
        input_nodes = []
        node_list = []
        operations = self.global_graph.get_operations()
        for op in operations:
            node_list.append(op.name)
            for tensor in op.inputs:
                input_name = tensor.name.split(':')[0]
                if input_name not in input_nodes:
                    input_nodes.append(input_name)
        return input_nodes, node_list

    def _check_node_output(self, node_name):
        op = self.global_graph.get_operation_by_name(node_name)
        if op.outputs:
            return True
        return False

    def _check_output_nodes_valid(self, outputs_tensor, node_list):
        for tensor in outputs_tensor:
            tensor_info = tensor.strip().split(':')
            if len(tensor_info) != 2:
                utils.print_error_log(
                    'Invalid output nodes (%s). Only support "name1:0;name2:1". Please check the output node.' % tensor)
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            node_name = tensor_info[0].strip()  # 0 for node_name
            if not node_name:
                utils.print_error_log(
                    'Invalid output nodes (%s). Only support "name1:0;name2:1". Please check the output node.' % tensor)
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            if node_name not in node_list:
                utils.print_error_log(
                    "The output node (%s) is not in the graph. Please check the output node." % node_name)
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            index = tensor_info[1].strip()  # 1 for tensor_index
            if not index:
                utils.print_error_log(
                    'Invalid output nodes (%s). Only support "name1:0;name2:1". Please check the output node.' % tensor)
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            op = self.global_graph.get_operation_by_name(node_name)
            pattern = re.compile(r'^[0-9]+$')
            match = pattern.match(index)
            if match is None:
                utils.print_error_log("The index (%s) of %s is invalid. Please check the output node."
                                      % (index, node_name))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            if int(index) < 0 or int(index) >= len(op.outputs):
                utils.print_error_log("The index (%s) of %s out of range [0, %d). Please check the output node."
                                      % (index, node_name, len(op.outputs)))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)

    def _get_outputs_tensor(self):
        input_nodes, node_list = self._get_all_node_and_input_node()
        outputs_tensor = []
        if self.args.output_nodes:
            outputs_tensor = self.args.output_nodes.strip().split(';')
            self._check_output_nodes_valid(outputs_tensor, node_list)
        else:
            output_nodes = list(set(node_list).difference(set(input_nodes)))
            for name in output_nodes:
                if self._check_node_output(name):
                    outputs_tensor.append(name + ":0")
        utils.print_info_log("The outputs tensor:\n{}\n".format(outputs_tensor))
        return outputs_tensor

    def generate_dump_data(self):
        """
        Generate TensorFlow model dump data
        :return tensorFlow model dump data directory
        """
        self._load_graph()
        self._create_dir()
        inputs_tensor = utils.get_inputs_tensor(self.global_graph, self.args.input_shape)
        self._make_inputs_data(inputs_tensor)
        outputs_tensor = self._get_outputs_tensor()
        self._run_model(outputs_tensor)
        return self.tf_dump_data_dir
