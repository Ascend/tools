/**
* Copyright 2020 Huawei Technologies Co., Ltd
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at

* http://www.apache.org/licenses/LICENSE-2.0

* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

#include "sample_process.h"
#include "acl/acl.h"
#include "model_process.h"
#include "utils.h"
using namespace std;
extern bool g_isDevice;
extern bool f_isTXT;
extern int loop;
extern int32_t device;
extern bool is_debug;
extern bool is_profi;
extern bool is_dump;

SampleProcess::SampleProcess()
    : deviceId_(0)
    , context_(nullptr)
    , stream_(nullptr)
{
}

SampleProcess::~SampleProcess()
{
    DestroyResource();
}

Result SampleProcess::InitResource()
{
    // ACL init
    aclError ret;
    const char* aclConfigPath = "./acl.json";
    ifstream acl_file(aclConfigPath);
    if (is_profi || is_dump || acl_file) {
        ret = aclInit(aclConfigPath);
    } 
    else {
        ret = aclInit(nullptr);
    }
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("acl init failed");
        return FAILED;
    }
    INFO_LOG("acl init success");

    // open device
    deviceId_ = device;
    ret = aclrtSetDevice(deviceId_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("acl open device %d failed", deviceId_);
        return FAILED;
    }
    INFO_LOG("open device %d success", deviceId_);

    // create context (set current)
    ret = aclrtCreateContext(&context_, deviceId_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("acl create context failed");
        return FAILED;
    }
    INFO_LOG("create context success");

    // create stream
    ret = aclrtCreateStream(&stream_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("acl create stream failed");
        return FAILED;
    }
    INFO_LOG("create stream success");

    // get run mode
    aclrtRunMode runMode;
    ret = aclrtGetRunMode(&runMode);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("acl get run mode failed");
        return FAILED;
    }
    g_isDevice = (runMode == ACL_DEVICE);
    INFO_LOG("get run mode success");

    return SUCCESS;
}

Result SampleProcess::Process(map<char, string>& params, vector<string>& input_files)
{
    // model init
    ModelProcess processModel;
    const std::string& omModelPath = params['m'];
    std::string output_path = params['o'].c_str();
    const char* outfmt = params['f'].c_str();
    const char* fmt_TXT = "TXT";
    f_isTXT = (strcmp(outfmt, fmt_TXT) == 0);

    std::string modelPath = params['m'].c_str();
    std::string modelName = Utils::modelName(modelPath);

    struct timeval begin;
    struct timeval end;
    double inference_time[loop];
    Result ret = processModel.LoadModelFromFileWithMem(omModelPath);
    if (ret != SUCCESS) {
        ERROR_LOG("load model from file failed");
        return FAILED;
    }

    ret = processModel.CreateDesc();
    if (ret != SUCCESS) {
        ERROR_LOG("create model description failed");
        return FAILED;
    }

    if (is_debug) {
        ret = processModel.PrintDesc();
        if (ret != SUCCESS) {
            ERROR_LOG("print model descrtption failed");
            return FAILED;
        }
    }
    ret = processModel.CreateOutput();
    if (ret != SUCCESS) {
        ERROR_LOG("create model output failed");
        return FAILED;
    }

    if (input_files.empty() == 1) {
        ret = processModel.CreateZeroInput();
        if (ret != SUCCESS) {
            ERROR_LOG("model create input failed");
            return FAILED;
        }
    } else {
        vector<void*> picDevBuffer(input_files.size(), nullptr);
        for (size_t index = 0; index < input_files.size(); ++index) {
            INFO_LOG("start to process file:%s", input_files[index].c_str());
            // model process
            uint32_t devBufferSize;
            picDevBuffer[index] = Utils::GetDeviceBufferOfFile(input_files[index], devBufferSize);
            if (picDevBuffer[index] == nullptr) {
                ERROR_LOG("get pic device buffer failed,index is %zu", index);
                return FAILED;
            }

            ret = processModel.CreateInput(picDevBuffer[index], devBufferSize);
            if (ret != SUCCESS) {
                ERROR_LOG("model create input failed");
                return FAILED;
            }
        }
    }

    // loop end
    for (size_t t = 0; t < loop; ++t) {
        gettimeofday(&begin, NULL);
        ret = processModel.Execute();
        gettimeofday(&end, NULL);
        inference_time[t] = 1000 * (end.tv_sec - begin.tv_sec) + (end.tv_usec - begin.tv_usec) / 1000.000;
        std::cout << "Inference time: " << inference_time[t] << "ms" << endl;
        if (ret != SUCCESS) {
            ERROR_LOG("model execute failed");
            return FAILED;
        }
        processModel.OutputModelResult(output_path, modelName, t);
    }
    double infer_time_ave = Utils::InferenceTimeAverage(inference_time, loop);
    printf("Inference average time: %f ms\n", infer_time_ave);
    if (loop > 1) {
        double infer_time_ave_without_first = Utils::InferenceTimeAverageWithoutFirst(inference_time, loop);
        printf("Inference average time without first time: %f ms\n", infer_time_ave_without_first);
    }
    processModel.DestroyInput();
    processModel.DestroyOutput();

    if (is_dump || is_profi) {
        if (remove("acl.json") == 0) {
            INFO_LOG("delete acl.json success");
        } else {
            ERROR_LOG("delete acl.json failed");
        }
    }

    return SUCCESS;
}

void SampleProcess::DestroyResource()
{
    aclError ret;
    if (stream_ != nullptr) {
        ret = aclrtDestroyStream(stream_);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("destroy stream failed");
        }
        stream_ = nullptr;
    }
    INFO_LOG("end to destroy stream");

    if (context_ != nullptr) {
        ret = aclrtDestroyContext(context_);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("destroy context failed");
        }
        context_ = nullptr;
    }
    INFO_LOG("end to destroy context");

    ret = aclrtResetDevice(deviceId_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("reset device failed");
    }
    INFO_LOG("end to reset device is %d", deviceId_);

    ret = aclFinalize();
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("finalize acl failed");
    }
    INFO_LOG("end to finalize acl");
}
