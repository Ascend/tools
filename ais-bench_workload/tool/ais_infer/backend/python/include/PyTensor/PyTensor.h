/*
 * Copyright(C) 2021. Huawei Technologies Co.,Ltd. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef PY_TENSOR_BASE
#define PY_TENSOR_BASE

#include <vector>
#include <string>
#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "Base/Tensor/TensorBase/TensorBase.h"

namespace py = pybind11;
#define REGIST_ENUM_TYPE_TO_MODULE(Module, EnumClass, EnumValueName, EnumValue) \
    (EnumClass).value((EnumValueName), (EnumValue)); \
    (Module).attr((EnumValueName)) = (EnumValue)

namespace Base {

void TensorToHost(TensorBase &tensor);
void TensorToDevice(TensorBase &tensor, const int32_t deviceId);
void TensorToDvpp(TensorBase &tensor, const int32_t deviceId);

TensorBase FromNumpy(py::buffer b);
py::buffer_info ToNumpy(const TensorBase &tensor);
TensorBase BatchVector(const std::vector<TensorBase> &tensors, const bool &keepDims = false);
}
void RegistPyTensorModule(py::module &m);
#endif

