/*
 * Copyright(C) 2020. Huawei Technologies Co.,Ltd. All rights reserved.
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

#ifndef MEMORY_HELPER_H
#define MEMORY_HELPER_H
#include "Base/ErrorCode/ErrorCode.h"

namespace Base {
struct MemoryData {
    enum MemoryType {
        MEMORY_HOST,
        MEMORY_DEVICE,
        MEMORY_DVPP,
        MEMORY_HOST_MALLOC,
        MEMORY_HOST_NEW,
    };

    MemoryData() = default;

    MemoryData(size_t size, MemoryType type = MEMORY_HOST, size_t deviceId = 0)
        : size(size), deviceId(deviceId), type(type) {}

    MemoryData(void* ptrData, size_t size, MemoryType type = MEMORY_HOST, size_t deviceId = 0)
        : ptrData(ptrData), size(size), deviceId(deviceId), type(type) {}

    void* ptrData = nullptr;
    size_t size;
    size_t deviceId;
    MemoryType type;
    APP_ERROR (*free)(void*) = nullptr;
};

class MemoryHelper {
public:
    // malloc memory
    static APP_ERROR Malloc(MemoryData& data);
    static APP_ERROR Free(MemoryData& data);
    static APP_ERROR Memset(MemoryData& data, int32_t value, size_t count);
    static APP_ERROR Memcpy(MemoryData& dest, const MemoryData& src, size_t count);

    static APP_ERROR MxbsMalloc(MemoryData& data);
    static APP_ERROR MxbsFree(MemoryData& data);
    static APP_ERROR MxbsMemset(MemoryData& data, int32_t value, size_t count);
    static APP_ERROR MxbsMemcpy(MemoryData& dest, const MemoryData& src, size_t count);
    static APP_ERROR MxbsMallocAndCopy(MemoryData& dest, const MemoryData& src);

private:
    static bool IsDeviceToHost(const MemoryData& dest, const MemoryData& src);
    static bool IsHostToHost(const MemoryData& dest, const MemoryData& src);
    static bool IsDeviceToDevice(const MemoryData& dest, const MemoryData& src);
    static bool IsHostToDevice(const MemoryData& dest, const MemoryData& src);
};
}  // namespace Base
#endif