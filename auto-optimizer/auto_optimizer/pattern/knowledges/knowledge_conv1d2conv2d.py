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
import operator as op
import numpy as np
import onnx

from auto_optimizer.pattern.knowledge_factory import KnowledgeFactory
from auto_optimizer.pattern.pattern import MATCH_PATTERN
from auto_optimizer.pattern.pattern import MatchBase
from auto_optimizer.pattern.pattern import Pattern
from auto_optimizer.pattern.matcher import MatchResult
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode, Node
from auto_optimizer.pattern.knowledges.knowledge_base import KnowledgeBase


class Conv1dMatch(MatchBase):
    def __init__(self):
        super().__init__()

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        if node is None:
            return False
        if not op.eq(node.op_type, 'Conv'):
            return False
        if len(node.inputs) > 1:
            weight = graph[node.inputs[1]]
            return len(weight.value.shape) == 3
        return False


# element_wise允许出现0次，或者多次
pattern = Pattern() \
    .add_node('Conv', ['Conv'], [Conv1dMatch()]) \
    .add_node('element_wise', ['Mul', 'Add', 'Sub', 'Div', 'Abs', 'Tanh', 'BatchNormalization', 'LeakyRelu', 'Relu']) \
    .add_edge('Conv', 'element_wise') \
    .set_input('Conv') \
    .set_output('element_wise') \
    .set_node_loop('element_wise', MATCH_PATTERN.MATCH_ZERO_OR_MORE) \
    .set_loop(MATCH_PATTERN.MATCH_ONCE_OR_MORE)


@KnowledgeFactory.register()
class KnowledgeConv1d2Conv2d(KnowledgeBase):
    def __init__(self):
        super().__init__()
        self._insert_op_names = set()
        # 注册pattern的apply方法
        self._register_apply_funcs(pattern, [self._conv1d2conv2d_apply])

    def __is_lower_onnx_version(self, graph) -> bool:
        """
        判断当前onnx版本是否小于1.11.0
        :param graph: 整图
        :return: onnx版本小于1.11.0，则返回True，否则返回False
        """
        limit_version = 13
        domain_check = lambda domain: domain == '' or domain == 'ai.onnx'
        opset_versions = [opset.version for opset in graph.opset_imports if domain_check(opset.domain)]
        return len(opset_versions) == 0 or opset_versions[0] < limit_version

    def _expand_conv_input_dims(self, graph, conv, refer_index) -> BaseNode:
        """
        通过增加Unsqueeze算子，将conv1d的输入从3维扩展到4维
        :param graph: 整图
        :param conv: 卷积算子，在该算子前面插入Unsqueeze算子
        :param refer_index: 插入算子的输入索引
        :return: 插入的Unsqueeze算子对象
        """
        op_name = f'Unsqueeze_before_{conv.name}'
        if op_name in self._insert_op_names:
            return None
        self._insert_op_names.add(op_name)
        if self.__is_lower_onnx_version(graph):
            us = graph.add_node(op_name, 'Unsqueeze', attrs={'axes': np.array([2], dtype=np.int64)})
            graph.insert_node(conv.name, us, mode='before', refer_index=refer_index)
        else:
            us = graph.add_node(op_name, 'Unsqueeze')
            axes_name = f'{op_name}_axes'
            graph.add_initializer(axes_name, np.array([2], dtype=np.int64))
            graph.insert_node(conv.name, us, mode='before', refer_index=refer_index)
            us.inputs.append(axes_name)
        graph.update_map()
        return us

    def _conv1d_to_conv2d(self, graph, conv) -> bool:
        """
        将conv1d转换成conv2d，修改conv1d属性和W
        :param graph: 整图
        :param conv: 卷积算子
        :return: True：操作成功；False：操作失败
        """
        attrs = ('dilations', 'kernel_shape', 'strides')
        for attr in attrs:
            if attr in conv.attrs.keys():
                val = conv[attr][0]
                conv[attr] = [1, val]

        if 'pads' in conv.attrs.keys():
            pds = conv['pads'][0]
            conv['pads'] = [0, pds, 0, pds]

        conv_w = graph[conv.inputs[1]].value
        conv_w = np.expand_dims(conv_w, axis=-2)
        graph[conv.inputs[1]].value = conv_w
        return True

    def _reduce_output_dims(self, graph, node, mode: str, refer_index) -> BaseNode:
        """
        降低维度
        :param graph: 整图
        :param node: 在该算子之前或之后插入Squeeze算子
        :param mode: 插入模式 before or after
        :param refer_index: 插入算子的输入索引
        :return: 插入的Squeeze算子对象
        """
        op_name = f'Squeeze_{mode}_{node.name}_{refer_index}'
        if op_name in self._insert_op_names:
            return None
        self._insert_op_names.add(op_name)
        if self.__is_lower_onnx_version(graph):
            sq = graph.add_node(op_name, 'Squeeze', attrs={'axes': np.array([2], dtype=np.int64)})
            graph.insert_node(node.name, sq, mode=mode, refer_index=refer_index)
        else:
            sq = graph.add_node(op_name, 'Squeeze')
            axes_name = f'{op_name}_axes'
            graph.add_initializer(axes_name, np.array([2], dtype=np.int64))
            graph.insert_node(node.name, sq, mode=mode, refer_index=refer_index)
            sq.inputs.append(axes_name)
        graph.update_map()
        return sq

    def _conv1d2conv2d_apply(self, graph, match_result: MatchResult) -> bool:
        node_map     = {}
        node_inputs  = set()
        node_outputs = set()
        const_inputs = set()
        # 构建所有输入输出的集合
        for node_dict in match_result.node_dicts:
            for nodes in node_dict.values():
                for node in nodes:
                    node_map[node.name] = node
                    for node_input in node.inputs:
                        node_inputs.add(node_input)
                    for node_output in node.outputs:
                        node_outputs.add(node_output)
        # 构建常量输入集合
        for node in graph.initializers:
            const_inputs.add(node.name)
        
        for node in node_map.values():
            for refer_index, node_input in enumerate(node.inputs):
                # 如果输入不在输出集合中，并且不在常量输入集合中则认为此输入为子图的外部输入
                if node_input not in node_outputs and node_input not in const_inputs:
                    self._expand_conv_input_dims(graph, node, refer_index)
            
            insert_node = None
            for refer_index, node_output in enumerate(node.outputs):
                next_nodes = graph.get_next_nodes(node_output).copy()
                # 如果没有后继节点出则在当前节点之后插入 Squeeze 节点
                if len(next_nodes) == 0:
                    self._reduce_output_dims(graph, node, 'after', 0)
                    continue
                for next_node in next_nodes:
                    # 区分后继节点的类型，如果后继节点不是算子节点则在当前节点之后插入 Squeeze 节点
                    if not isinstance(next_node, Node):
                        self._reduce_output_dims(graph, node, 'after', 0)
                        break
                    # 如果后继节点是算子节点则将 Squeeze 节点插入到后继节点之前
                    if next_node.name not in node_map.keys():
                        refer_index = next_node.inputs.index(node_output)
                        # 如果已插入过 Squeeze 节点则复用
                        if insert_node is not None:
                            next_node.inputs[refer_index] = insert_node.outputs[0]
                            graph.update_map()
                            continue
                        _insert_node = self._reduce_output_dims(graph, next_node, 'before', refer_index)
                        if _insert_node is not None:
                            insert_node = _insert_node

        # 对 Conv 节点进行升维
        for node_dict in match_result.node_dicts:
            conv1d_name = node_dict.get('Conv')[0].name
            conv1d = graph[conv1d_name]
            self._conv1d_to_conv2d(graph, conv1d)
        return True
