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
import numpy as np

from auto_optimizer.pattern.knowledge_factory import KnowledgeFactory
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode, Node, Initializer
from auto_optimizer.pattern.pattern import MATCH_PATTERN, MatchBase, Pattern
from auto_optimizer.pattern.matcher import MatchResult
from auto_optimizer.pattern.knowledges.knowledge_base import KnowledgeBase
from auto_optimizer.pattern.utils import NextNodeCount


class NonNegetiveAxes(MatchBase):
    # the axes to be sliced should not be negetive
    # as we need infershape to determine if some negetive axis is the same with positive axis
    # in reallity, a lot of models failed to infershape, so we add this constraint here
    def __init__(self):
        super().__init__()

    def match(self, node: BaseNode, graph: BaseGraph) -> bool:
        if not isinstance(node, (Node, )):
            return False
        if len(node.inputs) < 4:
            return False
        axes = graph.get_node(node.inputs[3], node_type=Initializer)
        return axes is not None and all(v >= 0 for v in axes.value)


# continue 4 slice op
r"""

       X
       |
       |
    Slice_0
       |
       |                      X
    Slice_1     Merge         |
       |       ======>        |
       |                Slice_to_keep
    Slice_2
       |
       |
 Slice_to_keep


"""
pattern0 = Pattern() \
    .add_node("Slice_0", ["Slice"], [NonNegetiveAxes(), NextNodeCount(1)]) \
    .add_node("Slice_1", ["Slice"], [NonNegetiveAxes(), NextNodeCount(1)]) \
    .add_node("Slice_2", ["Slice"], [NonNegetiveAxes(), NextNodeCount(1)]) \
    .add_node("Slice_to_keep", ["Slice"], [NonNegetiveAxes()]) \
    .add_edge("Slice_0", "Slice_1") \
    .add_edge("Slice_1", "Slice_2") \
    .add_edge("Slice_2", "Slice_to_keep") \
    .set_input("Slice_0") \
    .set_output("Slice_to_keep") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)

# continue 3 slice op
r"""

       X
       |
       |
    Slice_0                    X
       |         Merge         |
       |        ======>        |
    Slice_1              Slice_to_keep
       |
       |
 Slice_to_keep


"""
pattern1 = Pattern() \
    .add_node("Slice_0", ["Slice"], [NonNegetiveAxes(), NextNodeCount(1)]) \
    .add_node("Slice_1", ["Slice"], [NonNegetiveAxes(), NextNodeCount(1)]) \
    .add_node("Slice_to_keep", ["Slice"], [NonNegetiveAxes()]) \
    .add_edge("Slice_0", "Slice_1") \
    .add_edge("Slice_1", "Slice_to_keep") \
    .set_input("Slice_0") \
    .set_output("Slice_to_keep") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)

# continue 2 slice op
r"""

       X
       |                       X
       |         Merge         |
    Slice_0     ======>        |
       |                 Slice_to_keep
       |
 Slice_to_keep

"""
pattern2 = Pattern() \
    .add_node("Slice_0", ["Slice"], [NonNegetiveAxes(), NextNodeCount(1)]) \
    .add_node("Slice_to_keep", ["Slice"], [NonNegetiveAxes()]) \
    .add_edge("Slice_0", "Slice_to_keep") \
    .set_input("Slice_0") \
    .set_output("Slice_to_keep") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)


@KnowledgeFactory.register()
class KnowledgeMergeConsecutiveSlice(KnowledgeBase):
    """Combine consecutive slice operators together"""
    def __init__(self):
        super().__init__()
        # 注册pattern的apply方法
        self._register_apply_funcs(pattern0, [self._merge_continue_slice_apply])
        self._register_apply_funcs(pattern1, [self._merge_continue_slice_apply])
        self._register_apply_funcs(pattern2, [self._merge_continue_slice_apply])

    def merge_slice_nodes(self, graph: BaseGraph, matchinfo: Dict[str, List[BaseNode]]) -> bool:
        # get slice operators here, we only kept the last slice operator after optimization
        slice_to_keep = graph.get_node(matchinfo['Slice_to_keep'][0].name, node_type=Node)
        slices_to_remove = [
            graph.get_node(v[0].name, node_type=Node) for k, v in matchinfo.items() if k != 'Slice_to_keep'
        ]
        slices_total = [*slices_to_remove, slice_to_keep]
        # in case previous apply functions modified the graph and removed/renamed any node of current matching subgraph
        if any(node is None for node in slices_total):
            logging.info("Some matching node have been removed or renamed, failed to optimizd.")
            return False

        input_initializers = [
            [
                graph.get_node(inp, node_type=Initializer) for inp in node.inputs[1:]
            ] for node in slices_total
        ]
        if any(inp is None for inp in input_initializers):
            logging.info("Failed to get slices parameters.")
            return False
        input_values = [[inp.value for inp in lst] for lst in input_initializers]
        # add optional steps input, input_values should look like this now
        # for example: [[start0, end0, axes0, step0], [start1, end1, axes1, step1], ...]
        input_values = [lst if len(lst) > 3 else lst + [np.array([1])] for lst in input_values]
        # after transposed -> [[start0, start1, ...], [end0, end1, ...], [axes0, axes1, ...], [step0, step1, ...]]
        input_values = list(zip(*input_values))

        # duplicate axes means we can't merge these slice nodes together
        axes_to_merge = np.concatenate(input_values[2])
        if np.unique(axes_to_merge).size != axes_to_merge.size:
            logging.info(f"Slice nodes have duplicate slice axis: {axes_to_merge}")
            return False

        # we start modify the graph from here, as all validations are finished so we can make sure optimize will success
        # remove all other slice nodes except the last one
        for node in slices_to_remove:
            graph.remove(node.name)

        # construct new initializers and replace the inputs of last slice node with them
        for i, param in enumerate(["starts_", "ends_", "axes_", "steps_"]):
            new_input = graph.add_initializer(
                name=param + "_".join(node.name for node in slices_total),
                value=np.concatenate(input_values[i])
            )
            # the first input of slice operator is input data, so off by 1
            slice_to_keep.inputs[i + 1] = new_input.name
        graph.update_map()
        return True

    def _merge_continue_slice_apply(self, graph: BaseGraph, match_result: MatchResult) -> bool:
        flag = False
        for matchinfo in match_result.node_dicts:
            if matchinfo:
                flag |= self.merge_slice_nodes(graph, matchinfo)
        return flag
