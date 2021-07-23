#include <fstream>
#include <dlfcn.h>

// tensorflow2.x
#ifdef TF_VERSION2
#include "tensorflow/core/common_runtime/graph_constructor.h"
#else
// tensorflow1.15
#include "tensorflow/core/graph/graph_constructor.h"
#endif

#include "tensorflow/core/common_runtime/shape_refiner.h"
#include "tensorflow/core/platform/env.h"
#include "tensorflow/core/graph/graph.h"
#include "tensorflow/core/graph/algorithm.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/common_shape_fns.h"

using namespace tensorflow;
using namespace std;
using namespace shape_inference;

using TensorShapes = tensorflow::gtl::InlinedVector<tensorflow::TensorShape, 4>;

REGISTER_OP("DropOutDoMask")
    .Input("x: T")
    .Input("mask: uint8")
    .Input("keep_prob: T")
    .Output("y: T")
    .Attr("T: {float16, float32}")
    .SetIsStateful()
    .SetShapeFn([](shape_inference::InferenceContext *c) {
      c->set_output(0, c->input(0));
      return Status::OK();
    });

REGISTER_OP("DropOutGenMask")
    .Input("shape: T")
    .Attr("T: {int64, int32}")
    .Input("prob: S")
    .Attr("S: {float, half}")
    .Output("output: uint8")
    .Attr("seed: int = 0")
    .Attr("seed2: int = 0")
    .SetIsStateful()
    .SetShapeFn([](shape_inference::InferenceContext *c) {
      ShapeHandle unused;
      TF_RETURN_IF_ERROR(c->WithRankAtMost(c->input(1), 0, &unused));  // prob must be 0-d

      ShapeHandle inputShapeHandle;
      TF_RETURN_IF_ERROR(c->MakeShapeFromShapeTensor(0, &inputShapeHandle));

      int32 rank = c->Rank(inputShapeHandle);
      if (InferenceContext::kUnknownRank == rank) {
        ShapeHandle out = c->UnknownShapeOfRank(1);
        c->set_output(0, out);
        return Status::OK();
      }

      bool unknownDimExist = false;
      for (int32 i = 0; i < rank; ++i) {
        DimensionHandle dimHandle = c->Dim(inputShapeHandle, i);
        int64 value = c->Value(dimHandle);
        if (InferenceContext::kUnknownDim == value) {
          unknownDimExist = true;
          break;
        }
      }

      if (unknownDimExist) {
        ShapeHandle out = c->UnknownShapeOfRank(1);
        c->set_output(0, out);
        return Status::OK();
      }

      int64 bitCount = 0;
      if (rank != 0) {
        DimensionHandle inputDimHandle = c->NumElements(inputShapeHandle);
        bitCount = c->Value(inputDimHandle);
      }

      // align to 128 and around up
      int64 n128Bits = bitCount / 128;
      if ((bitCount % 128) != 0) { n128Bits++; }

      // transfer 128 bit count to byte count if shape is full know
      int64 nBytes = n128Bits * 16;

      ShapeHandle out = c->Vector(nBytes);
      c->set_output(0, out);
      return Status::OK();
      return Status::OK();
    });

class StringUtils {
 public:
  static std::string &Ltrim(std::string &s) {
    (void)s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](int c) {
      return !std::isspace(c);
    }));
    return s;
  }

  static std::string &Rtrim(std::string &s) {
    (void)s.erase(std::find_if(s.rbegin(), s.rend(), [](int c) {
      return !std::isspace(c);
    }).base(), s.end());
    return s;
  }

  /// @ingroup domi_common
  /// @brief trim space
  static std::string &Trim(std::string &s) { return Ltrim(Rtrim(s)); }

  // split string
  static std::vector<std::string> Split(const std::string &str, char delim) {
    std::vector<std::string> elems;

    if (str.empty()) {
      elems.emplace_back("");
      return elems;
    }

    std::stringstream ss(str);
    std::string item;

    while (getline(ss, item, delim)) {
      elems.push_back(item);
    }
    auto str_size = str.size();
    if (str_size > 0 && str[str_size - 1] == delim) {
      elems.emplace_back("");
    }

    return elems;
  }
};

int loadPbToGraph(const std::string &pb_file, Graph *graph) {
  GraphDef graph_def;
  Status status = ReadBinaryProto(Env::Default(), pb_file, &graph_def);
  if (!status.ok()) {
    string file_data;
    status = ReadFileToString(Env::Default(), pb_file, &file_data);
    if (!status.ok()) {
      std::cout << "[ERROR] read file to string failed. pb file:" <<
        pb_file << " reason:" << status.error_message() << std::endl;
      return -1;
    }
    if (!protobuf::TextFormat::ParseFromString(file_data, &graph_def)) {
      std::cout << "[ERROR] load pb file to graph_def failed. pb file:" <<
        pb_file << " reason:" << status.error_message() << std::endl;
      return -1;
    }
  }

  GraphConstructorOptions opts;
  status = ConvertGraphDefToGraph(opts, graph_def, graph);
  if (!status.ok()) {
    std::cout << "[ERROR] convert graph_def to graph failed. pb file:" <<
      pb_file << " reason:" << status.error_message() << std::endl;
    return -1;
  }
  return 0;
}

int saveGraphToPbtxt(Graph *graph) {
  std::string dst_pbtxt = "target.pbtxt";
  GraphDef graph_def;
  graph->ToGraphDef(&graph_def);
  Status status = WriteTextProto(Env::Default(), dst_pbtxt, graph_def);

  if (!status.ok()) {
    std::cout << "[ERROR] save graph to pbtxt failed. pbtxt file:" << dst_pbtxt << std::endl;
    return -1;
  }
  return 0;
}

vector<string> SplitInputShape(const std::string &input_shape) {
  vector<string> shape_pair_vec;
  size_t pos = input_shape.rfind(":");
  if (pos != std::string::npos) {
    shape_pair_vec.emplace_back(input_shape.substr(0, pos));
    shape_pair_vec.emplace_back(input_shape.substr(pos + 1, input_shape.size() - pos));
  }
  return shape_pair_vec;
}

int parseInputShape(const std::string &input_shape, std::map<std::string, TensorShape> &input_shape_map) {
  try {
    vector<string> shape_vec = StringUtils::Split(input_shape, ';');
    if (shape_vec.empty()) {
      std::cout << "[ERROR] parse input_shape failed, size zero after split by ; input_shape:" <<
        input_shape << std::endl;
      return -1;
    }
    const int DEFAULT_SHAPE_PAIR_SIZE = 2;
    for (const auto &shape : shape_vec) {
      vector<string> shape_pair_vec = SplitInputShape(shape);
      if (shape_pair_vec.size() != DEFAULT_SHAPE_PAIR_SIZE || shape_pair_vec[1].empty()) {
        std::cout << "[ERROR] parse input_shape failed, problom on : input_shape:" <<
          input_shape << std::endl;
        return -1;
      }

      vector<string> shape_value_strs = StringUtils::Split(shape_pair_vec[1], ',');
      TensorShape tensor_shape;
      for (auto &shape_value_str : shape_value_strs) {
        int64 left_result = stol(StringUtils::Trim(shape_value_str));
        tensor_shape.AddDim(left_result);
      }
      input_shape_map[shape_pair_vec[0]] = tensor_shape;
    }
  } catch (...) {
    std::cout << "[ERROR] parse input_shape failed cause exception. input_shape:" <<
      input_shape << std::endl;
    return -1;
  }

  return 0;
}

void graphInferShapeFromInput(Graph *graph, const std::map<std::string, TensorShape> &input_shape_map,
                              const std::string &result_file) {
  ShapeRefiner shape_refiner(graph->versions(), OpRegistry::Global());
  ofstream fs(result_file, ios::out);

  auto node_shape_inference_lambda = [&shape_refiner, &input_shape_map, &fs](tensorflow::Node *node) {
    auto iter = input_shape_map.find(node->name());
    if (iter != input_shape_map.end()) {
      node->AddAttr("shape", iter->second);
    }

    if (node->IsArg()) {
      auto func = node->attrs().Find("output_tensor_desc")->list().func()[0];
      std::map<string, AttrValue> attr_map(func.attr().begin(), func.attr().end());
      TensorShape tensor_shape;
      for (auto dim : attr_map["serialize_shape"].list().i()) {
        tensor_shape.AddDim(dim);
      }
      node->AddAttr("_output_shapes", TensorShapes({tensor_shape}));
    }

    auto status = shape_refiner.AddNode(node);
    if (!status.ok()) {
      std::cout << "[ERROR] infer shape failed. node:" << node->name() << "[" << node->type_string() << "] errmsg:" <<
        status.error_message() << std::endl;
      return;
    }

    auto node_ctx = shape_refiner.GetContext(node);

    for (int i = 0; i < node_ctx->num_outputs(); ++i) {
      fs << "node:" << node->name() << " index:" << i <<
        " shape:" << node_ctx->DebugString(node_ctx->output(i)) << std::endl;
    }

  };
  ReverseDFS(*graph, {}, node_shape_inference_lambda);
}

int extractShapeFromGraph(Graph *graph, const std::string &result_file) {
  ofstream fs(result_file, ios::out);

  auto node_shape_inference_lambda = [&fs](tensorflow::Node *node) {

  if (node->attrs().Find("output_tensor_desc") == nullptr) {
      std::cout << "[INFO] node:" << node->name() << " type:" << node->type_string() <<
        " has no output_tensor_desc" << std::endl;
    return;
  }

  int i = 0;
  for (auto func : node->attrs().Find("output_tensor_desc")->list().func()) {
    std::map<string, AttrValue> attr_map(func.attr().begin(), func.attr().end());

    std::string shape = "[";
    bool is_first = true;
    for (auto dim : attr_map["serialize_shape"].list().i()) {
      if (!is_first) {
        shape += ",";
      }
      shape += std::to_string(dim);
      is_first = false;
    }
    shape += "]";

    fs << "node:" << node->name() << " index:" << i << " shape:" << shape << std::endl;
    ++i;
  }

  };
  ReverseDFS(*graph, {}, node_shape_inference_lambda);
}

std::string getSoPath(const std::string &so_name) {
  std::string cmd = "find / -name \"" + so_name + "\" 2>/dev/null";
  char buf_ps[1024] = {'\0'};
  FILE *ptr = nullptr;
  if ((ptr = popen(cmd.c_str(), "r")) != nullptr) {
    fgets(buf_ps, 1024, ptr);
    pclose(ptr);
    ptr = nullptr;
  } else {
    std::cout << "[ERROR] find so file failed, so_name:" << so_name << std::endl;
  }
  std::string s(buf_ps);
  return StringUtils::Trim(s);
}

int init() {
  std::string py_so_name = "libpython3.7m.so";
  std::string py_so_path = getSoPath(py_so_name);
  if (py_so_path.empty()) {
    std::cout << "[ERROR] get path for so:" << py_so_name << " failed" << std::endl;
    return -1;
  }

  void *handle = dlopen(py_so_path.c_str(), RTLD_NOW | RTLD_GLOBAL);
  if (!handle) {
    std::cout << "[ERROR] dlopen python failed, error:" << std::string(dlerror()) << std::endl;
    return -1;
  }

  std::string pywrap_so_name = "_pywrap_tensorflow_internal.so";
  std::string pywrap_so_path = getSoPath(pywrap_so_name);
  if (pywrap_so_path.empty()) {
    std::cout << "[ERROR] get path for so:" << pywrap_so_name << " failed" << std::endl;
    return -1;
  }
  handle = dlopen(pywrap_so_path.c_str(), RTLD_NOW | RTLD_GLOBAL);
  if (!handle) {
    std::cout << "[ERROR] dlopen pywrap failed, error:" << std::string(dlerror()) << std::endl;
    return -1;
  }
  return 0;
}

int main(int argc, char *argv[]) {
  if (init() == -1) {
    std::cout << "[ERROR] Init failed" << std::endl;
    return -1;
  }

  if (argc < 2) {
    std::cout << "[ERROR] invalid argument. argument1 : pb/pbtxt file name, argument2 : input shape, \
      format like atc, must pass when infer pb" << std::endl;
    return -1;
  }

  std::cout << "CPU infershape start working now, please wait for a moment." << std::endl;

  std::string pb_file = std::string(argv[1]);
  std::string input_shape;
  if (argc == 3) {
    input_shape = std::string(argv[2]);
  }

  bool is_pb = false;
  if (StringUtils::Split(pb_file, '.')[1] == "pb") {
    is_pb = true;
  }

  if (is_pb && argc == 2) {
    std::cout << "[ERROR] invalid argument. argument1 : pb/pbtxt file name, argument2 : input shape, \
      format like atc, must pass when infer pb" << std::endl;
    return -1;
  }

  Graph graph(OpRegistry::Global());

  if (loadPbToGraph(pb_file, &graph) == -1) {
    std::cout << "[ERROR] load pb failed. pb file" << pb_file << std::endl;
    return -1;
  }

  std::string result_file = "cpu_infershape_result";
  std::map<std::string, TensorShape> input_shape_map;
  if (is_pb) {
    if (parseInputShape(input_shape, input_shape_map) == -1) {
      std::cout << "[ERROR] parse input shape failed. input_shape:" << input_shape << std::endl;
      return -1;
    }
  }
  graphInferShapeFromInput(&graph, input_shape_map, result_file);

  std::cout << "CPU infershape done, please check result in file " << result_file << std::endl;
  return 0;
}



