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
#ifndef TENSOR_BUFFER_H
#define TENSOR_BUFFER_H

#include <vector>
#include <string>
#include <memory>


#include "Base/MemoryHelper/MemoryHelper.h"
#include "Base/ErrorCode/ErrorCode.h"

namespace Base {

enum TensorBufferCopyType {
    HOST_AND_HOST = 0,
    HOST_AND_DEVICE,
    DEVICE_AND_SAME_DEVICE,
    DEVICE_AND_DIFF_DEVICE
};

class TensorBuffer {
public:
    TensorBuffer() {}
    TensorBuffer(uint32_t size, MemoryData::MemoryType type, int32_t deviceId) 
        : size(size), type(type), deviceId(deviceId) {}
    TensorBuffer(uint32_t size, int32_t deviceId) 
        : size(size), deviceId(deviceId) {}
    TensorBuffer(uint32_t size) : size(size) {}
    TensorBuffer(void *ptr, uint32_t size) : size(size)
    {
        data.reset(ptr, [] (void *p) {});
    }

    bool IsDevice() const
    {
        if (type == MemoryData::MemoryType::MEMORY_DEVICE || type == MemoryData::MemoryType::MEMORY_DVPP) {
            return true;
        }
        return false;
    }

    bool IsHost() const
    {
        return !IsDevice();
    }

    APP_ERROR SetContext() const;
    static APP_ERROR TensorBufferMalloc(TensorBuffer &buffer);
    static APP_ERROR TensorBufferCopy(TensorBuffer &dst, const TensorBuffer &src);

    static TensorBufferCopyType GetBufferCopyType(const TensorBuffer &buffer1, const TensorBuffer &buffer2);
    static APP_ERROR CheckCopyValid(const TensorBuffer &buffer1, const TensorBuffer &buffer2);
    static APP_ERROR CopyBetweenHost(TensorBuffer &dst, const TensorBuffer &src);
    static APP_ERROR CopyBetweenHostDevice(TensorBuffer &dst, const TensorBuffer &src);
    static APP_ERROR CopyBetweenSameDevice(TensorBuffer &dst, const TensorBuffer &src);
    static APP_ERROR CopyBetweenDiffDevice(TensorBuffer &dst, const TensorBuffer &src);

public:
    uint32_t size = 0;
    MemoryData::MemoryType type = MemoryData::MemoryType::MEMORY_HOST_NEW;
    int32_t deviceId = -1;
    std::shared_ptr<void> data = nullptr;
};


}

#endif