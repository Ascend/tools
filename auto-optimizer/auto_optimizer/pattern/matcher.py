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

import copy
import types
import operator as op
from typing import List, Dict
from auto_optimizer.graph_refactor.interface.base_node import BaseNode
from .pattern import PatternNode
from .pattern import DIRECTION


class MatchResult(object):
    def __init__(self, pattern):
        self.pattern = pattern
        self.node_dicts = []

    def add_node_dict(self, node_dict: Dict[str, List[BaseNode]]):
        """
        添加子图匹配到的节点数据
        :param node_dict:子图匹配后的所有节点，字典key是算子名，value是实际算子节点
        """
        direction = self.pattern.get_visit_direction()
        if direction == DIRECTION.DOWN_UP:
            self.node_dicts.insert(0, node_dict)
        else:
            self.node_dicts.append(node_dict)

    def is_empty(self):
        """
        判断当前匹配结果是否为空
        :return 匹配结果为空则返回True，否则返回False
        """
        if len(self.node_dicts) == 0:
            return True
        for node_dict in self.node_dicts:
            if len(node_dict) != 0:
                return False
        return True


class Matcher(object):
    def __init__(self, graph, pattern):
        self._graph = graph
        self._pattern = pattern

    def get_candidate_nodes(self) -> List[BaseNode]:
        """
        根据定义的子图的输入/输出节点，匹配计算图中所有候选节点
        :return: 返回候选节点列表
        """
        start_pattern_node = self._pattern.get_start_node()
        if start_pattern_node is None:
            return []

        ret = [] # List[NodeBase]
        hash_set = set()
        for node in self._graph.nodes:
            if not start_pattern_node.match(node, self._graph):
                continue
            if node.name in hash_set:
                continue
            ret.append(node)
            hash_set.add(node.name)
        return ret

    def __get_prev_nodes(self, cur_node: BaseNode):
        """
        根据节点输入名，获取所有该节点的前置节点
        """
        prev_nodes = set()
        for input_name in cur_node.inputs:
            node = self._graph.get_prev_node(input_name)
            if node is None:
                continue
            prev_nodes.add(node)
        return list(prev_nodes)

    def __get_prev_pattern_nodes(self, pattern_node) -> List[PatternNode]:
        """
        获取节点前置节点
        :param pattern_node: 算子节点模板
        """
        return pattern_node.inputs

    def __get_next_pattern_nodes(self, pattern_node) -> List[PatternNode]:
        """
        获取节点后置节点
        :param pattern_node: 算子节点模板
        """
        return pattern_node.outputs

    def __nodes_group_dfs(self, nodes, pattern_nodes, nodes_map, nodes_map_group, get_next_func):
        """
        匹配nodes和pattern_nodes，生成所有能匹配的组合
        :param nodes: 实际算子节点列表
        :param pattern_nodes: 算子节点列表，知识库中定义的算子节点
        :param nodes_map: nodes和pattern_nodes中匹配的节点
        :param nodes_map_group: nodes和pattern_nodes可以匹配的组合的一个集合
        :param get_next_func: 获取前置或者后置节点的方法
        """
        if len(nodes_map) == len(pattern_nodes):
            nodes_map_group.append(copy.deepcopy(nodes_map))
            return
        for pattern_node in pattern_nodes:
            if pattern_node in nodes_map:
                continue
            for node in nodes:
                if node in nodes_map.values():
                    continue
                if not pattern_node.match(node, self._graph):
                    continue
                nodes_map[pattern_node] = node
                self.__nodes_group_dfs(nodes, pattern_nodes, nodes_map, nodes_map_group, get_next_func)
            if pattern_node in nodes_map:
                nodes_map.pop(pattern_node)
                continue
            if self._pattern.node_can_match_zero(pattern_node.op_name):
                # 节点没有成功匹配过，但节点可以匹配0次
                nodes_map[pattern_node] = None
                if not isinstance(get_next_func, types.MethodType):
                    continue
                # 根据回调函数获取pattern_node的前置节点或者后置节点
                new_pattern_nodes = get_next_func(pattern_node)
                if len(new_pattern_nodes) != 0:
                    pattern_nodes.extend(new_pattern_nodes)
                self.__nodes_group_dfs(nodes, pattern_nodes, nodes_map, nodes_map_group, get_next_func)
                nodes_map.pop(pattern_node)
                for nd in new_pattern_nodes:
                    pattern_nodes.remove(nd)

    def __match_nodes(self, nodes, pattern_nodes, result, get_next_func) -> bool:
        """
        对nodes和pattern_nodes进行匹配，并基于这些节点往上或者往下继续遍历
        :param nodes: 实际算子节点列表
        :param pattern_nodes: 算子节点列表，知识库中定义的算子节点
        :param result: 匹配结果
        :param get_next_func: 获取前置或者后置节点的方法
        :return: 匹配成功则返回True，失败返回False
        """
        if len(pattern_nodes) == 0:
            return True
        # 计算nodes和pattern_nodes所有可能存在的组合
        nodes_map = {}
        nodes_map_group = []
        self.__nodes_group_dfs(nodes, pattern_nodes, nodes_map, nodes_map_group, get_next_func)
        if len(nodes_map_group) == 0:
            return False
        # 逐个尝试nodes_groups匹配组合，只要有能成功完成子图匹配的组合，则匹配成功并且返回
        for nodes_map in nodes_map_group:
            if len(nodes_map) == 0:
                continue
            ret = True
            for pattern_node, node in nodes_map.items():
                if node is None:
                    continue
                ret = self.__graph_bfs(node, pattern_node, result)
                if not ret:
                    break
            if ret:
                return True
        return False

    def __match_continuous_same_nodes(self, nodes, pattern_node, result, callback) -> bool:
        """
        匹配连续的相同节点
        :param nodes: 实际算子节点列表
        :param pattern_node: 算子节点模板
        :param result: 匹配结果
        :param callback: 回调函数
        :return: 如果nodes中节点存在与pattern_node不匹配的节点，则返回False，需要进一步和pattern_node子节点或者父节点进行匹配
        """
        match_continuous_nodes = []
        for node in nodes:
            if not pattern_node.match(node, self._graph):
                continue
            if pattern_node.op_name not in result:
                result[pattern_node.op_name] = []
            result[pattern_node.op_name].append(node)
            if not isinstance(callback, types.MethodType):
                return False
            # 进一步匹配前置节点/后置节点
            if callback(node, pattern_node, result):
                match_continuous_nodes.append(node)
            else:
                result[pattern_node.op_name].remove(node)
        return len(match_continuous_nodes) == len(nodes)

    def __match_prev_nodes(self, node, pattern_node, result) -> bool:
        """
        匹配node前置节点
        :param node: 实际算子节点
        :param pattern_node: 算子节点模板
        :param result: 匹配结果
        :return: 匹配成功则返回True，否则返回False
        """
        prev_nodes = self.__get_prev_nodes(node)
        if self._pattern.node_can_match_more(pattern_node.op_name):
            if self.__match_continuous_same_nodes(prev_nodes, pattern_node, result, self.__match_prev_nodes):
                return True
        if len(pattern_node.inputs) == 0:
            return True
        return self.__match_nodes(prev_nodes, pattern_node.inputs, result, self.__get_prev_pattern_nodes)

    def __match_next_nodes(self, node, pattern_node, result) -> bool:
        """
        匹配node后置节点
        :param node: 实际算子节点
        :param pattern_node: 算子节点模板
        :param result: 匹配结果
        :return: 匹配成功则返回True，否则返回False
        """
        next_nodes = self._graph.get_next_nodes(node.outputs[0])
        if self._pattern.node_can_match_more(pattern_node.op_name):
            if self.__match_continuous_same_nodes(next_nodes, pattern_node, result, self.__match_next_nodes):
                return True
        if len(pattern_node.outputs) == 0:
            return True
        return self.__match_nodes(next_nodes, pattern_node.outputs, result, self.__get_next_pattern_nodes)

    def __graph_bfs(self, node, pattern_node, result) -> bool:
        """
        从node开始匹配子图，应用广度优先算法
        :param node: 实际算子节点
        :param pattern_node: 算子节点模板
        :param result: 匹配结果
        :return: 匹配成功则返回True，否则返回False
        """
        if not pattern_node.match(node, self._graph):
            return False
        if pattern_node.op_name in result:
            return True
        result[pattern_node.op_name] = [node]

        # 遍历前置节点
        ret = self.__match_prev_nodes(node, pattern_node, result)
        # 遍历后置节点
        ret &= self.__match_next_nodes(node, pattern_node, result)
        # 结果处理
        if not ret:
            result.pop(pattern_node.op_name)
        return ret

    def get_match_map(self, node) -> MatchResult:
        """
        获取匹配的节点列表
        :param node: 子图遍历起始节点
        :return: 匹配结果
        """
        result = MatchResult(self._pattern)
        start_pattern_node = self._pattern.get_start_node()
        if not start_pattern_node.match(node, self._graph):
            return result

        match_nodes = {}
        # 子图遍历
        if not self.__graph_bfs(node, start_pattern_node, match_nodes):
            return result
        result.add_node_dict(match_nodes)
        return result
