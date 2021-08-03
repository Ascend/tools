/* Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
#include "tensorflow/core/common_runtime/function_body.h"
#include "tensorflow/core/common_runtime/function_def_utils.h"
#include "tensorflow/core/common_runtime/optimization_registry.h"
#include "tensorflow/core/framework/graph_to_functiondef.h"
#include "tensorflow/core/graph/node_builder.h"
#include "tensorflow/core/platform/logging.h"

namespace tensorflow {

class DbgDumpPass : public GraphOptimizationPass {
 public:
  DbgDumpPass() = default;
  ~DbgDumpPass() override = default;
  Status Run(const GraphOptimizationPassOptions &options) override;

 private:
  Status ProcessGraph(Graph *graph, FunctionLibraryDefinition *func_lib, std::string prefix = "");
};

Status DbgDumpPass::Run(const GraphOptimizationPassOptions &options) {
  if (options.graph == nullptr && options.partition_graphs == nullptr) {
    return Status::OK();
  }

  FunctionLibraryDefinition *func_lib = options.flib_def;
  Status status = Status::OK();
  if (options.graph != nullptr) {
    std::unique_ptr<Graph> *graph = options.graph;
    TF_RETURN_IF_ERROR(ProcessGraph((*graph).get(), func_lib));
  } else if (options.partition_graphs != nullptr) {
    for (auto &pg : *options.partition_graphs) {
      TF_RETURN_IF_ERROR(ProcessGraph(pg.second.get(), func_lib));
    }
  }

  auto func_names = func_lib->ListFunctionNames();
  for (const auto &func_name : func_names) {
    const tensorflow::FunctionDef *fdef = func_lib->Find(func_name);
    std::unique_ptr<tensorflow::FunctionBody> fbody;
    FunctionDefToBodyHelper(*fdef, tensorflow::AttrSlice{}, func_lib, &fbody);

    TF_RETURN_IF_ERROR(ProcessGraph(fbody->graph, func_lib, "[" + func_name + "]"));

    auto lookup = [&fdef](const tensorflow::Node *node) -> absl::optional<std::string> {
      for (const auto &control_ret : fdef->control_ret()) {
        if (control_ret.second == node->name()) {
          return absl::make_optional(node->name());
        }
      }
      return absl::nullopt;
    };
    tensorflow::FunctionDef optimized_fdef;
    TF_RETURN_IF_ERROR(tensorflow::GraphToFunctionDef(*fbody->graph, func_name, lookup, &optimized_fdef));
    TF_RETURN_IF_ERROR(func_lib->RemoveFunction(func_name));
    TF_RETURN_IF_ERROR(func_lib->AddFunctionDef(optimized_fdef));
  }

  return Status::OK();
}

Status DumpOutputs(Graph *graph, Node *node, std::string prefix = "") {
  if (node->num_outputs() == 0) {
    return Status::OK();
  }

  std::vector<std::string> tensor_names;
  std::vector<NodeBuilder::NodeOut> copyable_outputs;
  std::unordered_set<int> output_idxes;
  std::unordered_set<Node *> output_nodes;
  for (int i = 0; i < node->num_outputs(); i++) {
    if (DataTypeCanUseMemcpy(node->output_type(i))) {
      tensor_names.emplace_back(prefix + "(" + node->name() + "):" + std::to_string(i));
      copyable_outputs.emplace_back(NodeBuilder::NodeOut(node, i));
      output_idxes.insert(i);
    }
  }

  if (copyable_outputs.empty()) {
    return Status::OK();
  }

  for (auto edge : node->out_edges()) {
    if (output_idxes.count(edge->src_output())) {
      output_nodes.insert(edge->dst());
    }
  }

  Node *dump_node = nullptr;
  TF_RETURN_IF_ERROR(NodeBuilder(node->name() + "_dump_outputs", "AscendDump")
                       .Input(copyable_outputs)
                       .Attr("tensor_names", tensor_names)
                       .Attr("op_type", node->type_string())
                       .Finalize(graph, &dump_node));

  for (auto n : output_nodes) {
    graph->AddControlEdge(dump_node, n);
  }
  return Status::OK();
}

Status DbgDumpPass::ProcessGraph(Graph *graph, FunctionLibraryDefinition *func_lib, std::string prefix) {
  static std::atomic<int64_t> uuid{0};

  if (graph == nullptr) {
    return Status::OK();
  }

  for (auto node : graph->op_nodes()) {
    if (node->type_string() == "AscendDump") {
      return Status::OK();
    }
  }

  std::string graph_key = std::to_string(uuid.fetch_add(1)) + "_" + std::to_string(graph->num_nodes());

  if (VLOG_IS_ON(1)) {
    WriteTextProto(Env::Default(), "Graph_" + graph_key + ".before.pbtxt", graph->ToGraphDefDebug());
  }

  int num_nodes = graph->num_node_ids();
  for (int i = 0; i < num_nodes; i++) {
    Node *node = graph->FindNodeId(i);
    if (node == nullptr || !node->IsOp()) {
      continue;
    }
    DumpOutputs(graph, node, prefix);
  }

  if (VLOG_IS_ON(1)) {
    WriteTextProto(Env::Default(), "Graph_" + graph_key + ".after.pbtxt", graph->ToGraphDefDebug());
  }

  return Status::OK();
}
// REGISTER_OPTIMIZATION(OptimizationPassRegistry::POST_REWRITE_FOR_EXEC, 0, DbgDumpPass);
REGISTER_OPTIMIZATION(OptimizationPassRegistry::PRE_PLACEMENT, 0, DbgDumpPass);
}  // namespace tensorflow
