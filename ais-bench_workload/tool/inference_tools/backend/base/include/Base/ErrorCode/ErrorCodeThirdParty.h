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

#ifndef ERROR_CODE_THIRD_PARTY_H
#define ERROR_CODE_THIRD_PARTY_H

enum {
    APP_ERR_FLOW_CUSTOM_SUCCESS_2 = 102,
    APP_ERR_FLOW_CUSTOM_SUCCESS_1 = 101,
    APP_ERR_FLOW_CUSTOM_SUCCESS = 100,
    APP_ERR_FLOW_OK		  =  0,
    APP_ERR_FLOW_NOT_LINKED     = -1,
    APP_ERR_FLOW_FLUSHING       = -2,
    APP_ERR_FLOW_EOS            = -3,
    APP_ERR_FLOW_NOT_NEGOTIATED = -4,
    APP_ERR_FLOW_ERROR	  = -5,
    APP_ERR_FLOW_NOT_SUPPORTED  = -6,
    APP_ERR_FLOW_CUSTOM_ERROR   = -100,
    APP_ERR_FLOW_CUSTOM_ERROR_1 = -101,
    APP_ERR_FLOW_CUSTOM_ERROR_2 = -102
};

#endif  // ERROR_CODE_H_