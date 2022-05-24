# coding=utf-8
import json
import re
from typing import List
from .desc import InputDesc
from .desc import OutputDesc
from ..util.util import util
from ..util.constant import Constant
from ..util.precision_tool_exception import PrecisionToolException

NO_INPUT_NODES = ['Data', 'AtomicAddrClean', 'Recv', 'Constant']
NO_OUTPUT_NODES = ['Send', 'Recv', 'NetOutput', 'PartitionedCall']

JSON_KEY_NAME = 'name'
JSON_KEY_ID = 'id'
JSON_KEY_TYPE = 'type'
JSON_KEY_ATTR = 'attr'
JSON_KEY = 'key'
JSON_VALUE = 'value'
JSON_KEY_LIST = 'list'
JSON_KEY_STR = 's'
JSON_KEY_INT = 'i'
JSON_KEY_PASS_NAME = 'pass_name'
JSON_KEY_DATA_DUMP_ORIGINAL_OP_NAMES = '_datadump_original_op_names'
JSON_KEY_GE_ATTR_OP_KERNEL_LIB_NAME = "_ge_attr_op_kernel_lib_name"
JSON_KEY_PARENT_NODE_INDEX = "_parent_node_index"
JSON_KEY_SUBGRAPH_NAME = "subgraph_name"

KERNEL_NAME_SHUFFIX = '_kernelname'


class Op(object):
    """ Op class.
        name: op name
        type: op type
        inputs: list of input descs
        outputs: list of output descs
    """
    def __init__(self, op_json, op_list, graph_name, npu_graph, sub_graph):
        """Init"""
        self.op_json = op_json
        self.op_list = op_list
        self.graph_name = graph_name
        self.npu_graph = npu_graph
        self.sub_graph = sub_graph
        self.input_list = None
        self.output_list = None
        self.log = util.get_log()

    def name(self):
        """Get op name"""
        return self.op_json[JSON_KEY_NAME]

    def id(self):
        """Get op id"""
        return self.op_json[JSON_KEY_ID] if JSON_KEY_ID in self.op_json else ''

    def json(self):
        return json.dumps(self.op_json, indent=2)

    def type(self):
        """Get op type"""
        return self.op_json[JSON_KEY_TYPE]

    def subgraph_names(self):
        return self.op_json[JSON_KEY_SUBGRAPH_NAME] if JSON_KEY_SUBGRAPH_NAME in self.op_json else []

    def inputs(self):
        """Get the input list"""
        if self.input_list is None:
            self._parse_inputs()
        if len(self.input_list) == 0 and self.type() == 'Data':
            # Looking for Real Data
            self._looking_for_real_inputs()
        return self.input_list

    def outputs(self):
        """Get output list"""
        if self.output_list is None:
            self._parse_outputs()
        if len(self.output_list) == 0 and self.type() == 'PartitionedCall':
            self._looking_for_real_outputs()
        return self.output_list

    def pass_name(self):
        return self._attr(JSON_KEY_PASS_NAME)

    def kernel_name(self):
        return self._attr(self.name() + KERNEL_NAME_SHUFFIX)

    def ge_attr_op_kernel_lib_name(self):
        return self._attr(JSON_KEY_GE_ATTR_OP_KERNEL_LIB_NAME)

    def data_dump_original_op_names(self):
        return self._attr(JSON_KEY_DATA_DUMP_ORIGINAL_OP_NAMES)

    def parent_node_index(self):
        return self._attr(JSON_KEY_PARENT_NODE_INDEX)

    def _attr(self, key):
        if JSON_KEY_ATTR in self.op_json:
            for attr in self.op_json[JSON_KEY_ATTR]:
                if key == attr[JSON_KEY]:
                    if JSON_KEY_STR in attr[JSON_VALUE]:
                        return attr[JSON_VALUE][JSON_KEY_STR]
                    elif JSON_KEY_LIST in attr[JSON_VALUE]:
                        if JSON_KEY_STR in attr[JSON_VALUE][JSON_KEY_LIST]:
                            return attr[JSON_VALUE][JSON_KEY_LIST][JSON_KEY_STR]
                    elif JSON_KEY_INT in attr[JSON_VALUE]:
                        return attr[JSON_VALUE][JSON_KEY_INT]
                    else:
                        self.log.warning("Unknown attr format: %s", attr[JSON_VALUE])
        return ''

    def compare(self, right_op):
        """Compare with another op"""
        if not isinstance(right_op, Op):
            raise PrecisionToolException("Should compare with another op.")
        res_str = ['LeftOp(Type/Name) : [green][%s][/green] %s' % (self.type(), self.name()),
                   'RightOp(Type/Name): [green][%s][/green] %s' % (right_op.type(), right_op.name())]
        similar = True
        if len(self.inputs()) != len(right_op.inputs()):
            res_str.append("Input: [yellow]Input num mismatch.[/yellow]")
        else:
            res_str.append("Input:")
        for left_input in self.inputs():
            for right_input in right_op.inputs():
                if left_input.idx() != right_input.idx():
                    continue
                txt, input_similar = left_input.compare(right_input)
                res_str.append(' - ' + txt)
                similar = similar and input_similar
        if len(self.outputs()) != len(right_op.outputs()):
            res_str.append("Output: [yellow]Output num mismatch.[/yellow]")
        else:
            res_str.append("Output:")
        for left_output in self.outputs():
            for right_output in right_op.outputs():
                if left_output.idx() != right_output.idx():
                    continue
                txt, output_similar = left_output.compare(right_output)
                res_str.append(' - ' + txt)
                similar = similar and output_similar
        return Constant.NEW_LINE.join(res_str), similar

    def _attr_detail(self):
        """Gen attr details"""
        res_str = []
        if JSON_KEY_ATTR in self.op_json:
            res_str = [' ' + str(i) for i in self.op_json[JSON_KEY_ATTR]]
        return Constant.NEW_LINE.join(res_str)

    def summary(self, origin_txt=False, attr_detail=False):
        """Summary of current op"""
        res_str = ['Op(Type/Name): [green][%s][/green] %s' % (self.type(), self.name()),
                   'ID:    [yellow]%s[/yellow]' % self.id(),
                   'KernelName:    [yellow]%s[/yellow]' % self.kernel_name(),
                   'KernelLibName: [yellow]%s[/yellow]' % self.ge_attr_op_kernel_lib_name(),
                   'GraphName:     [yellow]%s[/yellow]' % self.graph_name]
        pass_name = self.pass_name()
        if pass_name != '':
            res_str.append('PassName: [yellow]%s[/yellow]' % pass_name)
        origin_op = self.data_dump_original_op_names()
        if origin_op != '':
            res_str.append('OriginalOp: %s' % origin_op)
        if attr_detail:
            res_str.append(self._attr_detail())
        res_str.append('Input:%s' % InputDesc.summary.__doc__)
        for i in self.inputs():
            res_str.append(' -' + i.summary(origin_txt))
        res_str.append('Output:')
        for i in self.outputs():
            res_str.append(' -' + i.summary(origin_txt))
        return Constant.NEW_LINE.join(res_str)

    def _parse_inputs(self):
        """ parse input desc in graph """
        self.input_list = []
        if 'input' not in self.op_json:
            if self.type() not in NO_INPUT_NODES:
                self.log.warning('Parse Op[%s][%s] inputs error.' % (self.type(), self.name()))
            return self.input_list
        desc_index = 0
        for i in range(len(self.op_json['input'])):
            name = self.op_json['input'][i]
            if name == '':
                # if self.type() not in NO_INPUT_NODES:
                # self.log.warning('invalid input name.')
                continue
            name_info = name.split(':')
            if len(name_info) == 2 and int(name_info[1]) == -1:
                # control edge
                self.input_list.append(InputDesc(name, [], i))
            else:
                self.input_list.append(InputDesc(name, self.op_json['input_desc'][desc_index], i))
                desc_index += 1
        self.input_list.sort(key=lambda x: x.index)
        return self.input_list

    def _parse_outputs(self):
        """ parse output desc in graph """
        self.output_list = []
        if 'dst_index' not in self.op_json:
            if self.type() not in NO_OUTPUT_NODES:
                self.log.warning('Parse Op[%s][%s] outputs error.' % (self.type(), self.name()))
            return self.output_list
        desc_index = 0
        for i in range(len(self.op_json['dst_index'])):
            dst_name = self.op_json['dst_name'][i]
            if self.op_json['dst_index'][i] == -1:
                # control edge
                self.output_list.append(OutputDesc(dst_name, [], -1))
            else:
                self.output_list.append(OutputDesc(dst_name, self.op_json['output_desc'][desc_index], desc_index))
                desc_index += 1
        self.output_list.sort(key=lambda x: x.index)
        return self.output_list

    def _looking_for_real_inputs(self):
        """Find real inputs of subgraph data node."""
        graph_name = self.graph_name
        parent_node_idx = self.parent_node_index()
        parent_nodes = self.npu_graph.get_parent_node_by_subgraph_name(graph_name)
        self.log.debug("Find %s parent nodes." % len(parent_nodes))
        for parent_node in parent_nodes:
            inputs = parent_node.inputs()
            if len(inputs) <= parent_node_idx:
                self.log.warning("Parent node has %d inputs, bug need index %d" % (len(inputs), parent_node_idx))
                continue
            self.input_list.append(inputs[parent_node_idx])

    def _looking_for_real_outputs(self):
        """Find real outputs of PartitionedCall Node"""
        subgraph_names = self.subgraph_names()
        for subgraph_name in subgraph_names:
            net_output_with_subgraph_name = subgraph_name + '_Node_Output'
            net_output_nodes = self.npu_graph.get_op(net_output_with_subgraph_name)
            self.log.debug("Find %s net output nodes, just need one." % len(net_output_nodes))
            for output_node in net_output_nodes:
                self.output_list = output_node.inputs()




