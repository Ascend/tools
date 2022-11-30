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

import sys
import argparse

from .graph_optimizer.optimizer import GraphOptimizer
from .graph_refactor.onnx.graph import OnnxGraph

def _opt_parser(opt_parser):
    opt_parser.add_argument('input_model', help='Input model path')
    opt_parser.add_argument('output_model', help='Output model path')
    opt_parser.add_argument('-k', '--knowledge', type=str, 
                            metavar='knowledge_names', nargs='+', help='name of knwoledges')

def main():
    parser = argparse.ArgumentParser(description='AutoOptimizer')

    subparsers = parser.add_subparsers(help='commands')
    opt_parser = subparsers.add_parser('opt', help='optimize graph')

    _opt_parser(opt_parser)

    args = parser.parse_args()

    cmd = sys.argv[1]
    if cmd == 'opt':
        knwoledges = args.knowledge
        if knwoledges:
            graph_opt = GraphOptimizer(knwoledges)
            graph = OnnxGraph.parse(args.input_model)
            graph_opt.apply_knowledges(graph)
            graph.save(args.output_model)

if __name__ == "__main__":
    main()