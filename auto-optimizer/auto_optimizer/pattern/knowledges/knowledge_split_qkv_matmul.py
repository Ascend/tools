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

from typing import List, Dict, Union
import operator as op
import logging

import numpy as np

from auto_optimizer.pattern.knowledge_factory import KnowledgeFactory
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode, Node, Initializer
from auto_optimizer.pattern.pattern import MATCH_PATTERN
from auto_optimizer.pattern.pattern import MatchBase
from auto_optimizer.pattern.pattern import Pattern
from auto_optimizer.pattern.matcher import MatchResult
from auto_optimizer.pattern.knowledges.knowledge_base import KnowledgeBase
from auto_optimizer.pattern.utils import NextNodeCount


class ConstSecondInput(MatchBase):
    # 限制节点的第二个输入参数为常数
    def __init__(self):
        super().__init__()

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        if not isinstance(node, (Node, )):
            return False
        input1 = graph.get_node(node.inputs[1], node_type=Initializer)
        return input1 is not None


class AllOutputsAreGatherMatch(MatchBase):
    # 限制节点的后置节点全部是Gather算子
    def __init__(self):
        super().__init__()

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        if not isinstance(node, (Node, )):
            return False
        nodes = graph.get_next_nodes(node.outputs[0])
        if not nodes:
            return False
        for n in nodes:
            if not (isinstance(n, (Node, )) and op.eq(n.op_type, 'Gather') and n.attrs.get('axis', None) == 0):
                return False
        return True


# QKV Slice 改图的简单图示，将MatMul到Transpose0的算子拆分为若干份，去掉Gather算子
# 如果Gather算子后面原本是Transpose算子，则去掉Gather后是两个连续的Transpose算子，可以合并
#
#      PreviousNode                                PreviousNode
#           |                                       /   |   \
#           |                                      /    |    \
#           |                                     /     |     \
#           |                                    /      |      \
#         MatMul                           MatMul0   MatMul1   MatMul2
#           |                  split         |          |           |
#      ElementWise(zero/more)  ====>  ElementWise0 ElementWise1 ElementWise2
#           |                                |          |           |
#        Reshape                          Reshape0   Reshape1    Reshape2
#           |                                |          |           |
#      Transpose0                    Transpose0_1  Transpose0_1  TransposeX(Transpose0_2+Transpose1)
#       /   |   \                            |          |           |
#      /    |    \                           |          |           |
#     /     |     \                          |          |           |
# Gather0 Gather1 Gather2                  Node0      Node1       Node2
#    |       |       |
#  Node0   Node1 Transpose1
#                    |
#                  Node2
#
# 尽量使用简单的pattern，将复杂的判断逻辑放在apply函数内
pattern0 = Pattern() \
    .add_node("MatMul_0", ["MatMul"], [NextNodeCount(1), ConstSecondInput()]) \
    .add_node('ElementWise_0', ['Mul', 'Add', 'Sub', 'Div'], [NextNodeCount(1)]) \
    .set_node_loop('ElementWise_0', MATCH_PATTERN.MATCH_ZERO_OR_MORE) \
    .add_edge("MatMul_0", "ElementWise_0") \
    .add_node("Reshape_0", ["Reshape"], [NextNodeCount(1), ConstSecondInput()]) \
    .add_edge("ElementWise_0", "Reshape_0") \
    .add_node("Transpose_0", ["Transpose"], [AllOutputsAreGatherMatch()]) \
    .add_edge("Reshape_0", "Transpose_0") \
    .set_input("MatMul_0") \
    .set_output("Transpose_0") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)


@KnowledgeFactory.register()
class KnowledgeSplitQKVMatmul(KnowledgeBase):
    """Split MatMul/Reshape/Transpose/Gathers Structure"""
    def __init__(self):
        super().__init__()
        # 注册pattern的apply方法
        self._register_apply_funcs(pattern0, [self._qkv_slice_apply])

    def __get_first_dim_of_split_after_reshape(self, size_of_dim_to_split: int, shape: np.ndarray) -> int:
        """
        计算矩阵乘法结果最后一个维度reshape后对应的首维度
        :param size_of_dim_to_split: 矩阵乘法结果最后一个维度的size
        :param shape: reshape算子的shape参数
        :return: 返回reshape后原来最后一个维度对应的首维度，当reshape不符合要求时返回-1

        假设矩阵乘法是(a,b)x(b,c), 结果为(a,c)，reshape算子将结果reshape为(d,e,...,n,k,...)
        这里需满足 c == n * k * ..., a == d * e * ... , 其中n对应c所在维度在reshape后的第一个维度
        """
        first_dim_of_split = len(shape)
        size_tmp = 1
        while size_tmp < size_of_dim_to_split and first_dim_of_split >= 0:
            size_tmp *= shape[first_dim_of_split - 1]
            first_dim_of_split -= 1
        return first_dim_of_split if size_tmp == size_of_dim_to_split else -1

    def __dup_branch_node(self, node: Node, graph: BaseGraph, weight: np.ndarray,
                          axis: int, num: int, indices: List[int], placeholder_index: int = 0) -> List[Node]:
        """
        复制逐元素算子和MatMul算子，这些算子的常数参数被切分为若干份，由各个分支平分
        :param node: 要复制的算子
        :param graph: 完整的图结构
        :param weight: 该算子的常数参数
        :param axis: 在哪个轴上进行复制
        :param num: 复制为几份
        :param indices: Gather节点对应的下标列表，决定参数的顺序
        :param placeholder_index: 节点的输入placeholder的下标
        :return: 返回复制完成的Node列表
        """
        ret = []
        op_type = node.op_type
        target_shape = list(weight.shape)
        target_shape[axis] = target_shape[axis] // num
        target_shape.insert(axis, num)
        weight = weight.reshape(target_shape)
        splitted_weight = np.split(weight, num, axis=axis)
        for idx in range(num):
            node_name = f"{node.name}_{idx}"
            init_name = f"{node_name}_init"
            node_weight = splitted_weight[indices[idx]].squeeze(axis)
            added_init = graph.add_initializer(
                name=init_name,
                value=node_weight
            )
            added_node = graph.add_node(
                name=node_name,
                op_type=op_type,
            )
            added_node.inputs = [added_init.name]
            added_node.inputs.insert(placeholder_index, "PlaceHolder")
            added_node.outputs = [f"{node_name}_output"]
            ret.append(added_node)
        return ret

    def __dup_reshape_node(self, node: Node, graph: BaseGraph, weight: np.ndarray, axis: int, num: int) -> List[Node]:
        """
        复制Reshape算子，Reshape算子的shape参数需要删除被拆分的轴，各个分支的shape参数是相同的
        :param node: 要复制的算子
        :param graph: 完整的图结构
        :param weight: 该算子的常数参数
        :param axis: 在哪个轴上进行复制
        :param num: 复制为几份
        :return: 返回复制完成的Node列表
        """
        ret = []
        op_type = node.op_type
        for idx in range(num):
            node_name = f"{node.name}_{idx}"
            init_name = f"{node_name}_init"
            node_weight = np.delete(weight.copy(), axis)
            added_init = graph.add_initializer(
                name=init_name,
                value=node_weight
            )
            added_node = graph.add_node(
                name=node_name,
                op_type=op_type,
            )
            added_node.inputs = ["PlaceHolder", added_init.name]
            added_node.outputs = [f"{node_name}_output"]
            ret.append(added_node)
        return ret

    def __dup_transpose_node(self, node: Node, graph: BaseGraph, perm: List[int], num: int) -> List[Node]:
        """
        复制Transpose算子，Transpose算子的perm属性需要重新计算，计算过程在外部
        :param node: 要复制的算子
        :param graph: 完整的图结构
        :param perm: 新的permutation
        :param num: 复制为几份
        :return: 返回复制完成的Node列表
        """
        ret = []
        for idx in range(num):
            node_name = f"{node.name}_{idx}"
            new_node = graph.add_node(
                name=node_name,
                op_type="Transpose",
                attrs={"perm": perm}
            )
            new_node.inputs = ["PlaceHolder"]
            new_node.outputs = [f"{node_name}_output"]
            ret.append(new_node)
        return ret

    def __reconnect_input_to_new_node(self, node_to_reconnect: Node, old_node: Node, new_node: Node):
        """
        将节点连接至新节点
        :param node_to_reconnect: 需要重新连接的节点
        :param old_node: 该节点之前连接的旧节点
        :param new_node: 该节点需要连接的新节点
        """
        for idx in range(len(node_to_reconnect.inputs)):
            if node_to_reconnect.inputs[idx] == old_node.outputs[0]:
                node_to_reconnect.inputs[idx] = new_node.outputs[0]

    def __connect_splitted_nodes(self, new_nodes: List[Node],
                                 pre_nodes: List[Union[Node, str]], placeholder_index: int = 0):
        """
        连接复制出来的新节点
        :param new_nodes: 本次需要连接的节点列表
        :param pre_nodes: 本次需要连接的节点的前驱节点或者placeholder名称列表
        :param placeholder_index: 节点的输入placeholder的下标
        """
        for idx, (node, pre_node) in enumerate(zip(new_nodes, pre_nodes)):
            node.inputs[placeholder_index] = pre_node.outputs[0] if isinstance(pre_node, (Node, )) else pre_node
            pre_nodes[idx] = node

    def __get_gather_nodes_indices(self, nodes: List[Node], graph: BaseGraph) -> List[int]:
        """
        获取Gather算子取的全部下标
        :param nodes: gather算子列表
        :param graph: 完整的图结构
        :return: 返回按gather节点顺序排列的下标列表
        """
        indices = []
        for n in nodes:
            indice = graph.get_node(n.inputs[1], node_type=Initializer)
            if indice is None or indice.value.size > 1:
                return []
            indices.append(int(indice.value))
        return indices

    def __split_branches(self, graph: BaseGraph, matchinfo: Dict[str, List[BaseNode]]) -> bool:
        """
        QKV Slice改图，将MatMul算子到Transpose算子拆分为若干份，去掉原本的Gather算子
        :param graph: 完整的图结构
        :param matchinfo: 匹配到的子图信息
        :return: 返回是否修改成功
        """
        if any(graph.get_node(node.name, node_type=Node) is None for nodes in matchinfo.values() for node in nodes):
            logging.info("Some matching node have been removed or renamed, failed to optimizd.")
            return False

        matmul_node = matchinfo['MatMul_0'][0]
        reshape_node = matchinfo['Reshape_0'][0]
        transpose_node = matchinfo['Transpose_0'][0]
        element_wise_nodes = matchinfo.get('ElementWise_0', [])

        # 矩阵乘法的被乘数和reshape算子的形状参数都必须是Initializer
        matmul_weight = graph.get_node(matmul_node.inputs[1], node_type=Initializer)
        resh_weight = graph.get_node(reshape_node.inputs[1], node_type=Initializer)
        if matmul_weight is None or resh_weight is None:
            logging.info("The multiplicand of MatMul or shape parameter of Reshape operator is not Initializer.")
            return False

        # 假设矩阵乘法是(a,b)x(b,c), 结果为(a,c)，reshape算子将结果reshape为(d,e,...,n,k,...)
        # 这里需满足 a == d * e * ... , c == n * k * ..., 其中n对应c维度在reshape后的第一个维度
        # n所在的维度之后由transpose算子移动到第一个维度，n与gather算子的数量相等
        # 该维度由多个gather平分，此时可以利用分块矩阵乘法将矩阵乘法分为n份，形成n个分支
        new_shape = resh_weight.value
        dim_to_split = matmul_weight.value.shape[-1]
        first_dim_of_split = self.__get_first_dim_of_split_after_reshape(dim_to_split, new_shape)
        if first_dim_of_split == -1:
            logging.info(f"The Reshape operator {reshape_node.name} does not meet specific requirement.")
            return False

        gather_nodes = graph.get_next_nodes(transpose_node.outputs[0])
        split_num = len(gather_nodes)

        perm = transpose_node.attrs.get('perm', [])
        if not perm or not isinstance(perm, (list, )) or perm[0] != first_dim_of_split:
            # reshape后(d,e,...n,k,r,...)中的n这个维度应该被transpose至最前面
            logging.info(f"The transpose operator {transpose_node.name} does not meet specific requirement.")
            return False

        if split_num != new_shape[perm[0]]:
            # gather算子的数量与transpose后数据首维度的size相等
            logging.info(f"The number of Gather operators {split_num} is not equal to {new_shape[perm[0]]}.")
            return False

        indices = self.__get_gather_nodes_indices(gather_nodes, graph)
        if sorted(indices) != [i for i in range(split_num)]:
            # 几个Gather算子的indices不重不漏的对应[0, n)，即平分首维度
            logging.info("The gather nodes does not split the first axis.")
            return False

        for node in element_wise_nodes:
            input0 = graph.get_node(node.inputs[0], node_type=Initializer)
            input1 = graph.get_node(node.inputs[1], node_type=Initializer)
            if not ((input0 is None) ^ (input1 is None)):
                logging.info(f"There should be exactly one Initializer parameter in Node {node.name}")
                # 所有逐元素运算算子都应该有且仅有一个参数是Initializer，另一个参数是PlaceHolder
                return False

        # 拆分之后，必须更新被拆分的transpose算子的perm属性，如[2, 0, 3, 1, 4] -> [0, 2, 1, 3]
        splitted_perm = [p if p < first_dim_of_split else p - 1 for p in perm[1:]]

        for gather_node in gather_nodes:
            for next_node in graph.get_next_nodes(gather_node.outputs[0]):
                if not isinstance(next_node, (Node, )):
                    logging.info(f"Successor {next_node.name} of {gather_node.name} is not type Node.")
                    return False
                if op.eq(next_node.op_type, "Transpose"):
                    perm1 = next_node.attrs.get("perm", [])
                    if not (isinstance(perm1, (list, )) and len(splitted_perm) == len(perm1)):
                        logging.info(f"The perm attribute of transpose operator {next_node.name} is invalid.")
                        return False
                    for node in graph.get_next_nodes(next_node.outputs[0]):
                        if not isinstance(node, (Node, )):
                            logging.info(f"Node {node.name} is not type Node.")
                            return False

        # pre_nodes用来存储前置节点，用于重新连接
        pre_node = graph.get_prev_node(matmul_node.inputs[0])
        if isinstance(pre_node, (Node, )) and pre_node.outputs[0] != matmul_node.inputs[0]:
            logging.info("The output of previous node of MatMul doesn't match the input of MatMul.")
            return False
        pre_nodes = [matmul_node.inputs[0] if pre_node is None else pre_node] * split_num

        # 执行到这里已经完全确认可以做优化，接下来开始改图，防止出现改图到一半发现无法继续修改的情况
        matmul_weight_length = len(matmul_weight.value.shape)
        new_matmuls = self.__dup_branch_node(matmul_node, graph, matmul_weight.value,
                                             matmul_weight_length - 1, split_num, indices)
        self.__connect_splitted_nodes(new_matmuls, pre_nodes)

        for node in element_wise_nodes:
            input0 = graph.get_node(node.inputs[0], node_type=Initializer)
            input1 = graph.get_node(node.inputs[1], node_type=Initializer)
            # 由于这两个参数可以互换，我们改图时需要判断具体哪个是Initializer
            node_weight = input0 if input1 is None else input1
            placeholder_index = 1 if input1 is None else 0
            matmul_weight_length = len(node_weight.value.shape)
            new_nodes = self.__dup_branch_node(node, graph, node_weight.value,
                                               matmul_weight_length - 1, split_num, indices, placeholder_index)
            self.__connect_splitted_nodes(new_nodes, pre_nodes, placeholder_index)

        new_reshapes = self.__dup_reshape_node(reshape_node, graph, resh_weight.value, first_dim_of_split, split_num)
        self.__connect_splitted_nodes(new_reshapes, pre_nodes)

        new_transposes = self.__dup_transpose_node(transpose_node, graph, splitted_perm, split_num)
        self.__connect_splitted_nodes(new_transposes, pre_nodes)

        for new_transpose, gather_node in zip(new_transposes, gather_nodes):
            for next_node in graph.get_next_nodes(gather_node.outputs[0]):
                if op.ne(next_node.op_type, "Transpose"):
                    # 如果gather节点后面不是Transpose节点，只需要删除该gather节点，重新连接其余节点
                    # 删除统一在最后进行
                    self.__reconnect_input_to_new_node(
                        node_to_reconnect=next_node,
                        old_node=gather_node,
                        new_node=new_transpose
                    )
                    continue

                # 如果gather节点后面是Transpose节点
                # 则去除gather后是两个连续的Transpose节点，可以进行合并
                # 这里new_transpose在old_transpose的前面
                perm0 = new_transpose.attrs.get("perm", [])
                perm1 = next_node.attrs.get("perm", [])
                new_perm = [perm0[p] for p in perm1]
                new_transpose.attrs["perm"] = new_perm
                for node in graph.get_next_nodes(next_node.outputs[0]):
                    self.__reconnect_input_to_new_node(
                        node_to_reconnect=node,
                        old_node=next_node,
                        new_node=new_transpose
                    )
                graph.remove(next_node.name, {})

        # 删除旧节点
        for name in [node.name for node in gather_nodes]:
            graph.remove(name, {})
        graph.remove(transpose_node.name, {})
        graph.remove(reshape_node.name, {})
        for name in [node.name for node in element_wise_nodes]:
            graph.remove(name, {})
        graph.remove(matmul_node.name, {})
        graph.update_map()
        return True

    def _qkv_slice_apply(self, graph: BaseGraph, match_result: MatchResult) -> bool:
        flag = False
        for matchinfo in match_result.node_dicts:
            if matchinfo:
                flag |= self.__split_branches(graph, matchinfo)
        return flag
