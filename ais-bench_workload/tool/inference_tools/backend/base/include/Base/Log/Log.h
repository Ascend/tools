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

#ifndef CORE_LOG_H
#define CORE_LOG_H

#include <vector>
#include <string>
#include <map>
#include <memory>
#include <ostream>
//#include <glog/logging.h>
#include <csignal>
#include <execinfo.h>
//#include "Base/ErrorCode/ErrorCode.h"

#include <iostream>

using namespace std;
#define FILELINE __FILE__, __FUNCTION__, __LINE__
#define LogDebug  cout  //LOG(INFO)   // VLOG_EVERY_N(Base::LOG_LEVEL_DEBUG, Base::Log::logFlowControlFrequency_)
#define LogInfo   cout       // LOG(INFO)        //LOG_EVERY_N(INFO, Base::Log::logFlowControlFrequency_)
#define LogWarn   cout  // LOG(WARNING)    //LOG_EVERY_N(WARNING, Base::Log::logFlowControlFrequency_)
#define LogError  cout     //LOG(ERROR)    // LOG_EVERY_N(ERROR, Base::Log::logFlowControlFrequency_)
#define LogFatal  cout      // LOG(FATAL)    //LOG_EVERY_N(FATAL, Base::Log::logFlowControlFrequency_)

#define LOG_DEBUG_LEVEL 1
#define LOG_INFO_LEVEL 2
#define LOG_WARNING_LEVEL 3
#define LOG_ERROR_LEVEL 4

extern int FRIZY_LOG_LEVEL;

void SETLOGLEVEL(int level);

#define DEBUG_LOG(fmt, args...)  do { if (FRIZY_LOG_LEVEL <= LOG_DEBUG_LEVEL) { fprintf(stdout, "[DEBUG] " fmt "\n", ##args); } else {} } while (0)
#define INFO_LOG(fmt, args...)  do { if (FRIZY_LOG_LEVEL <= LOG_INFO_LEVEL) { fprintf(stdout, "[INFO] " fmt "\n", ##args); } else {} } while (0)
#define WARN_LOG(fmt, args...)  do { if (FRIZY_LOG_LEVEL <= LOG_WARNING_LEVEL) { fprintf(stdout, "[WARN] " fmt "\n", ##args); } else {} } while (0)
#define ERROR_LOG(fmt, args...)  do { if (FRIZY_LOG_LEVEL <= LOG_ERROR_LEVEL) { fprintf(stdout, "[ERROR] " fmt "\n", ##args); } else {} } while (0)

#endif  // CORE_LOG_H