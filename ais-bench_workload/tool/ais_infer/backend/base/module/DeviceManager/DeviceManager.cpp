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
#include <iostream>
#include <memory>
#include "acl/acl.h"
#include "acl/acl_base.h"
#include "Base/Log/Log.h"
#include "Base/DeviceManager/DeviceManager.h"

namespace Base {
DeviceManager::~DeviceManager()
{
    std::lock_guard<std::mutex> lock(mtx_);
    if (initCounter_ != 0) {
        LogDebug << "DeviceManager Acl Resource is not released." << std::endl;
        return;
    }
}

DeviceManager* DeviceManager::GetInstance()
{
    static DeviceManager deviceManager;
    return &deviceManager;
}

bool DeviceManager::IsInitDevices() const
{
    bool status = initCounter_ > 0;
    return status;
}

void DeviceManager::SetAclJsonPath(std::string aclJsonPath)
{
    aclJsonPath_ = aclJsonPath;
}

/**
 * @description: initialize all devices
 * @param: configFilePath
 * @return: init_device_result
 */
APP_ERROR DeviceManager::InitDevices(std::string configFilePath)
{
    std::lock_guard<std::mutex> lock(mtx_);
    initCounter_++;
    if (initCounter_ > 1) {
        return APP_ERR_OK;
    }

    APP_ERROR ret = aclInit(aclJsonPath_.c_str());
    if (ret != APP_ERR_OK) {
        initCounter_ = 0;
        LogError << "Failed to initialize all devices: " << GetAppErrCodeInfo(ret) << ".\n";
        return ret;
    }
    ret = aclrtGetDeviceCount(&deviceCount_);
    if (ret != APP_ERR_OK) {
        initCounter_ = 0;
        aclFinalize();
        LogError << "Failed to get all devices count: " << GetAppErrCodeInfo(ret) << ".\n";
        return ret;
    }
    return APP_ERR_OK;
}

/**
 * @description: release all devices
 * @param: void
 * @return: destory_devices_result
 */
APP_ERROR DeviceManager::DestroyDevices()
{
    std::lock_guard<std::mutex> lock(mtx_);
    if (initCounter_ == 0) {
        return APP_ERR_COMM_OUT_OF_RANGE;
    }
    initCounter_--;
    if (initCounter_ == 0) {
        LogDebug << "DestroyDevices begin";
        for (auto item : contexts_) {
            LogDebug << "destory device:" << item.first << std::endl;
            APP_ERROR ret = aclrtDestroyContext(item.second.get());
            if (ret != APP_ERR_OK) {
                LogError << "aclrtDestroyContext failed. ret=" << ret << std::endl;
                return ret;
            }
            LogDebug << "aclrtDestroyContext successfully!" << std::endl;
        }
        contexts_.clear();
        APP_ERROR ret = aclFinalize();
        if (ret != APP_ERR_OK) {
            LogError << "Failed to release all devices: " << GetAppErrCodeInfo(ret) << "." << std::endl;
            return ret;
        }
        LogDebug << "DestroyDevices successfully" << std::endl;
        return APP_ERR_OK;
    }
    if (initCounter_ > 0) {
        return APP_ERR_OK;
    }

    return APP_ERR_OK;
}

/**
 * @description: get all devices count
 * @param: deviceCount
 * @return: get_devices_count_result
 */
APP_ERROR DeviceManager::GetDevicesCount(uint32_t& deviceCount)
{
    deviceCount = deviceCount_;
    return APP_ERR_OK;
}

/**
 * @description: get current running device
 * @param: device
 * @return: get_current_device_result
 */
APP_ERROR DeviceManager::GetCurrentDevice(DeviceContext& device)
{
    std::lock_guard<std::mutex> lock(mtx_);
    aclrtContext currentContext = nullptr;
    APP_ERROR ret = aclrtGetCurrentContext(&currentContext);
    if (ret != APP_ERR_OK) {
        LogError << "aclrtGetCurrentContext failed. ret=" << ret << std::endl;
        return ret;
    }
    DeviceContext currentDevice = {};
    currentDevice.devStatus = DeviceContext::DeviceStatus::USING;
    currentDevice.devId = -1;
    for (const auto &item : contexts_) {
        if (item.second.get() == currentContext) {
            currentDevice.devId = item.first;
        }
    }
    device = currentDevice;
    return APP_ERR_OK;
}

APP_ERROR DeviceManager::SetDeviceSimple(DeviceContext device)
{
    return SetDevice(device);
}

/**
 * @description: set one device for running
 * @param: device
 * @return: set_device_result
 */
APP_ERROR DeviceManager::SetDevice(DeviceContext device)
{
    std::lock_guard<std::mutex> lock(mtx_);
    auto deviceId = device.devId;
    if (contexts_.find(device.devId) == contexts_.end()) {
        aclrtContext newContext = nullptr;
        APP_ERROR ret = aclrtCreateContext(&newContext, device.devId);
        if (ret != APP_ERR_OK) {
            LogError << "aclrtCreateContext failed. ret=" << ret << std::endl;
            return ret;
        }
        std::shared_ptr<void> context(newContext, [] (void *c) {});
        contexts_[device.devId] = context;
    } else {
        APP_ERROR ret = aclrtSetCurrentContext(contexts_[deviceId].get());
        if (ret != APP_ERR_OK) {
            LogError << "aclrtSetCurrentContext failed. ret=" << ret << std::endl;
            return ret;
        }
    }
    return APP_ERR_OK;
}

/**
 * @description: free resources for one device
 * @param: device
 * @return: reset_device_result
 */
APP_ERROR DeviceManager::ResetDevice(DeviceContext device)
{
    return APP_ERR_OK;
}

/**
 * @description: check device id
 * @param: deviceId
 * @return: check_device_id_result
 */
APP_ERROR DeviceManager::CheckDeviceId(int32_t deviceId)
{
    if (deviceId < 0) {
        LogError << "deviceId(" << deviceId << ") is less than 0" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }

    if (deviceId > (int32_t)deviceCount_ - 1) {
        LogError << "deviceId(" << deviceId << ") is bigger than deviceCount(" << deviceCount_ << ")" << std::endl;
        return APP_ERR_COMM_INVALID_PARAM;
    }
    return APP_ERR_OK;
}
}  // namespace Base