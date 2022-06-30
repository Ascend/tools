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

#ifndef TENSOR_CORE_H
#define TENSOR_CORE_H

#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <map>

#include "Base/MemoryHelper/MemoryHelper.h"
#include "Base/ErrorCode/ErrorCode.h"
namespace Base {
enum TensorDataType {
    TENSOR_DTYPE_UNDEFINED = -1,
    TENSOR_DTYPE_FLOAT32 = 0,
    TENSOR_DTYPE_FLOAT16 = 1,
    TENSOR_DTYPE_INT8 = 2,
    TENSOR_DTYPE_INT32 = 3,
    TENSOR_DTYPE_UINT8 = 4,
    TENSOR_DTYPE_INT16 = 6,
    TENSOR_DTYPE_UINT16 = 7,
    TENSOR_DTYPE_UINT32 = 8,
    TENSOR_DTYPE_INT64 = 9,
    TENSOR_DTYPE_UINT64 = 10,
    TENSOR_DTYPE_DOUBLE64 = 11,
    TENSOR_DTYPE_BOOL = 12
};

static std::map<int, std::string> TensorDataTypeStr = {
    {-1, "TENSOR_DTYPE_UNDEFINED"},
    {0, "TENSOR_DTYPE_FLOAT32"},
    {1, "TENSOR_DTYPE_FLOAT16"},
    {2, "TENSOR_DTYPE_INT8"},
    {3, "TENSOR_DTYPE_INT32"},
    {4, "TENSOR_DTYPE_UINT8"},
    {6, "TENSOR_DTYPE_INT16"},
    {7, "TENSOR_DTYPE_UINT16"},
    {8, "TENSOR_DTYPE_UINT32"},
    {9, "TENSOR_DTYPE_INT64"},
    {10, "TENSOR_DTYPE_UINT64"},
    {11, "TENSOR_DTYPE_DOUBLE64"},
    {12, "TENSOR_DTYPE_BOOL"},
};

std::string GetTensorDataTypeDesc(TensorDataType type);

class TensorBuffer;
class TensorShape;
class TensorBase {
public:
    TensorBase();
    virtual ~TensorBase() = default;
    TensorBase(const TensorBase &tensor) = default;
    // tensor构造函数
    TensorBase(const MemoryData &memoryData, const bool &isBorrowed,
        const std::vector<uint32_t> &shape, const TensorDataType &type);
    TensorBase(const std::vector<uint32_t> &shape, const TensorDataType &type,
        const MemoryData::MemoryType &bufferType, const int32_t &deviceId);
    TensorBase(const std::vector<uint32_t> &shape, const TensorDataType &type, const int32_t &deviceId);
    TensorBase(const std::vector<uint32_t> &shape, const TensorDataType &type);
    TensorBase(const std::vector<uint32_t> &shape);
    TensorBase& operator=(const TensorBase &other);
    static APP_ERROR TensorBaseMalloc(TensorBase &tensor);
    static APP_ERROR TensorBaseCopy(TensorBase &dst, const TensorBase &src);
    // 获取tensor部署的设备类型
    MemoryData::MemoryType GetTensorType() const;
    // buffer记录的数据量
    size_t GetSize() const;
    // buffer 字节数据量
    size_t GetByteSize() const;
    // tensor 的shape
    std::vector<uint32_t> GetShape() const;
    // tensor 的 device
    int32_t GetDeviceId() const;
    // tensor 数据类型
    TensorDataType GetDataType() const;
    // 判断是否在Host
    bool IsHost() const;
    // 判断是否在Device
    bool IsDevice() const;
    // 获取tensor指针
    void* GetBuffer() const;
    // host to device
    APP_ERROR ToDevice(int32_t deviceId);
    // host to dvpp
    APP_ERROR ToDvpp(int32_t deviceId);
    // device to host
    APP_ERROR ToHost();
    static APP_ERROR BatchConcat(const std::vector<TensorBase> &inputs, TensorBase &output);
    static APP_ERROR BatchStack(const std::vector<TensorBase> &inputs, TensorBase &output);

    // 组batch
    static APP_ERROR BatchVector(const std::vector<TensorBase> &inputs, TensorBase &output,
        const bool &keepDims = false);
    // 详细信息
    std::string GetDesc();
private:
    static APP_ERROR CheckBatchTensors(const std::vector<TensorBase> &inputs, const bool &checkFirstDim);
private:
    std::shared_ptr<TensorBuffer> buffer_;
    std::shared_ptr<TensorShape> shape_;
    bool isInitFlag_ = false;
    TensorDataType dataType_ = TENSOR_DTYPE_UINT8;
};
}
#endif

