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

#include "model_process.h"
#include "utils.h"
#include <cstddef>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>

using namespace std;
extern bool g_is_device;
extern bool g_is_txt;
extern size_t g_dymindex;

ModelProcess::ModelProcess()
    : modelId_(0)
    , loadFlag_(false)
    , modelDesc_(nullptr)
    , input_(nullptr)
    , output_(nullptr)
    , numInputs_(0)
    , numOutputs_(0)
{
}

ModelProcess::~ModelProcess()
{
    Unload();
    DestroyDesc();
    DestroyInput();
    DestroyOutput();
}

Result ModelProcess::LoadModelFromFile(const string& modelPath)
{
    if (loadFlag_) {
        ERROR_LOG("has already loaded a model");
        return FAILED;
    }

    aclError ret = aclmdlLoadFromFile(modelPath.c_str(), &modelId_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("load model from file failed, model file is %s", modelPath.c_str());
        return FAILED;
    }

    loadFlag_ = true;
    INFO_LOG("load model %s success", modelPath.c_str());
    return SUCCESS;
}

Result ModelProcess::CreateDesc()
{
    modelDesc_ = aclmdlCreateDesc();
    if (modelDesc_ == nullptr) {
        ERROR_LOG("create model description failed");
        return FAILED;
    }

    aclError ret = aclmdlGetDesc(modelDesc_, modelId_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("get model description failed");
        return FAILED;
    }

    INFO_LOG("create model description success");

    return SUCCESS;
}

Result ModelProcess::GetDynamicGearCount(size_t &dymGearCount)
{
    aclError ret; 
    ret = aclmdlGetInputDynamicGearCount(modelDesc_, -1, &dymGearCount);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("get input dynamic gear count failed");
        return FAILED;
    }
    
    INFO_LOG("get input dynamic gear count success");

    return SUCCESS;
}

Result ModelProcess::GetDynamicIndex(size_t &dymTensorIndex)
{
    aclError ret; 
    ret = aclmdlGetInputIndexByName(modelDesc_, ACL_DYNAMIC_TENSOR_NAME, &dymTensorIndex);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("get input index by name failed %d", ret);
        return FAILED;
    }

    INFO_LOG("get input index by name success");
    return SUCCESS;
}

Result ModelProcess::CheckDynamicDims(vector<string> dymDims, size_t gearCount, aclmdlIODims *dims)
{
    aclmdlGetInputDynamicDims(modelDesc_, -1, dims, gearCount);
    bool if_same = false;
    for (size_t i = 0; i < gearCount; i++)
    {
        if ((size_t)dymDims.size() != dims[i].dimCount){
            ERROR_LOG("the dynamic_dims parameter is not correct");
            GetDimInfo(gearCount, dims);
            return FAILED;
        }
        for (size_t j = 0; j < dims[i].dimCount; j++)
        {  
            if (dims[i].dims[j] != atoi(dymDims[j].c_str()))
            {
                break;
            }
            if (j == dims[i].dimCount - 1)
            {
                if_same = true;
            }
        }
        
    }

    if(! if_same){
        ERROR_LOG("the dynamic_dims parameter is not correct");
        GetDimInfo(gearCount, dims);
        return FAILED;  
    }
    INFO_LOG("check dynamic dims success");
    return SUCCESS;
 
}

Result ModelProcess::SetDynamicDims(vector<string> dymDims)
{   
    aclmdlIODims dims;
    dims.dimCount = dymDims.size();
    for (size_t i = 0; i < dims.dimCount; i++)
    {   
        dims.dims[i] = atoi(dymDims[i].c_str());
    }

    aclError ret = aclmdlSetInputDynamicDims(modelId_, input_, g_dymindex, &dims);
 
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("aclmdlSetInputDynamicDims failed %d", ret);
        return FAILED;
    }
    INFO_LOG("set dynamic dims success");
    return SUCCESS; 
}

void ModelProcess::GetDimInfo(size_t gearCount, aclmdlIODims *dims)
{
    aclmdlGetInputDynamicDims(modelDesc_, -1, dims, gearCount);

    for (size_t i = 0; i < gearCount; i++)
    {
        if (i == 0)
        {
            INFO_LOG("model has %zu gear of dims", gearCount); 
        }
        stringstream ss;
        ss << "dims[" << i << "]:";
        for (size_t j = 0; j < dims[i].dimCount; j++)
        {
            ss << "[" << dims[i].dims[j] << "]";  
        }
        INFO_LOG("%s", ss.str().c_str()); 
    }
}

Result ModelProcess::PrintDesc()
{
    aclError ret;
    DEBUG_LOG("start print model description");
    size_t numInputs = aclmdlGetNumInputs(modelDesc_);
    size_t numOutputs = aclmdlGetNumOutputs(modelDesc_);
    DEBUG_LOG("NumInputs: %zu", numInputs);
    DEBUG_LOG("NumOutputs: %zu", numOutputs);

    aclmdlIODims dimsInput;
    aclmdlIODims dimsOutput;
    aclmdlIODims dimsCurrentOutput;
    for (size_t i = 0; i < numInputs; i++) {
        DEBUG_LOG("the size of %zu input: %zu", i, aclmdlGetInputSizeByIndex(modelDesc_, i));
        ret = aclmdlGetInputDims(modelDesc_, i, &dimsInput);
        DEBUG_LOG("the dims of %zu input:", i);
        for (size_t j = 0; j < dimsInput.dimCount; j++) {
            cout << dimsInput.dims[j] << " ";
        }
        cout << endl;
        DEBUG_LOG("the name of %zu input: %s", i, aclmdlGetInputNameByIndex(modelDesc_, i));
        DEBUG_LOG("the Format of %zu input: %u", i, aclmdlGetInputFormat(modelDesc_, i));
        DEBUG_LOG("the DataType of %zu input: %u", i, aclmdlGetInputDataType(modelDesc_, i));
    }
    for (size_t i = 0; i < numOutputs; i++) {
        DEBUG_LOG("the size of %zu output: %zu", i, aclmdlGetOutputSizeByIndex(modelDesc_, i));
        ret = aclmdlGetOutputDims(modelDesc_, i, &dimsOutput);
        DEBUG_LOG("the dims of %zu output:", i);
        for (size_t j = 0; j < dimsOutput.dimCount; j++) {
            cout << dimsOutput.dims[j] << " ";
        }
        cout << endl;
        ret = aclmdlGetCurOutputDims(modelDesc_, i, &dimsCurrentOutput);
        DEBUG_LOG("the dims of %zu current output:", i);
        for (size_t j = 0; j < dimsCurrentOutput.dimCount; j++) {
            cout << dimsCurrentOutput.dims[j] << " ";
        }
        cout << endl;
        DEBUG_LOG("the name of %zu output: %s", i, aclmdlGetOutputNameByIndex(modelDesc_, i));
        DEBUG_LOG("the Format of %zu output: %u", i, aclmdlGetOutputFormat(modelDesc_, i));
        DEBUG_LOG("the DataType of %zu output: %u", i, aclmdlGetOutputDataType(modelDesc_, i));
    }
    aclmdlBatch batch_info;
    ret = aclmdlGetDynamicBatch(modelDesc_, &batch_info);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("get DynamicBatch failed");
        (void)aclmdlDestroyDesc(modelDesc_);
        modelDesc_ = nullptr;
        return FAILED;
    }
    if (batch_info.batchCount != 0) {
        DEBUG_LOG("DynamicBatch:");
        for (size_t i = 0; i < batch_info.batchCount; i++) {
            cout << batch_info.batch[i] << " ";
        }
        cout << endl;
    }
    aclmdlHW dynamicHW;
    ret = aclmdlGetDynamicHW(modelDesc_, -1, &dynamicHW);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("get DynamicHW failed");
        (void)aclmdlDestroyDesc(modelDesc_);
        modelDesc_ = nullptr;
        return FAILED;
    }
    if (dynamicHW.hwCount != 0) {
        DEBUG_LOG("DynamicHW:");
        for (size_t i = 0; i < dynamicHW.hwCount; i++) {
            cout << dynamicHW.hw[i][0] << dynamicHW.hw[i][1] << " ";
        }
        cout << endl;
    }
    DEBUG_LOG("end print model description");
    return SUCCESS;
}

void ModelProcess::DestroyDesc()
{
    if (modelDesc_ != nullptr) {
        (void)aclmdlDestroyDesc(modelDesc_);
        modelDesc_ = nullptr;
    }
}

Result ModelProcess::CreateDymInput(size_t index)
{
    if (input_ == nullptr) {
        input_ = aclmdlCreateDataset();
        if (input_ == nullptr) {
            ERROR_LOG("can't create dataset, create input failed");
            return FAILED;
        }
    } 
    size_t buffer_size = aclmdlGetInputSizeByIndex(modelDesc_, index);
    void* inBufferDev = nullptr;
    aclError ret = aclrtMalloc(&inBufferDev, buffer_size, ACL_MEM_MALLOC_NORMAL_ONLY);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("malloc device buffer failed. size is %zu", buffer_size);
        return FAILED;
    }
    aclDataBuffer* inputData = aclCreateDataBuffer(inBufferDev, buffer_size);
    if (inputData == nullptr) {
        ERROR_LOG("can't create data buffer, create input failed");
        aclrtFree(inBufferDev);
        inBufferDev = nullptr;
        return FAILED;
    }
    ret = aclmdlAddDatasetBuffer(input_, inputData);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("add input dataset buffer failed");
        aclrtFree(inBufferDev);
        inBufferDev = nullptr;
        aclDestroyDataBuffer(inputData);
        inputData = nullptr;
        return FAILED;
    }
    return SUCCESS;
}

Result ModelProcess::CreateInput(void* inputDataBuffer, size_t bufferSize)
{
    if (input_ == nullptr) {
        input_ = aclmdlCreateDataset();
        if (input_ == nullptr) {
            ERROR_LOG("can't create dataset, create input failed");
            return FAILED;
        }
    }

    aclDataBuffer* inputData = aclCreateDataBuffer(inputDataBuffer, bufferSize);
    if (inputData == nullptr) {
        ERROR_LOG("can't create data buffer, create input failed");
        return FAILED;
    }

    aclError ret = aclmdlAddDatasetBuffer(input_, inputData);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("add input dataset buffer failed");
        aclDestroyDataBuffer(inputData);
        inputData = nullptr;
        return FAILED;
    }
    return SUCCESS;
}

Result ModelProcess::CreateZeroInput()
{   
    if (input_ == nullptr) {
        input_ = aclmdlCreateDataset();
        if (input_ == nullptr) {
            ERROR_LOG("can't create dataset, create input failed");
            return FAILED;
        }
    }
    aclError ret;
    numInputs_ = aclmdlGetNumInputs(modelDesc_);
    for (size_t i = 0; i < numInputs_; i++) {

        const char *name = aclmdlGetInputNameByIndex(modelDesc_, i);
        if (name == nullptr) {
            ERROR_LOG("get input name failed, index = %zu.", i);
            return FAILED;
        }

        size_t buffer_size_zero = aclmdlGetInputSizeByIndex(modelDesc_, i);
        void* inBufferDev = nullptr;

        ret = aclrtMalloc(&inBufferDev, buffer_size_zero, ACL_MEM_MALLOC_NORMAL_ONLY);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("malloc device buffer failed. size is %zu", buffer_size_zero);
            return FAILED;
        }
        if (strcmp(name, ACL_DYNAMIC_TENSOR_NAME) != 0) {
            ret = aclrtMemset(inBufferDev, buffer_size_zero, 0, buffer_size_zero);
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("memory set failed");\
                aclrtFree(inBufferDev);
                inBufferDev = nullptr;
                return FAILED;
            }
        }

        aclDataBuffer* inputData = aclCreateDataBuffer(inBufferDev, buffer_size_zero);
        if (inputData == nullptr) {
            ERROR_LOG("can't create data buffer, create input failed");
            aclrtFree(inBufferDev);
            inBufferDev = nullptr;
            return FAILED;
        }
        ret = aclmdlAddDatasetBuffer(input_, inputData);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("add input dataset buffer failed");
            aclrtFree(inBufferDev);
            inBufferDev = nullptr;
            aclDestroyDataBuffer(inputData);
            inputData = nullptr;
            return FAILED;
        }
    }
    return SUCCESS;
}

void ModelProcess::DestroyInput()
{
    if (input_ == nullptr) {
        return;
    }

    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(input_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(input_, i);
        void* data = aclGetDataBufferAddr(dataBuffer);
        (void)aclrtFree(data);
        (void)aclDestroyDataBuffer(dataBuffer);
    }
    aclmdlDestroyDataset(input_);
    input_ = nullptr;
}

Result ModelProcess::CreateOutput()
{
    if (modelDesc_ == nullptr) {
        ERROR_LOG("no model description, create ouput failed");
        return FAILED;
    }

    output_ = aclmdlCreateDataset();
    if (output_ == nullptr) {
        ERROR_LOG("can't create dataset, create output failed");
        return FAILED;
    }

    size_t outputSize = aclmdlGetNumOutputs(modelDesc_);
    for (size_t i = 0; i < outputSize; ++i) {
        size_t buffer_size = aclmdlGetOutputSizeByIndex(modelDesc_, i);

        void* outputBuffer = nullptr;
        aclError ret = aclrtMalloc(&outputBuffer, buffer_size, ACL_MEM_MALLOC_NORMAL_ONLY);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("can't malloc buffer, size is %zu, create output failed", buffer_size);
            return FAILED;
        }

        aclDataBuffer* outputData = aclCreateDataBuffer(outputBuffer, buffer_size);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("can't create data buffer, create output failed");
            aclrtFree(outputBuffer);
            return FAILED;
        }

        ret = aclmdlAddDatasetBuffer(output_, outputData);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("can't add data buffer, create output failed");
            aclrtFree(outputBuffer);
            aclDestroyDataBuffer(outputData);
            return FAILED;
        }
    }

    INFO_LOG("create model output success");
    return SUCCESS;
}

void ModelProcess::OutputModelResult(std::string& s, std::string& modelName)
{

    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(output_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
        void* data = aclGetDataBufferAddr(dataBuffer);
        uint32_t len = aclGetDataBufferSize(dataBuffer);
        aclDataType datatype = aclmdlGetOutputDataType(modelDesc_, i);
        void* dims = nullptr;
        aclmdlIODims* dim = nullptr;
        aclError ret = ACL_ERROR_NONE;
        if (!g_is_device) {
            ret = aclrtMallocHost(&dims, sizeof(aclmdlIODims));
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("aclrtMallocHost failed, ret[%d]", ret);
                return;
            }
        } else {
            ret = aclrtMalloc(&dims, sizeof(aclmdlIODims), ACL_MEM_MALLOC_NORMAL_ONLY);
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("malloc device buffer failed, ret[%d]", ret);
                return;
            }
        }
        dim = reinterpret_cast<aclmdlIODims*>(dims);
        ret = aclmdlGetOutputDims(modelDesc_, i, dim);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("aclmdlGetOutputDims failed, ret[%d]", ret);
            return;
        }

        void* outHostData = NULL;
        ret = ACL_ERROR_NONE;
        void* outData = NULL;
        if (!g_is_device) {
            ret = aclrtMallocHost(&outHostData, len);
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("aclrtMallocHost failed, ret[%d]", ret);
                return;
            }

            ret = aclrtMemcpy(outHostData, len, data, len, ACL_MEMCPY_DEVICE_TO_HOST);
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("aclrtMemcpy failed, ret[%d]", ret);
                return;
            }
            switch (datatype) {
            case 0:
                outData = reinterpret_cast<float*>(outHostData);
                break;
            case 1:
                outData = reinterpret_cast<aclFloat16*>(outHostData);
                break;
            case 2:
                outData = reinterpret_cast<int8_t*>(outHostData);
                break;
            case 3:
                outData = reinterpret_cast<int*>(outHostData);
                break;
            case 4:
                outData = reinterpret_cast<uint8_t*>(outHostData);
                break;
            case 6:
                outData = reinterpret_cast<int16_t*>(outHostData);
                break;
            case 7:
                outData = reinterpret_cast<uint16_t*>(outHostData);
                break;
            case 8:
                outData = reinterpret_cast<uint32_t*>(outHostData);
                break;
            case 9:
                outData = reinterpret_cast<int64_t*>(outHostData);
                break;
            case 10:
                outData = reinterpret_cast<uint64_t*>(outHostData);
                break;
            case 11:
                outData = reinterpret_cast<double*>(outHostData);
                break;
            case 12:
                outData = reinterpret_cast<bool*>(outHostData);
                break;
            default:
                printf("undefined data type!\n");
                break;
            }

        } else {
            outData = reinterpret_cast<float*>(data);
        }
        if (g_is_txt) {
            ofstream outstr(s + "/" + modelName + "_output_" + to_string(i) + ".txt", ios::out);
            int amount_onebatch = 1;
            for (int j = 1; j < dim->dimCount; j++) {
                amount_onebatch *= dim->dims[j];
            }
            switch (datatype) {
            case 0:
                for (int i = 0; i < len / sizeof(float); i++) {
                    float out = *((float*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 1:
                for (int i = 0; i < len / sizeof(aclFloat16); i++) {
                    aclFloat16 out = *((aclFloat16*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 2:
                for (int i = 0; i < len / sizeof(int8_t); i++) {
                    int8_t out = *((int8_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 3:
                for (int i = 0; i < len / sizeof(int); i++) {
                    int out = *((int*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 4:
                for (int i = 0; i < len / sizeof(uint8_t); i++) {
                    uint8_t out = *((uint8_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 6:
                for (int i = 0; i < len / sizeof(int16_t); i++) {
                    int16_t out = *((int16_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 7:
                for (int i = 0; i < len / sizeof(uint16_t); i++) {
                    uint16_t out = *((uint16_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 8:
                for (int i = 0; i < len / sizeof(uint32_t); i++) {
                    uint32_t out = *((uint32_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 9:
                for (int i = 0; i < len / sizeof(int64_t); i++) {
                    int64_t out = *((int64_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 10:
                for (int i = 0; i < len / sizeof(uint64_t); i++) {
                    uint64_t out = *((uint64_t*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 11:
                for (int i = 0; i < len / sizeof(double); i++) {
                    double out = *((double*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            case 12:
                for (int i = 0; i < len / sizeof(bool); i++) {
                    int out = *((bool*)outData + i);
                    outstr << out << " ";
                    if (i != 0 && (i + 1) % amount_onebatch == 0 && i != len / sizeof(float)-1){
                        outstr << "\n\n";
                    } else{
                        if ((i + 1) % 100 == 0 && i != len / sizeof(float)-1){
                            outstr << "\n";
                        }
                    }
                }
                break;
            default:
                printf("undefined data type!\n");
                break;
            }
            outstr.close();
        } else {
            ofstream outstr(s + "/" + modelName + "_output_" + to_string(i) + ".bin", ios::out | ios::binary);

            outstr.write((char*)outData, len);
            outstr.close();
        }

        if (!g_is_device) {
            ret = aclrtFreeHost(outHostData);
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("aclrtFreeHost failed, ret[%d]", ret);
                return;
            }
        }
    }

    INFO_LOG("output data success");
    return;
}

void ModelProcess::DestroyOutput()
{
    if (output_ == nullptr) {
        return;
    }

    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(output_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
        void* data = aclGetDataBufferAddr(dataBuffer);
        (void)aclrtFree(data);
        (void)aclDestroyDataBuffer(dataBuffer);
    }

    (void)aclmdlDestroyDataset(output_);
    output_ = nullptr;
}

Result ModelProcess::Execute()
{
    aclError ret = aclmdlExecute(modelId_, input_, output_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("execute model failed, modelId is %u", modelId_);
        return FAILED;
    }

    INFO_LOG("model execute success");
    return SUCCESS;
}

void ModelProcess::Unload()
{
    if (!loadFlag_) {
        WARN_LOG("no model had been loaded, unload failed");
        return;
    }

    aclError ret = aclmdlUnload(modelId_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("unload model failed, modelId is %u", modelId_);
    }
    if (modelDesc_ != nullptr) {
        (void)aclmdlDestroyDesc(modelDesc_);
        modelDesc_ = nullptr;
    }
    loadFlag_ = false;
    INFO_LOG("unload model success, model Id is %u", modelId_);
}
