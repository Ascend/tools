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

from ctypes import cast
from typing import List, Dict
import operator as op
from enum import Enum
from itertools import chain
import numpy as np
from onnx.onnx_cpp2py_export.shape_inference import InferenceError

from auto_optimizer.pattern.knowledge_factory import KnowledgeFactory
from auto_optimizer.pattern.knowledges.knowledge_base import KnowledgeBase
from auto_optimizer.pattern.pattern import MatchBase
from auto_optimizer.pattern.pattern import MATCH_PATTERN
from auto_optimizer.pattern.pattern import Pattern
from auto_optimizer.pattern.matcher import MatchResult
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode, Initializer, Node


class ElemType(Enum):
    FLOAT32    = 1
    UINT8      = 2
    INT8       = 3
    UINT16     = 4
    INT16      = 5
    INT32      = 6
    INT64      = 7
    STRING     = 8
    BOOLEAN    = 9
    FLOAT16    = 10
    FLOAT64    = 11
    UINT32     = 12
    UINT64     = 14
    COMPLEX128 = 15
    BFLOAT16   = 16

numpy_onnx_type_map = \
    { np.int32   : ElemType.INT32
    , np.int64   : ElemType.INT64
    , np.float32 : ElemType.FLOAT32
    , np.float64 : ElemType.FLOAT64
    }

class TypeCastStrategy(object):
    """ 类型转换策略
    将一个原始的数据类型转换到目标类型的过程描述为一个类型转换策略
    """
    def __init__(self, cast_from: np.dtype, cast_to: np.dtype):
        """
        :param cast_from: 原始数据类型
        :param cast_to  : 目标数据类型  
        """
        self._cast_from = cast_from
        self._cast_to   = cast_to

    @property
    def cast_from(self):
        return self._cast_from
    
    @property
    def cast_to(self):
        return self._cast_to

class IOType(Enum):
    """ 节点输入输出类型枚举
    """
    NODE_INPUT  = 0 # 节点输入
    NODE_OUTPUT = 1 # 节点输出

class GenericIO(object):
    """ 节点支持泛型的输入输出
    描述节点支持泛型的输入输出的索引列表
    """
    def __init__(self, generic_inputs: List[int], generic_outputs: List[int]):
        """
        :param generic_inputs  : 泛型输入索引列表
        :param generic_outputs : 泛型输出索引列表
        """
        self._generic_inputs  = generic_inputs
        self._generic_outputs = generic_outputs
    
    @property
    def generic_inputs(self):
        return self._generic_inputs
    
    @property
    def generic_outputs(self):
        return self._generic_outputs

class GenericOpMatch(MatchBase):
    """ 泛型节点匹配
    """

    # 完全泛型节点，此类节点的所有输入输出均为泛型类型，对于此类节点可以将所有满足转换
    # 原始类型的输入输出转换为目标类型
    entire_generic_ops = \
        [ 'Mul'
        , 'Add'
        , 'Sub'
        , 'Div'
        , 'Abs'
        , 'Tanh'
        , 'LeakyRelu'
        , 'Relu'
        , 'Sigmoid'
        , 'BatchNormalization'
        , 'ReduceSum'
        , 'Concat'
        , 'Gemm'
        , 'Split'
        , 'Slice'
        , 'Transpose'
        ]

    # 半泛型节点，部分输入通道类型为泛型 T，剩余输入通道类型为固定类型，对于此类算子需
    # 要将泛型的输入通道转换为目标类型
    partial_generic_ops = \
        { 'Expand'   : GenericIO([0], [0])
        , 'Less'     : GenericIO([0, 1], [])
        , 'Gather'   : GenericIO([0], [0])
        , 'Shape'    : GenericIO([0], [])
        , 'Where'    : GenericIO([1, 2], [0])
        , 'Equal'    : GenericIO([0, 1], [])
        , 'Reshape'  : GenericIO([0], [0])
        , 'Tile'     : GenericIO([0], [0])
        , 'ScatterND': GenericIO([0, 2], [0])
        , 'Unsqueeze': GenericIO([0], [0])
        , 'Squeeze'  : GenericIO([0], [0])
        }

    def __init__(self, strategy: TypeCastStrategy):
        """
        :param strategy: 类型转换策略
        """
        super().__init__()
        self._strategy = strategy

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        """ 节点匹配实现函数
        :param node : 匹配节点
        :param graph: 整图
        :return     : 是否匹配成功
        """
        elem_type = numpy_onnx_type_map.get(self._strategy.cast_to, 0)
        if node.op_type == 'Cast' and node['to'] == elem_type.value:
            return False
        return self._match_cast_from_input(node, graph)

    @classmethod
    def is_generic_io(cls, node: BaseNode, io_type: IOType, io_index: int) -> bool:
        """ 检查节点输入输出是否支持泛型
        :param node     : 待检查节点对象
        :param io_type  : 检查输入或输出
        :param io_index : 检查的输入输出通道
        :return         : 指定通道是否支持泛型
        """
        if node.op_type in cls.entire_generic_ops:
            return True
        if node.op_type in cls.partial_generic_ops:
            generic_io = cls.partial_generic_ops[node.op_type]
            if io_type == IOType.NODE_INPUT:
                return io_index in generic_io.generic_inputs
            if io_type == IOType.NODE_OUTPUT:
                return io_index in generic_io.generic_outputs
        return False

    def _match_cast_from_input(self, node: BaseNode, graph: BaseGraph) -> bool:
        """ 通过检查节点泛型输入对节点进行匹配
        :param node  : 待检查节点对象
        :param graph : 整图对象
        :return      : 是否匹配成功
        """
        # 生成所有边的数据类型信息
        edge_type_dict = {}
        for edge in graph.value_infos:
            edge_type_dict[edge.name] = edge.dtype
        for input_node in graph.inputs:
            edge_type_dict[input_node.name] = input_node.dtype
        for output_node in graph.outputs:
            edge_type_dict[output_node.name] = output_node.dtype
        for initializer in graph.initializers:
            edge_type_dict[initializer.name] = initializer.value.dtype

        # 至少要有一个泛型输入是转换原始类型才能匹配成功
        for index, node_input in enumerate(node.inputs):
            if GenericOpMatch.is_generic_io(node, IOType.NODE_INPUT, index) \
                and edge_type_dict.get(node_input, 0) == self._strategy.cast_from:
                return True
        return False

class TypeCastPattern(Pattern):
    """ 可进行类型转换的子图匹配模式
    数据类型转换改图知识库的基本原理，以 int64 -> int32 转换进行说明：
    1. 确定可进行类型转换的节点：基本思路为找到所有泛型节点，并且支持泛型的输入输出通道
       需要满足类型转换的原始类型（int64）
    2. 根据连接性判断将节点分为多个子图
    3. 类型转换的核心思想是将子图中的 int64 张量流转换为 int32 类型，张量流入子图时通
       过 Cast 算子转换为 int32 类型，流出子图时重新转换为 int64 类型，保证子图的修改
       不影响整图功能
    """
    def __init__(self, strategy: TypeCastStrategy):
        super().__init__()
        self.add_node('generic_operator', None, [GenericOpMatch(strategy)]) \
            .set_input('generic_operator') \
            .set_output('generic_operator') \
            .set_node_loop('generic_operator', MATCH_PATTERN.MATCH_ONCE_OR_MORE) \
            .set_loop(MATCH_PATTERN.MATCH_ONCE_OR_MORE)

class TypeCastApply(object):
    def __init__(self, strategy: TypeCastStrategy):
        self._strategy = strategy
        self._inserted_node_name = set()

    def __call__(self, graph: BaseGraph, match_result: MatchResult) -> bool:
        """ 类型转换应用方法
        :param graph       : 整图
        :param match_result: 子图匹配结果
        :return            : 类型转换是否应用成功
        """
        node_map = {}
        # 构建子图节点映射
        for node_dict in match_result.node_dicts:
            for nodes in node_dict.values():
                for node in nodes:
                    node_map[node.name] = node

        # 构建边名与数据类型的映射表
        edge_type_dict = self._make_edge_type_dict(graph)

        self._cast_subgraph_inputs(graph, node_map, edge_type_dict)
        self._cast_subgraph_outputs(graph, node_map, edge_type_dict)

        return True

    def _cast_subgraph_inputs(self, graph: BaseGraph, node_map, edge_type_dict):
        """ 将子图输入转换为目标类型
        :param graph         : 整图
        :param node_map      : 子图节点表
        :param edge_type_dict: 边名与数据类型的映射表
        """
        const_map = dict([(initializer.name, initializer) for initializer in graph.initializers])
        cast_from = self._strategy.cast_from
        cast_to   = self._strategy.cast_to

        # 遍历子图中的所有节点
        for node in node_map.values():
            # 处理节点输入
            for input_index, node_input in enumerate(node.inputs):
                # 如果当前输入不能泛型则不处理
                if not GenericOpMatch.is_generic_io(node, IOType.NODE_INPUT, input_index):
                    continue
                # 当前输入类型不为转换原始类型时不处理
                if edge_type_dict.get(node_input, 0) != cast_from:
                    continue

                # 常量输入直接对 initializer 节点的数据类型进行转换
                if node_input in const_map:
                    self._const_type_cast(graph, node, input_index, const_map, cast_to)
                    continue

                # 前置节点为子图外部节点或前置节点的当前输出为非泛型输出，则将需要将输入转换为目标类型
                prev_node = graph.get_prev_node(node_input)
                if prev_node:
                    output_index = prev_node.outputs.index(node_input)
                    _is_generic_output = GenericOpMatch.is_generic_io(prev_node, IOType.NODE_OUTPUT, output_index)
                    if prev_node.name not in node_map or not _is_generic_output:
                        # 如果前置节点当前输出通道后面存在转换到目标类型的 Cast 节点时，复用此节点
                        next_nodes = graph.get_next_nodes(node_input)
                        casts = list(filter(lambda node: node.op_type == 'Cast' and \
                            node['to'] == numpy_onnx_type_map.get(cast_to, 0), next_nodes))
                        if casts:
                            graph[node.name].inputs[input_index] = casts[0].outputs[0]
                            graph.update_map()
                        else:
                            self._insert_cast_node(graph, node, 'before', input_index, cast_to)
                    continue

                for input_node in graph.inputs:
                    if node_input == input_node.name:
                        self._insert_cast_node(graph, node, 'before', input_index, cast_to)

    def _cast_subgraph_outputs(self, graph, node_map, edge_type_dict):
        """ 将子图输出转换为原始类型
        :param graph         : 整图
        :param node_map      : 子图节点表
        :param edge_type_dict: 边名与数据类型的映射表
        """
        cast_from = self._strategy.cast_from

        # 遍历子图中的所有节点
        for node in node_map.values():
            # 处理节点输出
            for output_index, node_output in enumerate(node.outputs):
                # 如果当前输出不能泛型则不处理
                if not GenericOpMatch.is_generic_io(node, IOType.NODE_OUTPUT, output_index):
                    continue
                # 当前输出类型不为转换原始类型时不处理
                if edge_type_dict.get(node_output, 0) != cast_from:
                    continue

                # 查找后继节点
                next_nodes = graph.get_next_nodes(node_output).copy()

                cast_node = None
                for next_node in next_nodes:
                    input_index = next_node.inputs.index(node_output)
                    # 后继节点为子图外部节点或后继节点当前的输入为非泛型输入，则需要将当前节点输出转回原始类型
                    _is_generic_input = GenericOpMatch.is_generic_io(next_node, IOType.NODE_INPUT, input_index)
                    if next_node.name not in node_map or not _is_generic_input:
                        # 后继节点为 Cast 节点时再插入 Cast 节点没有意义
                        if next_node.op_type == 'Cast':
                            continue
                        # 复用 Cast 节点
                        if cast_node is not None:
                            next_node.inputs[input_index] = cast_node.outputs[0]
                            graph.update_map()
                            continue
                        _cast_node = self._insert_cast_node(graph, next_node, 'before', input_index, cast_from)
                        # 更新复用的 Cast 记录
                        if _cast_node is not None:
                            cast_node = _cast_node

                # 节点输出为图输出时转换为原始类型再输出
                for output_node in graph.outputs:
                    if node_output == output_node.name:
                        self._insert_cast_node(graph, output_node, 'before', 0, cast_from)

    def _make_edge_type_dict(self, graph: BaseGraph) -> Dict[str, np.dtype]:
        """ 构建边名与数据类型的映射表
        :param graph: 构建映射表的整图
        :return     : 边名与数据类型的映射表
        """
        edge_type_dict = {}
        for edge in chain(graph.value_infos, graph.inputs, graph.outputs):
            edge_type_dict[edge.name] = edge.dtype
        for initializer in graph.initializers:
            edge_type_dict[initializer.name] = initializer.value.dtype
        return edge_type_dict

    def _insert_cast_node(self, graph: BaseGraph, node: BaseNode,
                          mode: str, refer_index, cast_to: np.dtype) -> BaseNode:
        """ 插入类型转换节点
        :param graph      : 待插入节点整图
        :param node       : 参考节点
        :param mode       : 插入模式之前或之后
        :param refer_index: 插入节点在参考节点的输入输出索引
        :param cast_to    : 转换类型
        :return           : 插入的节点对象
        """
        elem_type = numpy_onnx_type_map.get(cast_to, 0)
        op_name = f'Cast_{mode}_{node.name}_{refer_index}'
        if op_name in self._inserted_node_name:
            return None
        self._inserted_node_name.add(op_name)
        cast = graph.add_node(op_name, 'Cast', attrs={'to': elem_type.value})
        graph.insert_node(node.name, cast, mode=mode, refer_index=refer_index)
        graph.update_map()
        return cast

    def _value_type_cast(self, node: BaseNode, cast_to: np.dtype) -> BaseNode:
        """ 节点数据类型转换
        :param node   : 待转换节点
        :param cast_to: 转换类型
        :return       : 转换完成的节点
        """
        # 使用类型对应的信息获取方法
        if np.issubdtype(cast_to, np.integer):
            get_info = np.iinfo
        elif np.issubdtype(cast_to, np.floating):
            get_info = np.finfo
        else:
            return node

        type_max = get_info(cast_to).max
        type_min = get_info(cast_to).min
        value = node.value.copy()
        if (value > type_max).any():
            value[value > type_max] = type_max
        if (value < type_min).any():
            value[value < type_min] = type_min
        node.value = value.astype(cast_to)
        return node

    def _const_type_cast(self, graph: BaseGraph, node: BaseNode, input_index, const_map, cast_to: np.dtype):
        """ 常量输入类型转换
        :param graph      : 整图
        :param node       : 常量输入的算子节点
        :param input_index: 常量输入的通道索引
        :param const_map  : 常量输入映射表
        :param cast_to    : 转换目标类型
        """
        const_input = node.inputs[input_index]
        if const_input not in node.inputs or const_input not in const_map:
            return

        const_node = const_map[const_input]
        if const_node.value.dtype == cast_to:
            return

        # 如果常量输入后面任意一个节点输入不支持泛型则不能直接将常量进行类型转换
        next_nodes = graph.get_next_nodes(const_node.name)
        cast_const_directly = True
        for next_node in next_nodes:
            next_input_index = next_node.inputs.index(const_node.name)
            if not GenericOpMatch.is_generic_io(next_node, IOType.NODE_INPUT, next_input_index):
                cast_const_directly = False
                break

        # 直接对常量输入进行类型转换
        if cast_const_directly:
            self._value_type_cast(const_node, cast_to)
            return

        # 构造的新常量输入节点的名字
        new_const_name = f'{const_node.name}_{numpy_onnx_type_map.get(cast_to, 0).name}'
        if new_const_name in const_map:
            return

        new_const_node = graph.add_initializer(new_const_name, const_node.value.copy())
        const_map[new_const_name] = new_const_node
        self._value_type_cast(new_const_node, cast_to)
        graph[node.name].inputs[input_index] = new_const_name
        graph.update_map()


@KnowledgeFactory.register()
class KnowledgeTypeCast(KnowledgeBase):
    def __init__(self):
        super().__init__()
        # 类型转换策略列表
        self._type_cast_strategies = \
            [ TypeCastStrategy(cast_from=np.int64,   cast_to=np.int32)
            , TypeCastStrategy(cast_from=np.float64, cast_to=np.float32)
            ]
        for strategy in self._type_cast_strategies:
            self._register_apply_funcs(TypeCastPattern(strategy), [TypeCastApply(strategy)])

    def pre_process(self, graph: BaseGraph) -> bool:
        try:
            graph.infershape()
        except InferenceError as e:
            return False
        return True

    def post_process(self, graph: BaseGraph) -> bool:
        return self.pre_process(graph)
