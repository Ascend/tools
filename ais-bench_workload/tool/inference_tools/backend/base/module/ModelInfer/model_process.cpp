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
bool g_is_device = true;
bool g_is_txt = false;
vector<int> g_output_size;

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
    DestroyInput(true);
    DestroyOutput(true);
}

Result ModelProcess::LoadModelFromFile(const string& modelPath)
{
    if (loadFlag_) {
        ERROR_LOG("has already loaded a model");
        return FAILED;
    }

    aclError ret = aclmdlLoadFromFile(modelPath.c_str(), &modelId_);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
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
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
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
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get input dynamic gear count failed %d", ret);
        return FAILED;
    }
    
    DEBUG_LOG("get input dynamic gear count success");

    return SUCCESS;
}

Result ModelProcess::GetDynamicIndex(size_t &dymindex)
{
    aclError ret; 

    const char *inputname = nullptr;
    bool dynamicIndex_exist = false;
    size_t numInputs = aclmdlGetNumInputs(modelDesc_);
    for (size_t i = 0; i < numInputs; i++) {
        inputname = aclmdlGetInputNameByIndex(modelDesc_, i);
        if (strcmp(inputname, ACL_DYNAMIC_TENSOR_NAME) == 0){
            dynamicIndex_exist = true;
        }
    }
    if (dynamicIndex_exist == false){
        g_dymindex = -1;
        return SUCCESS;
    }

    ret = aclmdlGetInputIndexByName(modelDesc_, ACL_DYNAMIC_TENSOR_NAME, &dymindex);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get input index by name failed %d", ret);
        g_dymindex = -1;
        return FAILED;
    }
    DEBUG_LOG("get input index by name success");
    g_dymindex = dymindex;
    return SUCCESS;
}

Result ModelProcess::CheckDynamicShape(std::vector<std::string> dym_shape_tmp, std::map<string, std::vector<int64_t>> &dym_shape_map, std::vector<int64_t> &dims_num)
{
    aclError ret; 
    const char *inputname = nullptr;
    vector<const char *> inputnames;
    string name;
    string shape_str;
    size_t numInputs = aclmdlGetNumInputs(modelDesc_);
    int64_t num_tmp = 0; 
    if (numInputs != dym_shape_tmp.size()){
        ERROR_LOG("om has %zu input, but dymShape parametet give %zu", numInputs, dym_shape_tmp.size());
        return FAILED;        
    }
    
    for (size_t i = 0; i < numInputs; i++) {
        inputname = aclmdlGetInputNameByIndex(modelDesc_, i);
        if (inputname == nullptr) {
            ERROR_LOG("get input name failed, index = %zu.", i);
            return FAILED;
        }    
        inputnames.push_back(inputname);    
    }
    for (size_t i = 0; i < dym_shape_tmp.size(); ++i){
        istringstream block(dym_shape_tmp[i]);
        string cell;
        size_t index = 0;
        vector<string> shape_tmp;
        while (getline(block, cell, ':')) {
            if (index == 0){
                name = cell;
            }
            else if (index == 1){
               shape_str = cell; 
            }
            index += 1;
        }
        Utils::SplitStringWithPunctuation(shape_str, shape_tmp, ',');
        size_t shape_tmp_size = shape_tmp.size();
        vector<int64_t> shape_array_tmp;
        
	    dims_num.push_back(shape_tmp_size);
        for(int index = 0; index < shape_tmp_size; ++index){
            num_tmp = atoi(shape_tmp[index].c_str());
            shape_array_tmp.push_back(num_tmp);  
        }
        dym_shape_map[name] = shape_array_tmp;     
    }
    for (size_t i = 0; i < inputnames.size(); ++i){
        if (dym_shape_map.count(inputnames[i]) <= 0){
            ERROR_LOG("the dymShape parameter set error, please check input name"); 
            return FAILED;       
        }
    }
    INFO_LOG("check Dynamic Shape success");
    return SUCCESS;

}

Result ModelProcess::SetDynamicShape(std::map<std::string, std::vector<int64_t>> dym_shape_map, std::vector<int64_t> &dims_num)
{
    aclError ret;
    const char *name;
    int input_num = dym_shape_map.size();
    aclTensorDesc * inputDesc;
    for (size_t i = 0; i < input_num; i++) {
        name = aclmdlGetInputNameByIndex(modelDesc_, i);
        int64_t arr[dym_shape_map[name].size()];
        std::copy(dym_shape_map[name].begin(), dym_shape_map[name].end(), arr);
	    inputDesc = aclCreateTensorDesc(ACL_FLOAT, dims_num[i], arr, ACL_FORMAT_NCHW);
        ret = aclmdlSetDatasetTensorDesc(input_, inputDesc, i);
        if (ret != ACL_SUCCESS) {
            cout << aclGetRecentErrMsg() << endl;
            ERROR_LOG("aclmdlSetDatasetTensorDesc failed %d", ret);
            return FAILED;
        }
    }
    DEBUG_LOG("set Dynamic shape success");
	return SUCCESS;	
}

Result ModelProcess::GetMaxDynamicHWSize(uint64_t &outsize)
{
    aclError ret;
    aclmdlHW dynamicHW;
    uint64_t maxDynamicHWSize = 0;
    ret = aclmdlGetDynamicHW(modelDesc_, -1, &dynamicHW);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get DynamicHW failed");
        return FAILED;
    }

    if (dynamicHW.hwCount <= 0) {
        ERROR_LOG("the dynamic_image_size parameter is not specified for model conversion");
        return FAILED;
    }
    for (size_t i = 0; i < dynamicHW.hwCount; i++) {
        if (maxDynamicHWSize < (dynamicHW.hw[i][0] * dynamicHW.hw[i][1])) {
            maxDynamicHWSize = dynamicHW.hw[i][0] * dynamicHW.hw[i][1];
        }
    }
    outsize = maxDynamicHWSize;
    return SUCCESS;
}

Result ModelProcess::CheckDynamicHWSize(pair<int, int> dynamicPair, bool &is_dymHW)
{
    aclmdlHW dynamicHW;
    aclError ret;
    bool if_same = false;
    ret = aclmdlGetDynamicHW(modelDesc_, -1, &dynamicHW);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get DynamicHW failed");
        return FAILED;
    }
    if (dynamicHW.hwCount > 0) {
        stringstream dynamicRange;
        for (size_t i = 0; i < dynamicHW.hwCount; i++) {
            if (dynamicPair.first == dynamicHW.hw[i][0] and dynamicPair.second == dynamicHW.hw[i][1]) {
                if_same = true;
                break;
            }
        }
        if (! if_same){
            ERROR_LOG("the dymHW parameter is not correct");
            return FAILED;                  
        }
        is_dymHW = true;
 
    }
    else{
        ERROR_LOG("the dynamic_image_size parameter is not specified for model conversion");
        return FAILED;       
    } 
    INFO_LOG("check dynamic image size success.");
    return SUCCESS;
}

Result ModelProcess::SetDynamicHW(std::pair<uint64_t , uint64_t > dynamicPair)
{
    aclError ret;
    ret = aclmdlSetDynamicHWSize(modelId_, input_, g_dymindex, dynamicPair.first, dynamicPair.second);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("aclmdlSetDynamicHWSize failed %d", ret);
        return FAILED;
    }
    DEBUG_LOG("set Dynamic HW success");
    return SUCCESS;
}

Result ModelProcess::CheckDynamicBatchSize(uint64_t dymbatch, bool &is_dymbatch)
{
    aclmdlBatch batch_info;
    aclError ret; 
    bool if_same = false;
    ret = aclmdlGetDynamicBatch(modelDesc_, &batch_info);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get DynamicBatch failed");
        return FAILED;
    }
    if (batch_info.batchCount > 0) {
        for (size_t i = 0; i < batch_info.batchCount; i++) {
            if (dymbatch == batch_info.batch[i]){
                if_same = true;
                break;
            }
        }
        if (! if_same){
            ERROR_LOG("the dymBatch parameter is not correct");
            GetDymBatchInfo();
            return FAILED;                  
        }
        is_dymbatch = true;
    }
    else{
        ERROR_LOG("the dynamic_batch_size parameter is not specified for model conversion");
        return FAILED;       
    }  
    INFO_LOG("check dynamic batch success");
    return SUCCESS;
}

Result ModelProcess::SetDynamicBatchSize(uint64_t batchSize)
{
    aclError ret = aclmdlSetDynamicBatchSize(modelId_, input_, g_dymindex, batchSize);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("aclmdlSetDynamicBatchSize failed %d", ret);
        return FAILED;
    }
    DEBUG_LOG("set dynamic batch size success");
    return SUCCESS; 
}

Result ModelProcess::GetMaxBatchSize(uint64_t &maxBatchSize)
{
    aclmdlBatch batch_info;
    aclError ret; 
    ret = aclmdlGetDynamicBatch(modelDesc_, &batch_info);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get DynamicBatch failed");
        return FAILED;
    }
    if (batch_info.batchCount > 0) {
        for (size_t i = 0; i < batch_info.batchCount; i++) {
            if (maxBatchSize < batch_info.batch[i]){
                maxBatchSize = batch_info.batch[i];
            }
        }
    }
    DEBUG_LOG("get max dynamic batch size success");
    return SUCCESS;
}

Result ModelProcess::GetCurOutputDimsMul(size_t index, vector<int64_t>& curOutputDimsMul)
{
    aclError ret; 
    aclmdlIODims ioDims;
    int64_t tmp_dim = 1;
    ret = aclmdlGetCurOutputDims(modelDesc_, index, &ioDims);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        WARN_LOG("aclmdlGetCurOutputDims failed ret[%d], maybe the modle has dynamic shape", ret);
        return FAILED;
    }
    for (int i = 1; i < ioDims.dimCount; i++) {
        tmp_dim *= ioDims.dims[ioDims.dimCount - i];
        curOutputDimsMul.push_back(tmp_dim);
    }
    return SUCCESS;
}


Result ModelProcess::CheckDynamicDims(vector<string> dym_dims, size_t gearCount, aclmdlIODims *dims)
{
    aclmdlGetInputDynamicDims(modelDesc_, -1, dims, gearCount);
    bool if_same = false;
    for (size_t i = 0; i < gearCount; i++)
    {
        if ((size_t)dym_dims.size() != dims[i].dimCount){
            ERROR_LOG("the dymDims parameter is not correct i:%d dysize:%d dimcount:%d", i, dym_dims.size(), dims[i].dimCount);
            GetDimInfo(gearCount, dims);
            return FAILED;
        }
        for (size_t j = 0; j < dims[i].dimCount; j++)
        {   
            if (dims[i].dims[j] != atoi(dym_dims[j].c_str()))
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

Result ModelProcess::SetDynamicDims(vector<string> dym_dims)
{   
    aclmdlIODims dims;
    dims.dimCount = dym_dims.size();
    for (size_t i = 0; i < dims.dimCount; i++)
    {   
        dims.dims[i] = atoi(dym_dims[i].c_str());
    }

    aclError ret = aclmdlSetInputDynamicDims(modelId_, input_, g_dymindex, &dims);
 
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("aclmdlSetInputDynamicDims failed %d", ret);
        return FAILED;
    }
    DEBUG_LOG("set dynamic dims success");
    return SUCCESS; 
}

void ModelProcess::GetDymBatchInfo(){
    aclmdlBatch batch_info;
    aclmdlGetDynamicBatch(modelDesc_, &batch_info);
    stringstream ss;
    ss << "model has dynamic batch size:{";
    for (size_t i = 0; i < batch_info.batchCount; i++) {
        ss << "[" << batch_info.batch[i] << "]";  
    }
    ss << "}, please set correct dynamic batch size";
    ERROR_LOG("%s", ss.str().c_str());    
}

void ModelProcess::GetDymHWInfo(){
    aclmdlHW  hw_info;
    aclmdlGetDynamicHW(modelDesc_, -1, &hw_info);
    stringstream ss;
    
    ERROR_LOG("model has %zu gear of HW", hw_info.hwCount);
    for (size_t i = 0; i < hw_info.hwCount; i++) {
        ss << "[" << hw_info.hw[i] << "]";  
    }
    ss << "}, please set correct dynamic batch size";
    ERROR_LOG("%s", ss.str().c_str());    
}

void ModelProcess::GetDimInfo(size_t gearCount, aclmdlIODims *dims)
{
    aclmdlGetInputDynamicDims(modelDesc_, -1, dims, gearCount);

    for (size_t i = 0; i < gearCount; i++)
    {
        if (i == 0)
        {
            ERROR_LOG("model has %zu gear of dims", gearCount); 
        }
        stringstream ss;
        ss << "dims[" << i << "]:";
        for (size_t j = 0; j < dims[i].dimCount; j++)
        {
            ss << "[" << dims[i].dims[j] << "]";  
        }
        ERROR_LOG("%s", ss.str().c_str()); 
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

        DEBUG_LOG("the name of %zu output: %s", i, aclmdlGetOutputNameByIndex(modelDesc_, i));
        DEBUG_LOG("the Format of %zu output: %u", i, aclmdlGetOutputFormat(modelDesc_, i));
        DEBUG_LOG("the DataType of %zu output: %u", i, aclmdlGetOutputDataType(modelDesc_, i));
    }
    aclmdlBatch batch_info;
    ret = aclmdlGetDynamicBatch(modelDesc_, &batch_info);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("get DynamicBatch failed");
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
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        modelDesc_ = nullptr;
        return FAILED;
    }
    if (dynamicHW.hwCount != 0) {
        DEBUG_LOG("DynamicHW:");
        for (size_t i = 0; i < dynamicHW.hwCount; i++) {
            cout << dynamicHW.hw[i][0] << "," <<dynamicHW.hw[i][1] << " ";
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
    aclError ret = aclrtMalloc(&inBufferDev, buffer_size, ACL_MEM_MALLOC_HUGE_FIRST);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
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
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
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
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
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

        ret = aclrtMalloc(&inBufferDev, buffer_size_zero, ACL_MEM_MALLOC_HUGE_FIRST);
        if (ret != ACL_SUCCESS) {
            cout << aclGetRecentErrMsg() << endl;
            ERROR_LOG("malloc device buffer failed. size is %zu", buffer_size_zero);
            return FAILED;
        }
        if (strcmp(name, ACL_DYNAMIC_TENSOR_NAME) != 0) {
            ret = aclrtMemset(inBufferDev, buffer_size_zero, 0, buffer_size_zero);
            if (ret != ACL_SUCCESS) {
                cout << aclGetRecentErrMsg() << endl;
                ERROR_LOG("memory set failed");
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
        if (ret != ACL_SUCCESS) {
            cout << aclGetRecentErrMsg() << endl;
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

void ModelProcess::DestroyInput(bool free_memory_flag=true)
{
    if (input_ == nullptr) {
        return;
    }

    size_t bufNum = aclmdlGetDatasetNumBuffers(input_);
    for (size_t i = 0; i < bufNum; ++i) {
        aclDataBuffer *dataBuffer = aclmdlGetDatasetBuffer(input_, i);
        if (dataBuffer == nullptr){
            continue;
        }
        void *data = aclGetDataBufferAddr(dataBuffer);
        if (data == nullptr){
            (void)aclDestroyDataBuffer(dataBuffer);
            continue;
        }
        if (free_memory_flag == true){
            (void)aclrtFree(data);
            data = nullptr;
        }
        (void)aclDestroyDataBuffer(dataBuffer);
        dataBuffer = nullptr;
    }
    (void)aclmdlDestroyDataset(input_);
    input_ = nullptr;
    DEBUG_LOG("destroy model input success");
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

    size_t outputNum = aclmdlGetNumOutputs(modelDesc_);

    if ((g_output_size.empty() == false)  && (outputNum != g_output_size.size())){
        ERROR_LOG("om has %zu output, but outputSize parametet give %zu", outputNum, g_output_size.size());
        return FAILED;   
    }

    for (size_t i = 0; i < outputNum; ++i) {
        size_t buffer_size = 0;
        if (g_output_size.empty() == false){
            buffer_size = g_output_size[i];
        }
        else{
            buffer_size = aclmdlGetOutputSizeByIndex(modelDesc_, i);
        }
        void* outputBuffer = nullptr;
        aclError ret = aclrtMalloc(&outputBuffer, buffer_size, ACL_MEM_MALLOC_HUGE_FIRST);
        if (ret != ACL_SUCCESS) {
            cout << aclGetRecentErrMsg() << endl;
            ERROR_LOG("can't malloc buffer, size is %zu, create output failed", buffer_size);
            return FAILED;
        }

        aclDataBuffer* outputData = aclCreateDataBuffer(outputBuffer, buffer_size);
        if (outputData == nullptr) {
            cout << aclGetRecentErrMsg() << endl;
            ERROR_LOG("can't create data buffer, create output failed");
            aclrtFree(outputBuffer);
            return FAILED;
        }

        ret = aclmdlAddDatasetBuffer(output_, outputData);
        if (ret != ACL_SUCCESS) {
            cout << aclGetRecentErrMsg() << endl;
            ERROR_LOG("can't add data buffer, create output failed");
            aclrtFree(outputBuffer);
            aclDestroyDataBuffer(outputData);
            return FAILED;
        }
    }

    INFO_LOG("create model output success");
    return SUCCESS;
}

// void ModelProcess::OutbufTofile()
// {
//     void* data = nullptr;
//     size_t len = 0;
//     aclError ret = ACL_SUCCESS;
//     void* outHostData = nullptr;
//     for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(output_); ++i) {
//         aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
//         data = aclGetDataBufferAddr(dataBuffer);
// 	    len = aclGetDataBufferSizeV2(dataBuffer);

//         ret = aclrtMallocHost(&outHostData, len);
//         ret = aclrtMemcpy(outHostData, len, data, len, ACL_MEMCPY_DEVICE_TO_HOST);
//         ofstream outstr("./lcmdebugmsame_output_" + to_string(i) + ".bin", ios::out | ios::binary);
//         printf("lcm debug outto buf i:%d\n");
//         outstr.write((char*)outHostData, len);
//         outstr.close();
//         ret = aclrtFreeHost(outHostData);
//     }
// }

void ModelProcess::OutputModelResult(std::string& s, std::string& modelName, std::uint64_t dymbatch_size, bool is_dymshape)
{
    void* data = nullptr;
    void* outHostData = nullptr;
    void* outData = nullptr;
    aclError ret = ACL_SUCCESS;    
    uint64_t maxBatchSize = 0;
    size_t len = 0;
    ret = GetMaxBatchSize(maxBatchSize);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("aclrtMallocHost failed, ret[%d]", ret);
        return;
    }   
    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(output_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
        data = aclGetDataBufferAddr(dataBuffer);
        if (is_dymshape){
	    aclTensorDesc *outputDesc = aclmdlGetDatasetTensorDesc(output_, i);
	    len = aclGetTensorDescSize(outputDesc);
	}
        else
	{
	    len = aclGetDataBufferSizeV2(dataBuffer);
            if (dymbatch_size > 0 && maxBatchSize > 0){
                len = len / (maxBatchSize / dymbatch_size);
            }
	}
        aclDataType datatype = aclmdlGetOutputDataType(modelDesc_, i);
        if (!g_is_device) {
            ret = aclrtMallocHost(&outHostData, len);
            if (ret != ACL_SUCCESS) {
                cout << aclGetRecentErrMsg() << endl;
                ERROR_LOG("aclrtMallocHost failed, ret[%d]", ret);
                return;
            }
            ret = aclrtMemcpy(outHostData, len, data, len, ACL_MEMCPY_DEVICE_TO_HOST);
            if (ret != ACL_SUCCESS) {
                cout << aclGetRecentErrMsg() << endl;
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
            vector<int64_t> curOutputDimsMul;
            ret = GetCurOutputDimsMul(i, curOutputDimsMul);
            ofstream outstr(s + "/" + modelName + "_output_" + to_string(i) + ".txt", ios::out);
            switch (datatype) {
            case 0:
                for (int64_t i = 1; i <= len / sizeof(float); i++) {
                    float out = *((float*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    }                    
                }
                break;
            case 1:{
                aclFloat16 * out_fp16 = reinterpret_cast<aclFloat16*>(outData);
                float out = 0;
                for (int i = 1; i <= len / sizeof(aclFloat16); i++) {
                    out = aclFloat16ToFloat(out_fp16[i-1]);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    }                   
                }
                break;
            }
            case 2:
                for (int i = 1; i <= len / sizeof(int8_t); i++) {
                    int8_t out = *((int8_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 3:
                for (int i = 1; i <= len / sizeof(int); i++) {
                    int out = *((int*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    }
                }
                break;
            case 4:
                for (int i = 1; i <= len / sizeof(uint8_t); i++) {
                    uint8_t out = *((uint8_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    }
                }
                break;
            case 6:
                for (int i = 1; i <= len / sizeof(int16_t); i++) {
                    int16_t out = *((int16_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 7:
                for (int i = 1; i <= len / sizeof(uint16_t); i++) {
                    uint16_t out = *((uint16_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 8:
                for (int i = 1; i <= len / sizeof(uint32_t); i++) {
                    uint32_t out = *((uint32_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 9:
                for (int i = 1; i <= len / sizeof(int64_t); i++) {
                    int64_t out = *((int64_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 10:
                for (int i = 1; i <= len / sizeof(uint64_t); i++) {
                    uint64_t out = *((uint64_t*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 11:
                for (int i = 1; i <= len / sizeof(double); i++) {
                    double out = *((double*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
                        } 
                    } 
                }
                break;
            case 12:
                for (int i = 1; i <= len / sizeof(bool); i++) {
                    int out = *((bool*)outData + i - 1);
                    outstr << out << " ";
                    vector<int64_t>::iterator it;
                    for(it = curOutputDimsMul.begin(); it != curOutputDimsMul.end(); it++){
                        if ((i != 0) && (i % *it == 0)){
                            outstr << "\n";
                            break;
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
            if (ret != ACL_SUCCESS) {
                cout << aclGetRecentErrMsg() << endl;
                ERROR_LOG("aclrtFreeHost failed, ret[%d]", ret);
                return;
            }
        }
    }

    INFO_LOG("output data success");
    return;
}

void ModelProcess::DestroyOutput(bool free_memory_flag=true)
{
    if (output_ == nullptr) {
        return;
    }

    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(output_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
        void* data = aclGetDataBufferAddr(dataBuffer);
        if (free_memory_flag == true){
            (void)aclrtFree(data);
        }
        (void)aclDestroyDataBuffer(dataBuffer);
    }

    (void)aclmdlDestroyDataset(output_);
    output_ = nullptr;
}

Result ModelProcess::Execute()
{
    aclError ret = aclmdlExecute(modelId_, input_, output_);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("execute model failed, modelId is %u", modelId_);
        return FAILED;
    }

    DEBUG_LOG("model execute success");
    return SUCCESS;
}

void ModelProcess::Unload()
{
    if (!loadFlag_) {
        WARN_LOG("no model had been loaded, unload failed");
        return;
    }

    aclError ret = aclmdlUnload(modelId_);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("unload model failed, modelId is %u", modelId_);
    }
    if (modelDesc_ != nullptr) {
        (void)aclmdlDestroyDesc(modelDesc_);
        modelDesc_ = nullptr;
    }
    loadFlag_ = false;
    INFO_LOG("unload model success, model Id is %u", modelId_);
}

Result ModelProcess::GetCurOutputShape(size_t index, std::vector<int64_t>& shape)
{
    aclError ret; 
    aclmdlIODims ioDims;
    int64_t tmp_dim = 1;
    // 对于动态shape场景，通过该接口获取不到输出shape
    ret = aclmdlGetCurOutputDims(modelDesc_, index, &ioDims);
    if (ret != ACL_SUCCESS) {
        // cout << aclGetRecentErrMsg() << endl;
        DEBUG_LOG("aclmdlGetCurOutputDims get not success, maybe the modle has dynamic shape", ret);
        return FAILED;
    }
    for (int i = 0; i < ioDims.dimCount; i++) {
        shape.push_back(ioDims.dims[i]);
    }
    return SUCCESS;
}

size_t ModelProcess::GetNumInputs()
{
    return aclmdlGetNumInputs(modelDesc_);
}

size_t ModelProcess::GetNumOutputs()
{
    return aclmdlGetNumOutputs(modelDesc_);
}

Result ModelProcess::GetInTensorDesc(size_t i, std::string& name, int& datatype, size_t& format, std::vector<int64_t>& shape, size_t& size)
{
    name = aclmdlGetInputNameByIndex(modelDesc_, i);
    datatype = aclmdlGetInputDataType(modelDesc_, i);
    format = aclmdlGetInputFormat(modelDesc_, i);
    size = aclmdlGetInputSizeByIndex(modelDesc_, i);

    aclmdlIODims dimsInput;
    aclmdlGetInputDims(modelDesc_, i, &dimsInput);

    shape.clear();
    for (size_t j = 0; j < dimsInput.dimCount; j++) {
        shape.push_back(dimsInput.dims[j]);
    }
    return SUCCESS;
}

Result ModelProcess::GetOutTensorDesc(size_t i, std::string& name, int& datatype, size_t& format, std::vector<int64_t>& shape, size_t& size)
{
    name = aclmdlGetOutputNameByIndex(modelDesc_, i);
    datatype = aclmdlGetOutputDataType(modelDesc_, i);
    format = aclmdlGetOutputFormat(modelDesc_, i);
    size = aclmdlGetOutputSizeByIndex(modelDesc_, i);

    aclmdlIODims dimsOutput;
    aclmdlGetOutputDims(modelDesc_, i, &dimsOutput);

    shape.clear();
    for (size_t j = 0; j < dimsOutput.dimCount; j++) {
        shape.push_back(dimsOutput.dims[j]);
    }
    return SUCCESS;
}

int ModelProcess::GetOutTensorLen(size_t i, bool is_dymshape, float sizeRatio)
{
    aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
    uint64_t maxBatchSize = 0;
    aclError ret = ACL_SUCCESS;
    size_t len;
    ret = GetMaxBatchSize(maxBatchSize);
    if (is_dymshape){
	    aclTensorDesc *outputDesc = aclmdlGetDatasetTensorDesc(output_, i);
	    len = aclGetTensorDescSize(outputDesc);
	}
    else{
	    len = aclGetDataBufferSizeV2(dataBuffer);
        len = len / sizeRatio;
	}
    return len;
}

Result ModelProcess::CreateOutput(void* outputBuffer, size_t bufferSize)
{
    if (output_ == nullptr) {
        output_ = aclmdlCreateDataset();
        if (output_ == nullptr) {
            ERROR_LOG("can't create dataset, create output failed");
            return FAILED;
        }
    }

    aclDataBuffer* outputData = aclCreateDataBuffer(outputBuffer, bufferSize);
    if (outputData == nullptr) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("can't create data buffer, create output failed");
        aclrtFree(outputBuffer);
        return FAILED;
    }

    aclError ret = aclmdlAddDatasetBuffer(output_, outputData);
    if (ret != ACL_SUCCESS) {
        cout << aclGetRecentErrMsg() << endl;
        ERROR_LOG("add input dataset buffer failed");
        aclDestroyDataBuffer(outputData);
        outputData = nullptr;
        return FAILED;
    }
    return SUCCESS;
}
