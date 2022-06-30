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
#ifndef TENSOR_CONTEXT_H
#define TENSOR_CONTEXT_H

#include <map>
#include <memory>
#include <mutex>

#include "Base/ErrorCode/ErrorCode.h"

namespace Base {


enum ContextMode {
    CONTEXT_IDEL = 0,
    CONTEXT_USING
};

struct ContextStatus {
    uint32_t deviceId = 0;
    ContextMode status = CONTEXT_IDEL;
};

class TensorContext
{
public:
    TensorContext();
    ~TensorContext();
    static std::shared_ptr<TensorContext> GetInstance();
    APP_ERROR SetContext(const uint32_t &deviceId);
private:
    bool InitDeviceFlag_ = false;
};
}
#endif