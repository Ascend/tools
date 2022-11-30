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

from abc import abstractmethod
from enum import Enum, unique
from typing import List
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode


@unique
class MATCH_PATTERN(Enum):
    # 不循环，只匹配一次
    MATCH_ONCE = 1
    # 循环无上限，匹配一次或者多次
    MATCH_ONCE_OR_MORE = 2
    # 循环无上限，匹配零次或者多次
    MATCH_ZERO_OR_MORE = 3


# 子图遍历方向
@unique
class DIRECTION(Enum):
    # 从上往下遍历
    UP_DOWN = 1
    # 从下往上遍历
    DOWN_UP = 2
    # 方向不明确
    UNKNOWN = 3


class MatchBase(object):
    def __init__(self):
        pass

    @abstractmethod
    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        return False


class PatternNode(object):
    def __init__(self, op_name: str, op_types: List[str], op_matchs: List[MatchBase] = None):
        self.op_name = op_name
        self.op_types = op_types
        self.op_matchs = op_matchs
        self.inputs = []
        self.outputs = []

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        """
        算子节点匹配
        :param node: 实际算子节点
        :param graph: 实际子图对象
        :return: 匹配成功返回True，失败返回False
        """
        if node is None:
            return False
        if self.op_types and self.op_types.count(node.op_type) == 0:
            return False
        if self.op_matchs is None:
            return True
        for op_match in self.op_matchs:
            if not op_match.match(node, graph):
                return False
        return True

    def set_input(self, prev_node):
        """
        设置前置节点
        :param prev_node: 前置节点
        """
        self.inputs.append(prev_node)

    def set_output(self, next_node):
        """
        设置后置节点
        :param next_node: 设置后置节点
        """
        self.outputs.append(next_node)


class Pattern(object):
    def __init__(self):
        self.node_dict = {} # Dict[str, PatternNode]
        self.in_nodes = [] # PatternNode
        self.out_nodes = [] # PatternNode
        self.node_match_pattern_dict = {}
        self.graph_match_pattern = MATCH_PATTERN.MATCH_ONCE

    def add_node(self, op_name, op_types, op_matchs: List[MatchBase] = None):
        """
        创建PatternNode，并增加到节点列表
        :param op_name: 算子节点名
        :param op_types: 支持的算子类型列表
        :param op_matchs: 算子匹配规则列表
        :return: 返回实例
        """
        if self.node_dict.get(op_name) is not None:
            raise RuntimeError('Operator({}) has bean existed.'.format(op_name))
        self.node_dict[op_name] = PatternNode(op_name, op_types, op_matchs)
        return self

    def add_edge(self, prev_op_name: str, next_op_name: str):
        prev_node = self.node_dict.get(prev_op_name)
        if prev_node is None:
            raise RuntimeError('Operator({}) has not bean added.'.format(prev_op_name))
        next_node = self.node_dict.get(next_op_name)
        if next_node is None:
            raise RuntimeError('Operator({}) has not bean added.'.foramt(next_op_name))
        next_node.set_input(prev_node)
        prev_node.set_output(next_node)
        return self

    def set_input(self, op_name):
        """
        设置子图的输入节点
        :param op_name: 算子节点名
        :return: 返回实例
        """
        in_node = self.node_dict.get(op_name)
        if in_node is None:
            raise RuntimeError('Operator({}) has not bean added.'.format(op_name))
        if len(in_node.inputs) > 0:
            raise RuntimeError('Operator({}) is not output node.'.format(op_name))
        self.in_nodes.append(in_node)
        return self

    def set_output(self, op_name):
        """
        设置子图的输出节点
        :param op_name: 输出节点名
        :return: 返回实例
        """
        out_node = self.node_dict.get(op_name)
        if out_node is None:
            raise RuntimeError('Operator({}) has not bean added.'.format(op_name))
        if len(out_node.outputs) > 0:
            raise RuntimeError('Operator({}) is not output node.'.format(op_name))
        self.out_nodes.append(out_node)
        return self

    def set_node_loop(self, op_name, match_pattern):
        """
        设置算子节点匹配模式
        :param op_name: 算子节点名称
        :param match_pattern: 匹配模式
        :return: 返回实例
        """
        node = self.node_dict.get(op_name)
        if node is None:
            raise RuntimeError('Operator({}) has not bean added.'.format(op_name))
        self.node_match_pattern_dict[op_name] = match_pattern
        return self

    def set_loop(self, match_pattern):
        """
        设置子图循环模式
        单输入多输出、多输入单输出、多输入多输出不支持子图循环匹配
        :param match_pattern: 子图匹配模式
        :return: 返回实例
        """
        self.graph_match_pattern = match_pattern
        if match_pattern == MATCH_PATTERN.MATCH_ONCE_OR_MORE:
            if len(self.in_nodes) != len(self.out_nodes):
                raise RuntimeError('if match sub graph continously, ' \
                    'input nodes size should be equal to output nodes size.')
        return self

    def get_visit_direction(self):
        """
        获取子图匹配的遍历方式：
          1、多输入单输出，从下往上遍历
          2、单输出多输出，从上往下遍历
          3、单输入单输出，从上往下遍历
          4、多输入多输出，当前没有出现这样场景，暂时不支持
        """
        if len(self.in_nodes) == 1:
            # 单输入，则从上往下遍历
            return DIRECTION.UP_DOWN
        if len(self.out_nodes) == 1:
            # 单输出，从下往上遍历
            return DIRECTION.DOWN_UP
        # 多输入多输出场景，没法确定遍历方向，暂时不支持
        return DIRECTION.UNKNOWN

    def get_start_node(self):
        """
        获取子图匹配遍历的起始节点
        :return: 返回子图遍历的起始节点
        """
        if len(self.in_nodes) == 1:
            # 单输入，从子图输入节点开始，从上往下遍历
            return self.in_nodes[0]
        if len(self.out_nodes) == 1:
            # 单输出，从子图输出节点开始，从下往上遍历
            return self.out_nodes[0]
        # 多输入多输出不支持
        return None

    def node_can_match_more(self, op_name) -> bool:
        """
        节点是否支持匹配多个
        :param op_name: 算子节点名称
        :return: 能匹配则返回True，否则返回False
        """
        if op_name not in self.node_match_pattern_dict:
            return False
        return self.node_match_pattern_dict[op_name] == MATCH_PATTERN.MATCH_ONCE_OR_MORE or \
            self.node_match_pattern_dict[op_name] == MATCH_PATTERN.MATCH_ZERO_OR_MORE

    def node_can_match_zero(self, op_name) -> bool:
        """
        节点是否支持匹配0个
        :param op_name: 算子节点名称
        :return: 能匹配则返回True，否则返回False
        """
        if op_name not in self.node_match_pattern_dict:
            return False
        return self.node_match_pattern_dict[op_name] == MATCH_PATTERN.MATCH_ZERO_OR_MORE

    def can_match_more(self) -> bool:
        """
        判断子图是否可以循环匹配
        :return: 能匹配则返回True，否则返回False
        """
        return self.graph_match_pattern == MATCH_PATTERN.MATCH_ONCE_OR_MORE or \
            self.graph_match_pattern == MATCH_PATTERN.MATCH_ZERO_OR_MORE
