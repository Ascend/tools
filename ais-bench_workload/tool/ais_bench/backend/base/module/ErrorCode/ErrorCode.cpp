/*
 * Copyright (c) 2020.Huawei Technologies Co., Ltd. All rights reserved.
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

#include "Base/Log/Log.h"
#include "Base/ErrorCode/ErrorCode.h"
#include "Base/ErrorCode/ErrorCodeThirdParty.h"

namespace {
template<typename T>
static int GetArrayLen(T& arr)
{
    return (sizeof(arr) / sizeof(arr[0]));
}

std::map<int, int> GST_RETURN_CODE_MAP = {
    {APP_ERR_FLOW_CUSTOM_SUCCESS_2, APP_ERR_OK},
    {APP_ERR_FLOW_CUSTOM_SUCCESS_1, APP_ERR_OK},
    {APP_ERR_FLOW_CUSTOM_SUCCESS, APP_ERR_OK},
    {APP_ERR_FLOW_OK, APP_ERR_OK},
    {APP_ERR_FLOW_NOT_LINKED, APP_ERR_PLUGIN_TOOLKIT_FLOW_NOT_LINKED},
    {APP_ERR_FLOW_FLUSHING, APP_ERR_PLUGIN_TOOLKIT_FLOW_FLUSHING},
    {APP_ERR_FLOW_EOS, APP_ERR_PLUGIN_TOOLKIT_FLOW_EOS},
    {APP_ERR_FLOW_NOT_NEGOTIATED, APP_ERR_PLUGIN_TOOLKIT_FLOW_NOT_NEGOTIATED},
    {APP_ERR_FLOW_ERROR, APP_ERR_PLUGIN_TOOLKIT_FLOW_ERROR},
    {APP_ERR_FLOW_NOT_SUPPORTED, APP_ERR_PLUGIN_TOOLKIT_FLOW_NOT_SUPPORTED},
    {APP_ERR_FLOW_CUSTOM_ERROR, APP_ERR_PLUGIN_TOOLKIT_FLOW_NOT_SUPPORTED},
    {APP_ERR_FLOW_CUSTOM_ERROR_1, APP_ERR_PLUGIN_TOOLKIT_FLOW_NOT_SUPPORTED},
    {APP_ERR_FLOW_CUSTOM_ERROR_2, APP_ERR_PLUGIN_TOOLKIT_FLOW_NOT_SUPPORTED},
};
std::map<int, std::pair<const std::string *, int>> ErrMsgMap = {
    {APP_ERR_ACL_ERR_BASE, std::make_pair(APP_ERR_ACL_LOG_STRING, GetArrayLen(APP_ERR_ACL_LOG_STRING))},
    {APP_ERR_COMM_BASE, std::make_pair(APP_ERR_COMMON_LOG_STRING, GetArrayLen(APP_ERR_COMMON_LOG_STRING))},
    {APP_ERR_DVPP_BASE, std::make_pair(APP_ERR_DVPP_LOG_STRING, GetArrayLen(APP_ERR_DVPP_LOG_STRING))},
    {APP_ERR_INFER_BASE, std::make_pair(APP_ERR_INFER_LOG_STRING, GetArrayLen(APP_ERR_INFER_LOG_STRING))},
    {APP_ERR_QUEUE_BASE, std::make_pair(APP_ERR_QUEUE_LOG_STRING, GetArrayLen(APP_ERR_QUEUE_LOG_STRING))},
    {APP_ERR_COMMANDER_BASE, std::make_pair(APP_ERR_COMMANDER_STRING, GetArrayLen(APP_ERR_COMMANDER_STRING))},
    {APP_ERR_STREAM_BASE, std::make_pair(APP_ERR_STREAM_LOG_STRING, GetArrayLen(APP_ERR_STREAM_LOG_STRING))},
    {APP_ERR_PLUGIN_TOOLKIT_BASE, std::make_pair(APP_ERR_PLUGIN_TOOLKIT_LOG_STRING,
                                                 GetArrayLen(APP_ERR_PLUGIN_TOOLKIT_LOG_STRING))},
    {APP_ERR_DEVICE_MANAGER_BASE, std::make_pair(APP_ERR_DEVICE_MANAGER_LOG_STRING,
                                                 GetArrayLen(APP_ERR_DEVICE_MANAGER_LOG_STRING))},
    {APP_ERR_EXTRA_BASE, std::make_pair(APP_ERR_EXTRA_STRING, GetArrayLen(APP_ERR_EXTRA_STRING))},
    {APP_ERR_BAD_ALLOC, std::make_pair(APP_ERR_INFER_STRING, GetArrayLen(APP_ERR_INFER_STRING))},
    {APP_ERR_STORAGE_OVER_LIMIT, std::make_pair(APP_ERR_STORAGE_STRING, GetArrayLen(APP_ERR_STORAGE_STRING))},
    {APP_ERR_INTERNAL_ERROR, std::make_pair(APP_ERR_INTERNAL_STRING, GetArrayLen(APP_ERR_INTERNAL_STRING))}
};
template<typename T>
static std::string GetErrMsg(T& messages, int offset, int len)
{
    return (offset < len) ? messages[offset] : "Undefined error code";
}
}

/**
 * @description: Get error message by code
 * @param err
 * @return message
 */
std::string GetAppErrCodeInfo(const APP_ERROR err)
{
    if (err == APP_ERR_ACL_FAILURE) {
        return "ACL: general failure";
    }
    int base = (err / RANGE_SIZE) * RANGE_SIZE;
    int offset = err % RANGE_SIZE;
    if (ErrMsgMap.find(base) != ErrMsgMap.end() && (offset >= 0)) {
        auto array = ErrMsgMap[base].first;
        auto arraySize = ErrMsgMap[base].second;
        return GetErrMsg(array, offset, arraySize);
    } else {
        return "Error code unknown";
    }
}

/**
 * @brief Concat the error info with the module name for LogError output
 * @param err
 * @param moduleName
 * @return
 */
std::string GetError(const APP_ERROR err, const std::string moduleName)
{
    if (moduleName.empty()) {
        return "[" + std::to_string(err) + "]" + "[" + GetAppErrCodeInfo(err) + "] ";
    } else {
        return "[" + moduleName + "][" + std::to_string(err) + "]" + "[" + GetAppErrCodeInfo(err) + "] ";
    }
}

APP_ERROR ConvertReturnCodeToLocal(ReturnCodeType type, int err)
{
    if (type == GST_FLOW_TYPE) {
        if (GST_RETURN_CODE_MAP.find(err) != GST_RETURN_CODE_MAP.end()) {
            return GST_RETURN_CODE_MAP[err];
        } else {
            LogDebug << "type(GST_FLOW_TYPE) can not find error code(" << err << ").";
        }
    }
    return APP_ERR_OK;
}