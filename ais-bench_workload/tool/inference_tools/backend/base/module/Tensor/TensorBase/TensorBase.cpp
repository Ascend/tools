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

#include "Base/Tensor/TensorBase/TensorBase.h"

#include <map>
#include <algorithm>

#include "Base/Tensor/TensorBuffer/TensorBuffer.h"
#include "Base/Tensor/TensorShape/TensorShape.h"
#include "Base/Log/Log.h"
#include "Base/DeviceManager/DeviceManager.h"

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

const std::map<Base::TensorDataType, std::string> DATA_TYPE_TO_STRING_MAP = {
    {Base::TENSOR_DTYPE_UNDEFINED, "undefined"},
    {Base::TENSOR_DTYPE_UINT8, "uint8"},
    {Base::TENSOR_DTYPE_INT8, "int8"},
    {Base::TENSOR_DTYPE_UINT16, "uint16"},
    {Base::TENSOR_DTYPE_INT16, "int16"},
    {Base::TENSOR_DTYPE_UINT32, "uint32"},
    {Base::TENSOR_DTYPE_INT32, "int32"},
    {Base::TENSOR_DTYPE_UINT64, "uint64"},
    {Base::TENSOR_DTYPE_INT64, "int64"},
    {Base::TENSOR_DTYPE_FLOAT16, "float16"},
    {Base::TENSOR_DTYPE_FLOAT32, "float32"},
    {Base::TENSOR_DTYPE_DOUBLE64, "double64"},
    {Base::TENSOR_DTYPE_BOOL, "bool"}
};
}
namespace Base {
std::string GetTensorDataTypeDesc(TensorDataType type)
{
    if (DATA_TYPE_TO_STRING_MAP.find(type) != DATA_TYPE_TO_STRING_MAP.end()) {
        return DATA_TYPE_TO_STRING_MAP.find(type)->second;
    }
    return DATA_TYPE_TO_STRING_MAP.at(TENSOR_DTYPE_UNDEFINED);
}

TensorBase& TensorBase::operator=(const TensorBase &other)
{
    if (this == &other) {
        return *this;
    }
    buffer_ = other.buffer_;
    shape_ = other.shape_;
    dataType_ = other.dataType_;
    return *this;
}

// tensor构造函数
TensorBase::TensorBase()
{
    shape_ = std::make_shared<TensorShape>();
    buffer_ = std::make_shared<TensorBuffer>();
}
TensorBase::TensorBase(const MemoryData &memoryData, const bool &isBorrowed, const std::vector<uint32_t> &shape,
    const TensorDataType &type) : dataType_(type)
{
    shape_ = std::make_shared<TensorShape>(shape);
    buffer_ = std::make_shared<TensorBuffer>();
    buffer_->type = memoryData.type;
    buffer_->size = memoryData.size;
    buffer_->deviceId = (int32_t)memoryData.deviceId;
    if (isBorrowed) {
        auto deleter = [] (void *p) {};
        buffer_->data.reset(memoryData.ptrData, deleter);
    } else {
        const TensorBuffer buffer = *buffer_;
        auto deleter = [buffer] (void *p) {
            buffer.SetContext();
            Base::MemoryData memoryData(p, buffer.size, buffer.type, buffer.deviceId);
            Base::MemoryHelper::Free(memoryData);
        };
        buffer_->data.reset(memoryData.ptrData, deleter);
    }
}

TensorBase::TensorBase(const std::vector<uint32_t> &shape, const TensorDataType &type,
        const MemoryData::MemoryType &bufferType, const int32_t &deviceId) : dataType_(type)
{
    shape_ = std::make_shared<TensorShape>(shape);
    uint32_t bytes = 0;
    if (DATA_TYPE_TO_BYTE_SIZE_MAP.find(type) != DATA_TYPE_TO_BYTE_SIZE_MAP.end()) {
        bytes = DATA_TYPE_TO_BYTE_SIZE_MAP.find(type)->second;
    }
    buffer_ = std::make_shared<TensorBuffer>(shape_->GetSize() * bytes, bufferType, deviceId);
}

TensorBase::TensorBase(const std::vector<uint32_t> &shape, const TensorDataType &type) : dataType_(type)
{
    shape_ = std::make_shared<TensorShape>(shape);
    uint32_t bytes = 0;
    if (DATA_TYPE_TO_BYTE_SIZE_MAP.find(type) != DATA_TYPE_TO_BYTE_SIZE_MAP.end()) {
        bytes = DATA_TYPE_TO_BYTE_SIZE_MAP.find(type)->second;
    }
    buffer_ = std::make_shared<TensorBuffer>(shape_->GetSize() * bytes);
}

TensorBase::TensorBase(const std::vector<uint32_t> &shape, const TensorDataType &type, const int32_t &deviceId)
{
    shape_ = std::make_shared<TensorShape>(shape);
    uint32_t bytes = 0;
    if (DATA_TYPE_TO_BYTE_SIZE_MAP.find(type) != DATA_TYPE_TO_BYTE_SIZE_MAP.end()) {
        bytes = DATA_TYPE_TO_BYTE_SIZE_MAP.find(type)->second;
    }
    buffer_ = std::make_shared<TensorBuffer>(shape_->GetSize() * bytes, deviceId);
}

TensorBase::TensorBase(const std::vector<uint32_t> &shape)
{
    shape_ = std::make_shared<TensorShape>(shape);
    buffer_ = std::make_shared<TensorBuffer>(shape_->GetSize());
}

APP_ERROR TensorBase::TensorBaseMalloc(TensorBase &tensor)
{
    APP_ERROR ret = TensorBuffer::TensorBufferMalloc(*tensor.buffer_);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBufferMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBase::TensorBaseCopy(TensorBase &dst, const TensorBase &src)
{
    APP_ERROR ret = TensorBuffer::TensorBufferCopy(*dst.buffer_, *src.buffer_);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBufferCopy failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}

// 判断是否在Host
bool TensorBase::IsHost() const
{
    if (buffer_.get() == nullptr) {
        return false;
    }
    return buffer_->IsHost();
}

// 判断是否在Device
bool TensorBase::IsDevice() const
{
    if (buffer_.get() == nullptr) {
        return false;
    }
    return buffer_->IsDevice();
}

APP_ERROR TensorBase::ToDevice(int32_t deviceId)
{
    if (buffer_.get() == nullptr) {
        return APP_ERR_COMM_INVALID_POINTER;
    }

    if (GetDeviceId() == deviceId && buffer_->type == MemoryData::MemoryType::MEMORY_DEVICE) {
        return APP_ERR_OK;
    }

    APP_ERROR ret = DeviceManager::GetInstance()->CheckDeviceId(deviceId);
    if (ret != APP_ERR_OK) {
        return ret;
    }

    // device a to device b
    TensorBuffer newBuffer(buffer_->size, MemoryData::MemoryType::MEMORY_DEVICE, deviceId);
    ret = TensorBuffer::TensorBufferMalloc(newBuffer);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    ret = TensorBuffer::TensorBufferCopy(newBuffer, *buffer_);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferCopy failed. ret=" << ret << std::endl;
        return ret;
    }
    *buffer_ = newBuffer;
    return APP_ERR_OK;
}

APP_ERROR TensorBase::ToDvpp(int32_t deviceId)
{
    if (buffer_.get() == nullptr) {
        return APP_ERR_COMM_INVALID_POINTER;
    }

    if (GetDeviceId() == deviceId && buffer_->type == MemoryData::MemoryType::MEMORY_DVPP) {
        return APP_ERR_OK;
    }

    APP_ERROR ret = DeviceManager::GetInstance()->CheckDeviceId(deviceId);
    if (ret != APP_ERR_OK) {
        return ret;
    }

    // device a to device b
    TensorBuffer newBuffer(buffer_->size, MemoryData::MemoryType::MEMORY_DVPP, deviceId);
    ret = TensorBuffer::TensorBufferMalloc(newBuffer);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    ret = TensorBuffer::TensorBufferCopy(newBuffer, *buffer_);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferCopy failed. ret=" << ret << std::endl;
        return ret;
    }
    *buffer_ = newBuffer;
    return APP_ERR_OK;
}

APP_ERROR TensorBase::ToHost()
{
    if (buffer_.get() == nullptr) {
        return APP_ERR_COMM_INVALID_POINTER;
    }

    if (IsHost()) {
        return APP_ERR_OK;
    }
    TensorBuffer host(buffer_->size);
    APP_ERROR ret = TensorBuffer::TensorBufferMalloc(host);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    ret = TensorBuffer::TensorBufferCopy(host, *buffer_);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferCopy failed. ret=" << ret << std::endl;
        return ret;
    }
    *buffer_ = host;
    return APP_ERR_OK;
}

// 获取tensor部署的设备类型
MemoryData::MemoryType TensorBase::GetTensorType() const
{
    if (buffer_.get() == nullptr) {
        return MemoryData::MemoryType::MEMORY_HOST_NEW;
    }
    return buffer_->type;
}

// buffer记录的数据量
size_t TensorBase::GetSize() const
{
    if (shape_.get() == nullptr) {
        return 0;
    }
    return shape_->GetSize();
}
// buffer 字节数据量
size_t TensorBase::GetByteSize() const
{
    if (shape_.get() == nullptr) {
        return 0;
    }
    uint32_t bytes = 0;
    if (DATA_TYPE_TO_BYTE_SIZE_MAP.find(dataType_) != DATA_TYPE_TO_BYTE_SIZE_MAP.end()) {
        bytes = DATA_TYPE_TO_BYTE_SIZE_MAP.find(dataType_)->second;
    }
    return shape_->GetSize() * bytes;
}
// tensor 的shape
std::vector<uint32_t> TensorBase::GetShape() const
{
    if (shape_.get() == nullptr) {
        return std::vector<uint32_t>();
    }
    return shape_->GetShape();
}
// tensor 的 device
int32_t TensorBase::GetDeviceId() const
{
    if (buffer_.get() == nullptr) {
        return -1;
    }
    return buffer_->deviceId;
}
// tensor 数据类型
TensorDataType TensorBase::GetDataType() const
{
    return dataType_;
}

// 获取tensor指针
void* TensorBase::GetBuffer() const
{
    if (buffer_.get() == nullptr) {
        return nullptr;
    }
    return buffer_->data.get();
}

APP_ERROR TensorBase::CheckBatchTensors(const std::vector<TensorBase> &inputs, const bool &checkFirstDim)
{
    auto checkFunc = [checkFirstDim] (const TensorBase &t1, const TensorBase &t2) {
        if (t1.GetShape().size() != t2.GetShape().size()) {
            LogError << "dimension is not match (" << t1.GetShape().size() << ") vs (" << t2.GetShape().size() << ")" << std::endl;
            return false;
        }
        if (t1.GetDeviceId() != t2.GetDeviceId()) {
            LogError << "deviceId is not match (" << t1.GetDeviceId() << ") vs (" << t2.GetDeviceId() << ")" << std::endl;
            return false;
        }
        if (t1.GetDataType() != t2.GetDataType()) {
            LogError << "data type is not match (" << t1.GetDataType() << ") vs (" << t2.GetDataType() << ")" << std::endl;
            return false;
        }
        if (t1.GetTensorType() != t2.GetTensorType()) {
            LogError << "memory type is not match (" << t1.GetTensorType() << ") vs (" << t2.GetTensorType() << ")" << std::endl;
            return false;
        }
        uint32_t startIndex = checkFirstDim ? 0 : 1;
        for (uint32_t i = startIndex; i < t1.GetShape().size(); i++) {
            if (t1.GetShape()[i] == t2.GetShape()[i]) {
                continue;
            }
            std::string shapeStr1 = "(";
            std::string shapeStr2 = "(";
            for (uint32_t j = 0; j < t1.GetShape().size(); j++) {
                shapeStr1 += std::to_string(t1.GetShape()[j]) + ",";
                shapeStr2 += std::to_string(t2.GetShape()[j]) + ",";
            }
            if (shapeStr1.size() > 0) {
                shapeStr1[shapeStr1.size() - 1] = ')';
                shapeStr2[shapeStr2.size() - 1] = ')';
            }
            LogError << "tensor shape is not match " << shapeStr1 << " vs " << shapeStr2 << std::endl;
            return false;
        }
        return true;
    };
    for (uint32_t i = 1; i < inputs.size(); i++) {
        if (!checkFunc(inputs[0], inputs[i])) {
            return APP_ERR_COMM_INVALID_PARAM;;
        }
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBase::BatchConcat(const std::vector<TensorBase> &inputs, TensorBase &output)
{
    // check input size
    if (inputs.size() == 0) {
        LogError << "input size(" << std::to_string(inputs.size()) << ")" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }
    // check
    APP_ERROR ret = CheckBatchTensors(inputs, false);
    if (ret != APP_ERR_OK) {
        LogError << "CheckBatchTensors failed. ret=" << ret << std::endl;
        return ret;
    }
    uint32_t batch = 0;
    for (uint32_t i = 0; i < inputs.size(); i++) {
        batch  += inputs[i].GetShape()[0];
    }
    std::vector<uint32_t> batchShape = {};
    batchShape.push_back(batch);
    for (uint32_t i = 1; i < inputs[0].GetShape().size(); i++) {
        batchShape.push_back(inputs[0].GetShape()[i]);
    }
    // malloc
    output = TensorBase(batchShape, inputs[0].GetDataType(), inputs[0].GetTensorType(), inputs[0].GetDeviceId());
    ret = TensorBaseMalloc(output);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBaseMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    // copy
    uint32_t offset = 0;
    for (uint32_t i = 0; i < inputs.size(); i++) {
        uint8_t *ptr = (uint8_t*)output.GetBuffer() + offset;
        offset += inputs[i].GetByteSize();
        auto patch = TensorBuffer((void*)ptr, inputs[i].GetByteSize());
        patch.type = inputs[i].GetTensorType();
        APP_ERROR ret = TensorBuffer::TensorBufferCopy(patch, *inputs[i].buffer_);
        if (ret != APP_ERR_OK) {
            LogError << "TensorBuffer::TensorBufferCopy failed. ret=" << ret << std::endl;
            return ret;
        }
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBase::BatchStack(const std::vector<TensorBase> &inputs, TensorBase &output)
{
    // check
    if (inputs.size() == 0) {
        LogError << "input size(" << std::to_string(inputs.size()) << ")" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }
    // check shape and device
    APP_ERROR ret = CheckBatchTensors(inputs, true);
    if (ret != APP_ERR_OK) {
        LogError << "CheckBatchTensors failed. ret=" << ret << std::endl;
        return ret;
    }
    std::vector<uint32_t> batchShape = {};
    batchShape.push_back(inputs.size());
    for (uint32_t i = 0; i < inputs[0].GetShape().size(); i++) {
        batchShape.push_back(inputs[0].GetShape()[i]);
    }
    // malloc
    output = TensorBase(batchShape, inputs[0].GetDataType(), inputs[0].GetTensorType(), inputs[0].GetDeviceId());
    ret = TensorBaseMalloc(output);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBaseMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    // copy
    uint32_t offset = 0;
    for (uint32_t i = 0; i < inputs.size(); i++) {
        uint8_t *ptr = (uint8_t*)output.GetBuffer() + offset;
        offset += inputs[i].GetByteSize();
        auto patch = TensorBuffer((void*)ptr, inputs[i].GetByteSize());
        patch.type = inputs[i].GetTensorType();
        APP_ERROR ret = TensorBuffer::TensorBufferCopy(patch, *inputs[i].buffer_);
        if (ret != APP_ERR_OK) {
            LogError << "TensorBuffer::TensorBufferCopy failed. ret=" << ret << std::endl;
            return ret;
        }
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBase::BatchVector(const std::vector<TensorBase> &inputs, TensorBase &output, const bool &keepDims)
{
    if (keepDims) {
        APP_ERROR ret = BatchConcat(inputs, output);
        if (ret != APP_ERR_OK) {
            LogError << "BatchConcat failed. ret=" << ret << std::endl;
            return ret;
        }
    } else {
        APP_ERROR ret = BatchStack(inputs, output);
        if (ret != APP_ERR_OK) {
            LogError << "BatchConcat failed. ret=" << ret << std::endl;
            return ret;
        }
    }
    return APP_ERR_OK;
}

std::string TensorBase::GetDesc()
{
    std::string shapeStr;
    std::vector<uint32_t> shape = GetShape();
    for (size_t i = 0; i < shape.size(); ++i) {
        shapeStr += std::to_string(shape.at(i));
        if (i != shape.size() - 1) {
            shapeStr += ", ";
        }
    }

    return "<Tensor>\nshape:\t(" + shapeStr + \
        ")\ndtype:\t" + GetTensorDataTypeDesc(GetDataType()) + \
        "\ndevice:\t" + std::to_string(GetDeviceId());
}
}
