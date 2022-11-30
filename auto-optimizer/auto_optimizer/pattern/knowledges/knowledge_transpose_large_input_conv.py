# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Dict
import logging
import operator as op

import numpy as np
import onnx

from auto_optimizer.pattern.knowledge_factory import KnowledgeFactory
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode, Initializer, Node, PlaceHolder
from auto_optimizer.pattern.pattern import MATCH_PATTERN, Pattern, MatchBase
from auto_optimizer.pattern.matcher import MatchResult
from auto_optimizer.pattern.knowledges.knowledge_base import KnowledgeBase
from auto_optimizer.pattern.utils import NextNodeCount

SHAPE_THRESHOLD = 20000


class HugeConv(MatchBase):
    def __init__(self):
        super().__init__()

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        if node is None or not isinstance(node, Node):
            return False
        if not op.eq(node.op_type, 'Conv'):
            return False
        kernel_shape = node.attrs.get('kernel_shape', None)
        if not (kernel_shape is not None and isinstance(kernel_shape, (list, ))):
            return False
        if len(kernel_shape) != 2:
            return False
        ph = graph.get_node(node.inputs[0], node_type=PlaceHolder)
        if ph is None or ph.shape is None or isinstance(ph.shape[-1], str):
            return False
        return ph.shape[-1] >= SHAPE_THRESHOLD


# AASIST pattern
# when W axis is huge, we exchange W/H axis because H axis have better tiling strategy
# this signifigant reduce the time npu takes to calculate Conv_0/Conv_1/Conv_2
r"""
      PreNode                          PreNode
         |                                |
         |                           Transpose_W_to_H
         |                                |
       Selu_0                           Selu_0
       /   \                            /   \
      /     \                          /     \
     /       \                        /       \
  Conv_1      |                  Conv_1_tr     |
    |         |       Transpose      |         |
  Selu_1    Conv_0   ==========>   Selu_1  Conv_0_tr
    |         |                      |         |
  Conv_2      |                  Conv_2_tr     |
     \       /                        \       /
      \     /                          \     /
       \   /                            \   /
       Add_0                            Add_0
         |                                |
         |                           Transpose_H_to_W
         |                                |
      NextNode                         NextNode
"""
# Selu_0 is special here because it has two next nodes
pattern_aasist = Pattern() \
    .add_node("Selu_0", ["Selu"], [NextNodeCount(2)]) \
    .add_node("Conv_0", ["Conv"], [NextNodeCount(1), HugeConv()]) \
    .add_node("Conv_1", ["Conv"], [NextNodeCount(1), HugeConv()]) \
    .add_node("Selu_1", ["Selu"], [NextNodeCount(1)]) \
    .add_node("Conv_2", ["Conv"], [NextNodeCount(1), HugeConv()]) \
    .add_node("Add_0", ["Add"], [NextNodeCount(1)]) \
    .add_node("MaxPool_0", ["MaxPool"]) \
    .add_edge("Selu_0", "Conv_0") \
    .add_edge("Selu_0", "Conv_1") \
    .add_edge("Conv_1", "Selu_1") \
    .add_edge("Selu_1", "Conv_2") \
    .add_edge("Conv_0", "Add_0") \
    .add_edge("Conv_2", "Add_0") \
    .add_edge("Add_0", "MaxPool_0") \
    .set_input("Selu_0") \
    .set_output("MaxPool_0") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)


@KnowledgeFactory.register()
class KnowledgeTransposeLargeInputConv(KnowledgeBase):
    """Swap H/W axis of conv operator with large input shape."""
    def __init__(self):
        super().__init__()
        # 注册pattern的apply方法
        self._register_apply_funcs(pattern_aasist, [self._aasist_pattern_apply])

    def pre_process(self, graph: BaseGraph) -> bool:
        try:
            graph.infershape()
        except onnx.onnx_cpp2py_export.shape_inference.InferenceError:
            logging.info('infershape failed before optimization.')
        return True

    def post_process(self, graph: BaseGraph) -> bool:
        try:
            graph.infershape()
        except onnx.onnx_cpp2py_export.shape_inference.InferenceError:
            logging.info('infershape failed after optimization.')
        return True

    def _transpose_conv(self, graph: BaseGraph, conv: Node):
        # we need to transpose H/W axes of dilations/kernel_shape/pads/strides attrs and weight input
        # we don't need to transpose bias input since it can only be 1D
        dilations = conv.attrs.get('dilations', [1, 1])
        dilations[-1], dilations[-2] = dilations[-2], dilations[-1]
        conv.attrs['dilations'] = dilations

        kernel_shape = conv.attrs.get('kernel_shape', [3, 3])
        kernel_shape[-1], kernel_shape[-2] = kernel_shape[-2], kernel_shape[-1]
        conv.attrs['kernel_shape'] = kernel_shape

        pads = conv.attrs.get('pads', [0, 0, 0, 0])
        pads[-1], pads[-2] = pads[-2], pads[-1]
        pads[len(pads)//2-1], pads[len(pads)//2-2] = pads[len(pads)//2-2], pads[len(pads)//2-1]
        conv.attrs['pads'] = pads

        strides = conv.attrs.get('strides', [1, 1])
        strides[-1], strides[-2] = strides[-2], strides[-1]
        conv.attrs['strides'] = strides

        weight = graph.get_node(conv.inputs[1], node_type=Initializer)
        perm = [i for i in range(len(weight.value.shape))]
        perm[-1], perm[-2] = perm[-2], perm[-1]
        weight_value = np.transpose(weight.value, perm)
        name = f'{conv.name}_new_init'
        graph.add_initializer(name=name, value=weight_value)
        conv.inputs[1] = name

    def _aasist_match_apply(self, graph: BaseGraph, matchinfo: Dict[str, List[BaseNode]]) -> bool:
        # make sure nodes of matching subgraph still exist in case some previous apply functions modified graph
        if any(graph.get_node(node.name, node_type=Node) is None for nodes in matchinfo.values() for node in nodes):
            logging.info("Some matching node have been removed or renamed, failed to optimizd.")
            return False

        selu_0 = graph.get_node(matchinfo['Selu_0'][0].name, node_type=Node)
        add_0 = graph.get_node(matchinfo['Add_0'][0].name, node_type=Node)
        convs = [graph.get_node(matchinfo[name][0].name, node_type=Node) for name in ('Conv_0', 'Conv_1', 'Conv_2')]
        ph = graph.get_node(selu_0.inputs[0], node_type=PlaceHolder)
        if ph is None or ph.shape is None:
            logging.info("Failed to get input shape of subgraph.")
            return False
        perm = [i for i in range(len(ph.shape))]
        perm[-1], perm[-2] = perm[-2], perm[-1]

        # add transpose node before selu_0
        transpose_pre = graph.add_node(
            name=f'Transpose_pre_{selu_0.name}_aasist_pattern',
            op_type='Transpose',
            attrs={'perm': perm}
        )
        graph.insert_node(selu_0.name, transpose_pre, 0, 'before')

        # transpose H/W axes for convolution nodes
        for conv in convs:
            self._transpose_conv(graph, conv)

        # add transpose node after add_0
        transpose_post = graph.add_node(
            name=f'Transpose_post_{add_0.name}_aasist_pattern',
            op_type='Transpose',
            attrs={'perm': perm}
        )
        graph.insert_node(add_0.name, transpose_post, 0, 'after')
        graph.update_map()
        return True

    def _aasist_pattern_apply(self, graph: BaseGraph, match_result: MatchResult) -> bool:
        flag = False
        for matchinfo in match_result.node_dicts:
            if matchinfo:
                flag |= self._aasist_match_apply(graph, matchinfo)
        return flag
