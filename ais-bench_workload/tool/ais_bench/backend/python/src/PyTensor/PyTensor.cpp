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
#include "PyTensor/PyTensor.h"
#include "Base/Tensor/TensorBuffer/TensorBuffer.h"
#include "Base/Tensor/TensorShape/TensorShape.h"

#include <map>
#include <exception>
#include <pybind11/stl.h>

#include "Base/Log/Log.h"

namespace {
const uint32_t ZERO_BYTE = 0;
const uint32_t ONE_BYTE = 1;
const uint32_t TWO_BYTE = 2;
const uint32_t FOUR_BYTE = 4;
const uint32_t EIGHT_BYTE = 8;

const std::map<Base::TensorDataType, uint32_t> DATA_TYPE_TO_BYTE_SIZE_MAP = {
    {Base::TENSOR_DTYPE_UNDEFINED, ZERO_BYTE},
    {Base::TENSOR_DTYPE_UINT8, ONE_BYTE},
    {Base::TENSOR_DTYPE_INT8, ONE_BYTE},
    {Base::TENSOR_DTYPE_UINT16, TWO_BYTE},
    {Base::TENSOR_DTYPE_INT16, TWO_BYTE},
    {Base::TENSOR_DTYPE_UINT32, FOUR_BYTE},
    {Base::TENSOR_DTYPE_INT32, FOUR_BYTE},
    {Base::TENSOR_DTYPE_UINT64, EIGHT_BYTE},
    {Base::TENSOR_DTYPE_INT64, EIGHT_BYTE},
    {Base::TENSOR_DTYPE_FLOAT16, TWO_BYTE},
    {Base::TENSOR_DTYPE_FLOAT32, FOUR_BYTE},
    {Base::TENSOR_DTYPE_DOUBLE64, EIGHT_BYTE},
    {Base::TENSOR_DTYPE_BOOL, ONE_BYTE}
};

const std::map<Base::TensorDataType, std::string> DATA_TYPE_TO_FORMAT_MAP = {
    {Base::TENSOR_DTYPE_UINT8, py::format_descriptor<uint8_t>::format()},
    {Base::TENSOR_DTYPE_INT8, py::format_descriptor<int8_t>::format()},
    {Base::TENSOR_DTYPE_UINT16, py::format_descriptor<uint16_t>::format()},
    {Base::TENSOR_DTYPE_INT16, py::format_descriptor<int16_t>::format()},
    {Base::TENSOR_DTYPE_UINT32, py::format_descriptor<uint32_t>::format()},
    {Base::TENSOR_DTYPE_INT32, py::format_descriptor<int32_t>::format()},
    {Base::TENSOR_DTYPE_UINT64, "L"},
    {Base::TENSOR_DTYPE_INT64, "l"},
    {Base::TENSOR_DTYPE_FLOAT16, "e"},
    {Base::TENSOR_DTYPE_FLOAT32, py::format_descriptor<float>::format()},
    {Base::TENSOR_DTYPE_DOUBLE64, py::format_descriptor<double>::format()},
    {Base::TENSOR_DTYPE_BOOL, py::format_descriptor<bool>::format()}
};

const std::map<std::string, Base::TensorDataType> FORMAT_TO_DATA_TYPE_MAP = {
    {py::format_descriptor<uint8_t>::format(), Base::TENSOR_DTYPE_UINT8},
    {py::format_descriptor<int8_t>::format(), Base::TENSOR_DTYPE_INT8},
    {py::format_descriptor<uint16_t>::format(), Base::TENSOR_DTYPE_UINT16},
    {py::format_descriptor<int16_t>::format(), Base::TENSOR_DTYPE_INT16},
    {py::format_descriptor<uint32_t>::format(), Base::TENSOR_DTYPE_UINT32},
    {py::format_descriptor<int32_t>::format(), Base::TENSOR_DTYPE_INT32},
    {"L", Base::TENSOR_DTYPE_UINT64},
    {"l", Base::TENSOR_DTYPE_INT64},
    {"e", Base::TENSOR_DTYPE_FLOAT16},
    {py::format_descriptor<float>::format(), Base::TENSOR_DTYPE_FLOAT32},
    {py::format_descriptor<double>::format(), Base::TENSOR_DTYPE_DOUBLE64},
    {py::format_descriptor<bool>::format(), Base::TENSOR_DTYPE_BOOL}
};
}
namespace Base {
void TensorToHost(TensorBase &tensor)
{
    APP_ERROR ret = tensor.ToHost();
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
}

void TensorToDevice(TensorBase &tensor, const int32_t deviceId)
{
    APP_ERROR ret = tensor.ToDevice(deviceId);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
}

void TensorToDvpp(TensorBase &tensor, const int32_t deviceId)
{
    APP_ERROR ret = tensor.ToDvpp(deviceId);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
}

TensorBase FromNumpy(py::buffer b)
{
    py::buffer_info info = b.request();
    auto dataType = Base::TENSOR_DTYPE_UINT8;
    if (FORMAT_TO_DATA_TYPE_MAP.find(info.format) != FORMAT_TO_DATA_TYPE_MAP.end()) {
        dataType = FORMAT_TO_DATA_TYPE_MAP.find(info.format)->second;
    }
    std::vector<uint32_t> shape = {};
    for (auto s : info.shape) {
        shape.push_back((uint32_t)s);
    }
    uint32_t bytes = 0;
    if (DATA_TYPE_TO_BYTE_SIZE_MAP.find(dataType) != DATA_TYPE_TO_BYTE_SIZE_MAP.end()) {
        bytes = DATA_TYPE_TO_BYTE_SIZE_MAP.find(dataType)->second;
    }
    MemoryData memoryData(info.ptr, info.size * bytes, MemoryData::MemoryType::MEMORY_HOST, -1);
    TensorBase src(memoryData, true, shape, dataType);
    TensorBase dst(shape, dataType);
    APP_ERROR ret = Base::TensorBase::TensorBaseMalloc(dst);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBaseMalloc failed. ret=" << ret << std::endl;
        throw std::runtime_error(GetError(ret));
    }
    ret = Base::TensorBase::TensorBaseCopy(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBaseCopy failed. ret=" << ret << std::endl;
        throw std::runtime_error(GetError(ret));
    }
    return dst;
}

py::buffer_info ToNumpy(const TensorBase &tensor)
{
    int32_t dims = tensor.GetShape().size();
    auto shape = tensor.GetShape();
    auto dtype = tensor.GetDataType();
    uint32_t bytes = 0;
    if (DATA_TYPE_TO_BYTE_SIZE_MAP.find(dtype) != DATA_TYPE_TO_BYTE_SIZE_MAP.end()) {
        bytes = DATA_TYPE_TO_BYTE_SIZE_MAP.find(dtype)->second;
    }

    std::vector<uint32_t> strides(dims);
    uint32_t size = 1;
    for (int32_t i = dims - 1; i >= 0; i--) {
        strides[i] = bytes * size;
        size *= shape[i];
    }
    // cpu tensor
    if (tensor.IsDevice()) {
        throw std::runtime_error("tensor is in npu. can't convert to numpy array");
    }

    std::string format = py::format_descriptor<uint8_t>::format();
    if (DATA_TYPE_TO_FORMAT_MAP.find(dtype) != DATA_TYPE_TO_FORMAT_MAP.end()) {
        format = DATA_TYPE_TO_FORMAT_MAP.find(dtype)->second;
    }
    py::buffer_info buf = {tensor.GetBuffer(), bytes, format, (int64_t)shape.size(), shape, strides};
    return buf;
}

TensorBase BatchVector(const std::vector<TensorBase> &tensors, const bool &keepDims)
{
    TensorBase output = {};
    APP_ERROR ret = TensorBase::BatchVector(tensors, output, keepDims);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBase::BatchVector failed. ret=" << ret << std::endl;
        throw std::runtime_error(GetError(ret));
    }
    return output;
}
}

void RegistPyTensorEnumType(py::module &m)
{
    auto dtype = py::enum_<Base::TensorDataType>(m, "dtype");
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "int8", Base::TensorDataType::TENSOR_DTYPE_INT8);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "uint8", Base::TensorDataType::TENSOR_DTYPE_UINT8);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "int16", Base::TensorDataType::TENSOR_DTYPE_INT16);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "uint16", Base::TensorDataType::TENSOR_DTYPE_UINT16);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "int32", Base::TensorDataType::TENSOR_DTYPE_INT32);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "uint32", Base::TensorDataType::TENSOR_DTYPE_UINT32);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "int64", Base::TensorDataType::TENSOR_DTYPE_INT64);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "uint64", Base::TensorDataType::TENSOR_DTYPE_UINT64);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "float16", Base::TensorDataType::TENSOR_DTYPE_FLOAT16);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "float32", Base::TensorDataType::TENSOR_DTYPE_FLOAT32);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "double", Base::TensorDataType::TENSOR_DTYPE_DOUBLE64);
    REGIST_ENUM_TYPE_TO_MODULE(m, dtype, "bool", Base::TensorDataType::TENSOR_DTYPE_BOOL);

    auto memoryType = py::enum_<Base::MemoryData::MemoryType>(m, "type");
    REGIST_ENUM_TYPE_TO_MODULE(m, memoryType, "memory_host", Base::MemoryData::MemoryType::MEMORY_HOST);
    REGIST_ENUM_TYPE_TO_MODULE(m, memoryType, "memory_device", Base::MemoryData::MemoryType::MEMORY_DEVICE);
    REGIST_ENUM_TYPE_TO_MODULE(m, memoryType, "memory_dvpp", Base::MemoryData::MemoryType::MEMORY_DVPP);
}

void RegistPyTensorModule(py::module &m)
{
    py::class_<Base::MemorySummary, std::unique_ptr<Base::MemorySummary, py::nodelete>>(m, "MemorySummary")
        .def(py::init([]() { return Base::GetMemorySummaryPtr(); }))
        .def_readwrite("H2D_time_list", &Base::MemorySummary::H2DTimeList)
        .def_readwrite("D2H_time_list", &Base::MemorySummary::D2HTimeList)
        .def("reset", &Base::MemorySummary::Reset);

    auto tensor = py::class_<Base::TensorBase>(m, "Tensor", py::buffer_protocol());
    tensor.def(py::init(&Base::FromNumpy));
    tensor.def_buffer(&Base::ToNumpy);
    tensor.def("to_device", &Base::TensorToDevice);
    tensor.def("to_host", &Base::TensorToHost);
    tensor.def("to_dvpp", &Base::TensorToDvpp);
    tensor.def("__str__", &Base::TensorBase::GetDesc);
    tensor.def("__repr__", &Base::TensorBase::GetDesc);

    m.def("batch", &Base::BatchVector, py::arg("inputs"), py::arg("keep_dims") = false);

    auto pyGetType = [] (const Base::TensorBase &tensor) {
            auto type = tensor.GetTensorType();
            if (type == Base::MemoryData::MEMORY_HOST_MALLOC || type == Base::MemoryData::MEMORY_HOST_NEW) {
                return Base::MemoryData::MEMORY_HOST;
            }
            return type;
    };
    tensor.def_property_readonly("type", pyGetType);
    tensor.def_property_readonly("device", &Base::TensorBase::GetDeviceId);
    tensor.def_property_readonly("dtype", &Base::TensorBase::GetDataType);
    tensor.def_property_readonly("shape", &Base::TensorBase::GetShape);
    RegistPyTensorEnumType(m);
}
