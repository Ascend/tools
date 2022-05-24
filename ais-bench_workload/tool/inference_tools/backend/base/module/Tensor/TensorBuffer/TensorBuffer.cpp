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
#include "Base/Tensor/TensorBuffer/TensorBuffer.h"
#include "Base/Tensor/TensorContext/TensorContext.h"
#include "Base/Log/Log.h"

namespace Base {
APP_ERROR TensorBuffer::SetContext() const
{
    if (IsDevice()) {
        APP_ERROR ret = TensorContext::GetInstance()->SetContext(deviceId);
        if (ret != APP_ERR_OK) {
            LogError << "SetContext failed. ret=" << ret << std::endl;
            return ret;
        }
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBuffer::TensorBufferMalloc(TensorBuffer &buffer)
{
    // SetContext
    APP_ERROR ret = buffer.SetContext();
    if (ret != APP_ERR_OK) {
        LogError << "SetContext failed. ret=" << ret << std::endl;
        return ret;
    }

    // Malloc
    Base::MemoryData memorydata(buffer.size, buffer.type, buffer.deviceId);
    ret = MemoryHelper::MxbsMalloc(memorydata);
    if (ret != APP_ERR_OK) {
        LogError << "MemoryHelper::MxbsMalloc failed. ret=" << ret << std::endl;
        return ret;
    }
    const TensorBuffer buf = buffer;
    auto deleter = [buf] (void *p) {
        buf.SetContext();
        Base::MemoryData memoryData(p, buf.size, buf.type, buf.deviceId);
        Base::MemoryHelper::Free(memoryData);
    };
    buffer.data.reset(memorydata.ptrData, deleter);
    return APP_ERR_OK;
}

APP_ERROR TensorBuffer::CheckCopyValid(const TensorBuffer &buffer1, const TensorBuffer &buffer2)
{
    if (buffer1.size != buffer2.size) {
        LogError << "param1 data size(" << buffer1.size << ") not match to param2 size(" << buffer2.size << ")" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }

    if (buffer1.data.get() == nullptr) {
        LogError << "param1 pointer is nullptr" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }

    if (buffer2.data.get() == nullptr) {
        LogError << "param2 pointer is nullptr" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }

    return APP_ERR_OK;
}
TensorBufferCopyType TensorBuffer::GetBufferCopyType(const TensorBuffer &buffer1, const TensorBuffer &buffer2)
{
    if (buffer1.IsHost() && buffer2.IsHost()) {
        return TensorBufferCopyType::HOST_AND_HOST;
    }

    if (buffer1.IsDevice() && buffer2.IsHost()) {
        return TensorBufferCopyType::HOST_AND_DEVICE;
    }

    if (buffer1.IsHost() && buffer2.IsDevice()) {
        return TensorBufferCopyType::HOST_AND_DEVICE;
    }

    if (buffer1.deviceId != buffer2.deviceId) {
        return TensorBufferCopyType::DEVICE_AND_DIFF_DEVICE;
    }
    return TensorBufferCopyType::DEVICE_AND_SAME_DEVICE;
}


APP_ERROR TensorBuffer::CopyBetweenHost(TensorBuffer &dst, const TensorBuffer &src)
{
    APP_ERROR ret = CheckCopyValid(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "CheckCopyValid failed. ret=" << ret << std::endl;
        return ret;
    }

    std::copy((uint8_t*) src.data.get(), (uint8_t*)src.data.get() + src.size, (uint8_t*)dst.data.get());
    return APP_ERR_OK;
}
APP_ERROR TensorBuffer::CopyBetweenHostDevice(TensorBuffer &dst, const TensorBuffer &src)
{
    APP_ERROR ret = CheckCopyValid(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "CheckCopyValid failed. ret=" << ret << std::endl;
        return ret;
    }

    if (dst.IsHost() && src.IsDevice()) {
        ret = src.SetContext();
        if (ret != APP_ERR_OK) {
            LogError << "SetContext failed. ret=" << ret << std::endl;
            return ret;
        }
    }

    if (dst.IsDevice() && src.IsHost()) {
        ret = dst.SetContext();
        if (ret != APP_ERR_OK) {
            LogError << "SetContext failed. ret=" << ret << std::endl;
            return ret;
        }
    }

    MemoryData dstMemory(dst.data.get(), dst.size, dst.type, dst.deviceId);
    MemoryData srcMemory(src.data.get(), src.size, src.type, src.deviceId);
    ret = MemoryHelper::MxbsMemcpy(dstMemory, srcMemory, dst.size);
    if (ret != APP_ERR_OK) {
        LogError << "MemoryHelper::MxbsMemcpy failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}
APP_ERROR TensorBuffer::CopyBetweenSameDevice(TensorBuffer &dst, const TensorBuffer &src)
{
    APP_ERROR ret = CheckCopyValid(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "CheckCopyValid failed. ret=" << ret << std::endl;
        return ret;
    }

    ret = src.SetContext();
    if (ret != APP_ERR_OK) {
        LogError << "SetContext failed. ret=" << ret << std::endl;
        return ret;
    }

    MemoryData dstMemory(dst.data.get(), dst.size, dst.type, dst.deviceId);
    MemoryData srcMemory(src.data.get(), src.size, src.type, src.deviceId);
    ret = MemoryHelper::MxbsMemcpy(dstMemory, srcMemory, dst.size);
    if (ret != APP_ERR_OK) {
        LogError << "MemoryHelper::MxbsMemcpy failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBuffer::CopyBetweenDiffDevice(TensorBuffer &dst, const TensorBuffer &src)
{
    APP_ERROR ret = CheckCopyValid(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "CheckCopyValid failed. ret=" << ret << std::endl;
        return ret;
    }

    TensorBuffer host(src.size);
    ret = TensorBuffer::TensorBufferMalloc(host);
    if (ret != APP_ERR_OK) {
        LogError << "TensorBuffer::TensorBufferMalloc failed. ret=" << ret << std::endl;
        return ret;
    }

    ret = CopyBetweenHostDevice(host, src);
    if (ret != APP_ERR_OK) {
        LogError << "CopyBetweenHostDevice failed. ret=" << ret << std::endl;
        return ret;
    }

    ret = CopyBetweenHostDevice(dst, host);
    if (ret != APP_ERR_OK) {
        LogError << "CopyBetweenHostDevice failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR TensorBuffer::TensorBufferCopy(TensorBuffer &dst, const TensorBuffer &src)
{
    APP_ERROR ret = CheckCopyValid(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "CheckCopyValid failed. ret=" << ret << std::endl;
        return ret;
    }

    auto copyType = GetBufferCopyType(dst, src);
    // host to host
    if (copyType == TensorBufferCopyType::HOST_AND_HOST) {
        ret = CopyBetweenHost(dst, src);
        if (ret != APP_ERR_OK) {
            LogError << "CopyBetweenHost failed. ret=" << ret << std::endl;
            return ret;
        }
        return APP_ERR_OK;
    }
    // device to host or host to device
    if (copyType == TensorBufferCopyType::HOST_AND_DEVICE) {
        ret = CopyBetweenHostDevice(dst, src);
        if (ret != APP_ERR_OK) {
            LogError << "CopyBetweenHostDevice failed. ret=" << ret << std::endl;
            return ret;
        }
        return APP_ERR_OK;
    }

    // devie a to device a
    if (copyType == TensorBufferCopyType::DEVICE_AND_SAME_DEVICE) {
        ret = CopyBetweenSameDevice(dst, src);
        if (ret != APP_ERR_OK) {
            LogError << "CopyBetweenHostDevice failed. ret=" << ret << std::endl;
            return ret;
        }
        return ret;
    }
    // device a to device b
    ret = CopyBetweenDiffDevice(dst, src);
    if (ret != APP_ERR_OK) {
        LogError << "CopyBetweenDiffDevice failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}
}