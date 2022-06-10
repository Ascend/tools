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

#include <limits>

#include "absl/algorithm/container.h"
#include "absl/memory/memory.h"
#include "absl/strings/str_replace.h"
#include "tensorflow/c/c_api.h"
#include "tensorflow/c/c_api_internal.h"
#include "tensorflow/c/eager/c_api_experimental.h"
#include "tensorflow/c/eager/c_api_internal.h"
#include "tensorflow/core/framework/common_shape_fns.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/op_kernel.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/util/env_var.h"
#include "./dump_config.h"

namespace {
const static char kSysEndian = []() {
  int x = 1;
  return (((char *)&x)[0]) ? '<' : '>';
}();

char TensorDtype2Np(tensorflow::DataType dtype) {
  if (tensorflow::DataTypeIsFloating(dtype)) {
    return 'f';
  } else if (tensorflow::DataTypeIsSigned(dtype)) {
    return 'i';
  } else if (tensorflow::DataTypeIsUnsigned(dtype)) {
    return 'u';
  } else if (tensorflow::DataTypeIsComplex(dtype)) {
    return 'c';
  } else {
    return 'b';
  }
}

std::string TensorShape2Npy(tensorflow::TensorShape shape) {
  auto num_dims = shape.dims();
  if (num_dims == 0) {
    return "()";
  } else if (num_dims == 1) {
    return "(" + std::to_string(shape.dim_size(0)) + ",)";
  }
  std::string shape_string = "(";
  for (int i = 0; i < num_dims - 1; i++) {
    shape_string += std::to_string(shape.dim_size(i));
    shape_string += ", ";
  }
  return shape_string + std::to_string(shape.dim_size(num_dims - 1)) + ")";
}

std::string AssembleNpyHeader(tensorflow::Tensor tensor) {
  std::string dict;
  dict += "{'descr': '";
  dict += kSysEndian;
  dict += TensorDtype2Np(tensor.dtype());
  dict += std::to_string(tensorflow::DataTypeSize(tensor.dtype()));
  dict += "', 'fortran_order': False, 'shape': ";
  dict += TensorShape2Npy(tensor.shape());
  dict += ", }";
  int remainder = 16 - (10 + dict.size()) % 16;
  dict.insert(dict.end(), remainder, ' ');
  dict.back() = '\n';

  std::string header;
  header += (char)0x93;
  header += "NUMPY";
  header += (char)0x01;  // Numpy major
  header += (char)0x00;  // Numpy minor
  auto size = (uint16_t)dict.size();
  char *size_bits = (char *)(&size);
  header += *size_bits;
  header += *(size_bits + 1);
  header.insert(header.end(), dict.begin(), dict.end());

  return header;
}

void WriteTensor2Npy(tensorflow::Tensor tensor, std::string fname) {
  FILE *fp = NULL;
  auto shape = tensor.shape().dim_sizes();
  int64_t num_elements = tensor.NumElements();

  fp = fopen(fname.c_str(), "wb");

  std::string header = AssembleNpyHeader(tensor);

  fseek(fp, 0, SEEK_SET);
  fwrite(&header[0], sizeof(char), header.size(), fp);
  fseek(fp, 0, SEEK_END);
  fwrite(tensor.tensor_data().data(), tensorflow::DataTypeSize(tensor.dtype()), num_elements, fp);
  fclose(fp);
}
}  // namespace

namespace tensorflow {

REGISTER_OP("AscendDump")
  .Input("inputs: Tin")
  .Attr("tensor_names: list(string)")
  .Attr("op_type: string")
  .Attr("Tin: list(type)")
  .SetIsStateful();

class AscendDump : public OpKernel {
 public:
  explicit AscendDump(OpKernelConstruction *ctx) : OpKernel(ctx) {
    OP_REQUIRES_OK(ctx, ctx->GetAttr("tensor_names", &tensor_names_));
    OP_REQUIRES_OK(ctx, ctx->GetAttr("op_type", &op_type_));
  }

  void Compute(OpKernelContext *ctx) override {
    OpInputList inputs;
    OP_REQUIRES_OK(ctx, ctx->input_list("inputs", &inputs));
    std::string nanos_uuid = std::to_string(Env::Default()->NowMicros());
    for (int64 i = 0; i < inputs.size(); i++) {
      std::string tensor_name = absl::StrReplaceAll(tensor_names_[i], {{"/", "_"}, {":", "."}});
      std::string file_name = absl::StrCat(tensor_name, ".", nanos_uuid, ".npy");
      VLOG(1) << "Dump " << tensor_names_[i] << " to " << file_name;
      if (g_dumpConfig.dumpSwitch != 0) {
        std::string real_file_name = absl::StrCat(g_dumpConfig.dumpPath, file_name);
        WriteTensor2Npy(inputs[i], real_file_name);
      }
      VLOG(1) << tensor_names_[i] << " " << inputs[i].DebugString() << std::endl;
    }
  }

 private:
  std::vector<std::string> tensor_names_;
  std::string op_type_;
};

REGISTER_KERNEL_BUILDER(Name("AscendDump").Device(DEVICE_CPU).Priority(999), AscendDump);

}  // namespace tensorflow