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

from auto_optimizer.pattern.knowledge_factory import KnowledgeFactory
from auto_optimizer.graph_refactor.interface.base_graph import BaseGraph
from auto_optimizer.graph_refactor.interface.base_node import BaseNode, Node
from auto_optimizer.pattern.pattern import MATCH_PATTERN, Pattern
from auto_optimizer.pattern.matcher import MatchResult
from auto_optimizer.pattern.knowledges.knowledge_base import KnowledgeBase
from auto_optimizer.pattern.utils import NextNodeCount


# continue 4 Concat op
r"""

   A          B
    \        /
     \      /
      \    /
     Concat_0      C
         \        /                        A   B     C     D   E
          \      /                          \   \    |    /   /
           \    /                Merge       \   \   |   /   /
          Concat_1      D        ======>      \   \  |  /   /
              \        /                      Concat_to_keep
               \      /
                \    /
               Concat_2      E
                   \        /
                    \      /
                     \    /
                  Concat_to_keep

"""
pattern0 = Pattern() \
    .add_node("Concat_0", ["Concat"], [NextNodeCount(1)]) \
    .add_node("Concat_1", ["Concat"], [NextNodeCount(1)]) \
    .add_node("Concat_2", ["Concat"], [NextNodeCount(1)]) \
    .add_node("Concat_to_keep", ["Concat"]) \
    .add_edge("Concat_0", "Concat_1") \
    .add_edge("Concat_1", "Concat_2") \
    .add_edge("Concat_2", "Concat_to_keep") \
    .set_input("Concat_0") \
    .set_output("Concat_to_keep") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)

# continue 3 Concat op
r"""

   A          B
    \        /
     \      /
      \    /                            A   B         C    D
     Concat_0      C                     \   \       /    /
         \        /           Merge       \   \     /    /
          \      /            ======>      \   \   /    /
           \    /                          Concat_to_keep
          Concat_1      D
              \        /
               \      /
                \    /
             Concat_to_keep

"""
pattern1 = Pattern() \
    .add_node("Concat_0", ["Concat"], [NextNodeCount(1)]) \
    .add_node("Concat_1", ["Concat"], [NextNodeCount(1)]) \
    .add_node("Concat_to_keep", ["Concat"]) \
    .add_edge("Concat_0", "Concat_1") \
    .add_edge("Concat_1", "Concat_to_keep") \
    .set_input("Concat_0") \
    .set_output("Concat_to_keep") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)

# continue 2 Concat op
r"""

   A          B
    \        /                      A     B     C
     \      /                        \    |    /
      \    /            Merge         \   |   /
     Concat_0      C    ======>        \  |  /
         \        /                 Concat_to_keep
          \      /
           \    /
        Concat_to_keep

"""
pattern2 = Pattern() \
    .add_node("Concat_0", ["Concat"], [NextNodeCount(1)]) \
    .add_node("Concat_to_keep", ["Concat"]) \
    .add_edge("Concat_0", "Concat_to_keep") \
    .set_input("Concat_0") \
    .set_output("Concat_to_keep") \
    .set_loop(MATCH_PATTERN.MATCH_ONCE)


@KnowledgeFactory.register()
class KnowledgeMergeConsecutiveConcat(KnowledgeBase):
    """Combine consecutive concat operators together"""
    def __init__(self):
        super().__init__()

        # 注册pattern的apply方法
        self._register_apply_funcs(pattern0, [self._merge_continue_concat_apply])
        self._register_apply_funcs(pattern1, [self._merge_continue_concat_apply])
        self._register_apply_funcs(pattern2, [self._merge_continue_concat_apply])

    def merge_concat_nodes(self, graph: BaseGraph, matchinfo: Dict[str, List[BaseNode]]) -> bool:
        # get concats operators here, we only kept the last concat operator after optimization
        concat_to_keep = graph.get_node(matchinfo['Concat_to_keep'][0].name, node_type=Node)
        concats_to_remove = [
            graph.get_node(v[0].name, node_type=Node) for k, v in matchinfo.items() if k != 'Concat_to_keep'
        ]
        concats_total = [*concats_to_remove, concat_to_keep]
        # in case previous apply functions modified the graph and removed/renamed any node of current matching subgraph
        if any(node is None for node in concats_total):
            logging.info("Some matching node have been removed or renamed, failed to optimizd.")
            return False
        # the axis attr of all concat nodes should be the same to be merged
        if len(set(node.attrs.get('axis', -1) for node in concats_total)) != 1:
            logging.info("Matching nodes have different axes.")
            return False

        # collect all outputs of concat operators about to remove,
        # these output should be removed if they are in the new input list
        # since their corresponding node are about to be removed, all other inputs should be kept
        outputs_of_concats_to_remove = [node.outputs[0] for node in concats_to_remove]
        new_inputs = [inp for node in concats_total for inp in node.inputs if inp not in outputs_of_concats_to_remove]

        # we start modify the graph from here, as all validations are finished so we can make sure optimize will success
        # remove all the nodes except the last one, and give all input to the last concat node
        for node in concats_to_remove:
            graph.remove(node.name, {})
        concat_to_keep.inputs = new_inputs
        graph.update_map()
        return True

    def _merge_continue_concat_apply(self, graph: BaseGraph, match_result: MatchResult) -> bool:
        flag = False
        for matchinfo in match_result.node_dicts:
            if matchinfo:
                flag |= self.merge_concat_nodes(graph, matchinfo)
        return flag
