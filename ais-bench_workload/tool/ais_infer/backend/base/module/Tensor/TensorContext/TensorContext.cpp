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
#include "Base/Tensor/TensorContext/TensorContext.h"
#include "Base/DeviceManager/DeviceManager.h"
#include "Base/Log/Log.h"
#include "acl/acl.h"

namespace {
    const uint32_t MAX_CONTEXT_NUM = 5;
    const uint32_t MAX_QUEUE_LENGHT = 1000;
}
namespace Base {
TensorContext::TensorContext()
{
#ifdef COMPILE_PYTHON_MODULE
    // if (Base::Log::InitPythonModuleLog() != APP_ERR_OK) {
    //     LogWarn << "Failed to initialize log." << std::endl;
    // }
#endif
    if (!DeviceManager::GetInstance()->IsInitDevices()) {
        APP_ERROR ret = DeviceManager::GetInstance()->InitDevices();
        if (ret != APP_ERR_OK) {
            LogError << "DeviceManager InitDevices failed. ret=" << ret << std::endl;
            return;
        }
        InitDeviceFlag_ = true;
    }
}

TensorContext::~TensorContext()
{
    if (InitDeviceFlag_) {
        APP_ERROR ret = DeviceManager::GetInstance()->DestroyDevices();
        if (ret != APP_ERR_OK) {
            LogError << "DeviceManager DestroyDevices failed. ret=" << ret << std::endl;
            return;
        }
        InitDeviceFlag_ = false;
    }
}

APP_ERROR TensorContext::SetContext(const uint32_t &deviceId)
{
    DeviceContext device = {};
    device.devId = deviceId;
    APP_ERROR ret = DeviceManager::GetInstance()->SetDevice(device);
    if (ret != APP_ERR_OK) {
        LogError << "SetDevice failed. ret=" << ret << std::endl;
        return ret;
    }
    return APP_ERR_OK;
}

std::shared_ptr<TensorContext> TensorContext::GetInstance()
{
    static std::shared_ptr<TensorContext> tensorContext = std::make_shared<TensorContext>();
    return tensorContext;
}
}
