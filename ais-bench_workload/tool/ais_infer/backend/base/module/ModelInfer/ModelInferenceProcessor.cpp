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

#include "Base/ModelInfer/ModelInferenceProcessor.h"
#include "acl/acl.h"
#include "Base/Log/Log.h"

namespace Base {

APP_ERROR ModelInferenceProcessor::GetModelDescInfo()
{
    TensorDesc info;
    int datatype;
    // create in tensos desc info
    size_t numInputs = processModel.GetNumInputs();
    modelDesc_.inTensorsDesc.clear();
    modelDesc_.inTensorsDesc.reserve(numInputs);
    int index = 0;
    for (size_t i = 0; i < numInputs; i++) {
        // dynamicindex not as intensors, it is args info
        if (i == dynamicIndex_){
            continue;
        }
        CHECK_RET_EQ(processModel.GetInTensorDesc(i, info.name, datatype, info.format, info.shape, info.size), SUCCESS);
        info.realsize = info.size;
        info.datatype = (TensorDataType)datatype;
        modelDesc_.inTensorsDesc.push_back(info);
        modelDesc_.innames2Index[info.name] = index;
        index++;
    }

    // create out tensos info
    size_t numOutputs = processModel.GetNumOutputs();
    modelDesc_.outTensorsDesc.clear();
    modelDesc_.outTensorsDesc.reserve(numOutputs);
    for (size_t i = 0; i < numOutputs; i++) {
        CHECK_RET_EQ(processModel.GetOutTensorDesc(i, info.name, datatype, info.format, info.shape, info.size), SUCCESS);
        info.realsize = info.size;
        info.datatype = (TensorDataType)datatype;
        modelDesc_.outTensorsDesc.push_back(info);
        modelDesc_.outnames2Index[info.name] = i;
    }

    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::Init(const std::string& modelPath, std::shared_ptr<SessionOptions> options, const int32_t &deviceId)
{
    options_ = options;
    deviceId_ = deviceId;

    SETLOGLEVEL(options_->log_level);

    // initResource 
    CHECK_RET_EQ(processModel.LoadModelFromFile(modelPath), SUCCESS);

    CHECK_RET_EQ(processModel.CreateDesc(), SUCCESS);

    CHECK_RET_EQ(processModel.GetDynamicGearCount(dym_gear_count_), SUCCESS);

    processModel.GetDynamicIndex(dynamicIndex_);

    CHECK_RET_EQ(GetModelDescInfo(), APP_ERR_OK);

    CHECK_RET_EQ(AllocDyIndexMem(), APP_ERR_OK);

    if (options_->log_level == LOG_DEBUG_LEVEL){
        processModel.PrintDesc();
    }

    return APP_ERR_OK;
}

/*
 * @description Unload Model
 * @return APP_ERROR error code
 */
APP_ERROR ModelInferenceProcessor::DeInit(void)
{
    FreeDyIndexMem();
    FreeDymInfoMem();
    DestroyInferCacheData();
    return APP_ERR_OK;
}

const std::vector<Base::TensorDesc>& ModelInferenceProcessor::GetInputs() const
{
    return modelDesc_.inTensorsDesc;
}

const std::vector<Base::TensorDesc>& ModelInferenceProcessor::GetOutputs() const
{
    return modelDesc_.outTensorsDesc;
}

std::shared_ptr<SessionOptions> ModelInferenceProcessor::GetOptions()
{
    return options_;
}

APP_ERROR ModelInferenceProcessor::DestroyOutMemoryData(std::vector<MemoryData>& outputs)
{
    for (size_t i = 0; i < outputs.size(); ++i) {
        if (outputs[i].ptrData != nullptr){
            outputs[i].free(outputs[i].ptrData);
        }
    }
    outputs.clear();
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::CreateOutMemoryData(std::vector<MemoryData>& outputs)
{
    int size;
    int customIndex = 0;
    for (size_t i = 0; i < modelDesc_.outTensorsDesc.size(); ++i) {
        size = modelDesc_.outTensorsDesc[i].size;
        if (size == 0 && customIndex < customOutTensorSize_.size()){
            size = customOutTensorSize_[customIndex++];
        }
        if (size == 0){
            ERROR_LOG("out i:%d size is zero custom:%d %d\n", size, customIndex, customOutTensorSize_.size());
            return APP_ERR_ACL_FAILURE;
        }
        DEBUG_LOG("Create OutMemory i:%d name:%s size:%d\n", i, modelDesc_.outTensorsDesc[i].name.c_str(), size);
        Base::MemoryData memorydata(size, MemoryData::MemoryType::MEMORY_DEVICE, deviceId_);
        auto ret = MemoryHelper::MxbsMalloc(memorydata);
        if (ret != APP_ERR_OK) {
            ERROR_LOG("MemoryHelper::MxbsMalloc failed.i:%d name:%s size:%d ret:%d", \
                    i, modelDesc_.outTensorsDesc[i].name.c_str(), size, ret);
            return ret;
        }
        outputs.push_back(std::move(memorydata));
    }

    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::AddOutTensors(std::vector<MemoryData>& outputs, std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors)
{
    bool is_dymshape = (dynamicInfo_.dynamicType == DYNAMIC_SHAPE ? true : false);
    uint64_t dymbatch_size = (dynamicInfo_.dynamicType == DYNAMIC_BATCH ? dynamicInfo_.dyBatch.batchSize : 0);
    int realLen;
    // 获取输出tensor实际size 对于动态分档场景 需要获取size的实际大小。根据第一个入参的size/realsize比值获取
    // 对于动态shape模型 可以直接获取len
    float sizeRatio = (float)modelDesc_.inTensorsDesc[0].size / modelDesc_.inTensorsDesc[0].realsize;
    for (const auto& name : outputNames) {
        auto index = modelDesc_.outnames2Index[name];

        std::vector<int64_t> i64shape;
        std::vector<uint32_t> u32shape;
        realLen = processModel.GetOutTensorLen(index, is_dymshape, sizeRatio);
        if (processModel.GetCurOutputShape(index, i64shape) != SUCCESS){
            // 针对于动态shape场景 无法获取真实的输出shape 先填写一个一维的值 以便后续内存可以导出
            i64shape.push_back(realLen / aclDataTypeSize(static_cast<aclDataType>(modelDesc_.outTensorsDesc[index].datatype)));
        }
        DEBUG_LOG("AddOutTensors name:%s index:%d ratio:%f len:%d outdescsize:%d shapesize:%d\n",
            name.c_str(), index, sizeRatio, realLen, modelDesc_.outTensorsDesc[index].size, i64shape.size());
        outputs[index].size = realLen;
        bool isBorrowed = false;
        for (size_t j = 0; j < i64shape.size(); ++j) {
            u32shape.push_back((uint32_t)(i64shape[j]));
        }
        TensorBase outputTensor(outputs[index], isBorrowed, u32shape, modelDesc_.outTensorsDesc[index].datatype);
        outputTensors.push_back(outputTensor);
        // mem control by outTensors so outputs mems nullptr
        outputs[index].ptrData = nullptr;
    }

    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::CheckInMapAndFillBaseTensor(const std::map<std::string, TensorBase>& feeds, std::vector<BaseTensor> &inputs)
{
    if (feeds.size() != modelDesc_.inTensorsDesc.size()){
        ERROR_LOG("intensors size:%d need size:%d not match\n", feeds.size(), modelDesc_.inTensorsDesc.size());
        return APP_ERR_ACL_FAILURE;
    }

    for (size_t i = 0; i < modelDesc_.inTensorsDesc.size(); ++i) {
        auto iter = feeds.find(modelDesc_.inTensorsDesc[i].name);
        if (feeds.end() == iter) {
            ERROR_LOG("intensors i:%lld name:%s not find\n", i, modelDesc_.inTensorsDesc[i].name);
            return APP_ERR_ACL_FAILURE;
        }

        BaseTensor baseTensor = {};
        baseTensor.buf = iter->second.GetBuffer();
        baseTensor.size = iter->second.GetByteSize();
        if (baseTensor.size != modelDesc_.inTensorsDesc[i].realsize){
            ERROR_LOG("Check i:%d name:%s in size:%d needsize:%d not match\n",
                i, modelDesc_.inTensorsDesc[i].name.c_str(), baseTensor.size, modelDesc_.inTensorsDesc[i].realsize);
            return APP_ERR_ACL_FAILURE;
        }
        inputs.push_back(std::move(baseTensor));
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::Inference(const std::map<std::string, TensorBase>& feeds, std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors)
{
    APP_ERROR ret;

    // create basetensors
    std::vector<BaseTensor> inputs;
    ret = CheckInMapAndFillBaseTensor(feeds, inputs);
    if (ret != APP_ERR_OK){
        ERROR_LOG("Check InVector failed ret:%d\n", ret);
        return ret;
    }
    ret = ModelInference_Inner(inputs, outputNames, outputTensors);
    return ret;
}

APP_ERROR ModelInferenceProcessor::CheckInVectorAndFillBaseTensor(const std::vector<TensorBase>& feeds,
        std::vector<BaseTensor> &inputs)
{
    for (size_t i = 0; i < feeds.size(); ++i) {
        BaseTensor baseTensor = {};
        baseTensor.buf = feeds[i].GetBuffer();
        baseTensor.size = feeds[i].GetByteSize();
        if (baseTensor.size != modelDesc_.inTensorsDesc[i].realsize){
            ERROR_LOG("Check i:%d name:%s in size:%d needsize:%d not match\n",
                i, modelDesc_.inTensorsDesc[i].name.c_str(), baseTensor.size, modelDesc_.inTensorsDesc[i].realsize);
            return APP_ERR_ACL_FAILURE;
        }
        inputs.push_back(std::move(baseTensor));
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::Inference(const std::vector<TensorBase>& feeds,
    std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors)
{
    APP_ERROR ret;
    // create basetensors
    std::vector<BaseTensor> inputs;
    ret = CheckInVectorAndFillBaseTensor(feeds, inputs);
    if (ret != APP_ERR_OK){
        ERROR_LOG("Check InVector failed ret:%d\n", ret);
        return ret;
    }
    ret = ModelInference_Inner(inputs, outputNames, outputTensors);
    return ret;
}

APP_ERROR ModelInferenceProcessor::DestroyInferCacheData()
{
    DestroyOutMemoryData(outputsMemDataQue_);
    processModel.DestroyInput(false);
    processModel.DestroyOutput(false);
    return APP_ERR_OK;
}

// step inference one:set inputs
APP_ERROR ModelInferenceProcessor::Inference_SetInputs(const std::map<std::string, TensorBase>& feeds)
{
    // create basetensors
    std::vector<BaseTensor> inputs;
    APP_ERROR ret = CheckInMapAndFillBaseTensor(feeds, inputs);
    if (ret != APP_ERR_OK){
        ERROR_LOG("Check InVector failed ret:%d\n", ret);
        return ret;
    }
    ret = SetInputsData(inputs);
    if (ret != APP_ERR_OK){
        ERROR_LOG("Set InputsData failed ret:%d\n", ret);
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::Inference_SetInputs(const std::vector<TensorBase>& feeds)
{
    // create basetensors
    std::vector<BaseTensor> inputs;
    APP_ERROR ret = CheckInVectorAndFillBaseTensor(feeds, inputs);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("Check InVector failed ret:%d\n", ret);
        return ret;
    }

    ret = SetInputsData(inputs);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("Set InputsData failed ret:%d\n", ret);
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetInputsData(std::vector<BaseTensor> &inputs)
{
    APP_ERROR ret;

    DestroyInferCacheData();

    if (inputs.size() != modelDesc_.inTensorsDesc.size()){
        WARN_LOG("intensors in:%d need:%d not match\n", inputs.size(), modelDesc_.inTensorsDesc.size());
        return APP_ERR_ACL_FAILURE;
    }

    if (dynamicInfo_.dynamicType != DYNAMIC_DIMS && dym_gear_count_ > 0){
        WARN_LOG("check failed dym gearcount:%d but dymtype:%d not set\n", dym_gear_count_, dynamicInfo_.dynamicType);
        return APP_ERR_ACL_FAILURE;
    }

    // add dynamic index tensor
    if (dynamicIndex_ != -1) {
        Base::BaseTensor dyIndexTensor = {};
        dyIndexTensor.buf = dynamicIndexMemory_.ptrData;
        dyIndexTensor.size = dynamicIndexMemory_.size;
        inputs.insert(inputs.begin() + dynamicIndex_, dyIndexTensor);
    }

    // create output memdata
    ret = CreateOutMemoryData(outputsMemDataQue_);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("create outmemory data failed:%d\n", ret);
        return ret;
    }

    // add data to input dataset
    for (const auto& tensor : inputs) {
        auto result = processModel.CreateInput(tensor.buf, tensor.size);
        if (result != SUCCESS) {
            ERROR_LOG("create inputdataset failed:%d\n", result);
            return APP_ERR_ACL_FAILURE;
        }
    }

    // add data to output dataset
    for (const auto& tensor : outputsMemDataQue_) {
        auto result = processModel.CreateOutput(tensor.ptrData, tensor.size);
        if (result != SUCCESS){
            ERROR_LOG("create outputdataset failed:%d\n", result);
            return APP_ERR_ACL_FAILURE;
        }
    }

    ret = SetDynamicInfo();
    if (ret != APP_ERR_OK){
        ERROR_LOG("set dynamic info failed:%d\n", ret);
        return ret;
    }

    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::Inference_GetOutputs(std::vector<std::string> outputNames,
    std::vector<TensorBase> &outputTensors)
{
    for (const auto& name : outputNames) {
        if (modelDesc_.outnames2Index.find(name) == modelDesc_.outnames2Index.end()) {
            ERROR_LOG("outnames %s not valid\n", name.c_str());
            return APP_ERR_ACL_FAILURE;
        }
    }

    APP_ERROR ret = AddOutTensors(outputsMemDataQue_, outputNames, outputTensors);
    if (ret != APP_ERR_OK){
        ERROR_LOG("create outTensor failed ret:%d\n", ret);
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::ModelInference_Inner(std::vector<BaseTensor> &inputs,
    std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors)
{
    APP_ERROR ret = SetInputsData(inputs);
    if (ret != APP_ERR_OK){
        ERROR_LOG("Set InputsData failed ret:%d\n", ret);
        return ret;
    }

    for (int i = 0; i < options_->loop; i++){
        ret = Inference_Execute();
        if (ret != APP_ERR_OK){
            ERROR_LOG("Execute Infer failed ret:%d\n", ret);
            return ret;
        }
    }

    ret = Inference_GetOutputs(outputNames, outputTensors);
    if (ret != APP_ERR_OK){
        ERROR_LOG("Get OutTensors failed ret:%d\n", ret);
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::Inference_Execute()
{
    struct timeval start = { 0 };
    struct timeval end = { 0 };
    gettimeofday(&start, nullptr);

    Result result = processModel.Execute();
    if (result != SUCCESS) {
        ERROR_LOG("acl execute failed:%d\n", result);
        return APP_ERR_ACL_FAILURE;
    }

    gettimeofday(&end, nullptr);
    float time_cost = 1000 * (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000.000;
    DEBUG_LOG("model aclExec const : %f\n", time_cost);
    sumaryInfo_.execTimeList.push_back(time_cost);
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::ResetSumaryInfo()
{
    memset(&sumaryInfo_, 0, sizeof(InferSumaryInfo));
    return APP_ERR_OK;
}

const InferSumaryInfo& ModelInferenceProcessor::GetSumaryInfo()
{
    return sumaryInfo_;
}

APP_ERROR ModelInferenceProcessor::AllocDyIndexMem()
{
    if (dynamicIndex_ == -1 || dynamicIndexMemory_.ptrData != nullptr){
        return APP_ERR_OK;
    }

    TensorDesc info;
    int datatype;
    CHECK_RET_EQ(processModel.GetInTensorDesc(dynamicIndex_, info.name, datatype, info.format, info.shape, info.size), SUCCESS);

    dynamicIndexMemory_.size = info.size;
    dynamicIndexMemory_.type = MemoryData::MemoryType::MEMORY_DEVICE;
    dynamicIndexMemory_.deviceId = deviceId_;
    auto ret = MemoryHelper::MxbsMalloc(dynamicIndexMemory_);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("MemoryHelper::MxbsMalloc failed. ret=", ret);
        return ret;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::FreeDyIndexMem()
{
    if (dynamicIndexMemory_.ptrData != nullptr){
        dynamicIndexMemory_.free(dynamicIndexMemory_.ptrData);
        dynamicIndexMemory_.ptrData = nullptr;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::FreeDymInfoMem()
{
    switch (dynamicInfo_.dynamicType) {
    case DYNAMIC_DIMS:
        if (dynamicInfo_.dyDims.pDims != nullptr){
            free(dynamicInfo_.dyDims.pDims);
            dynamicInfo_.dyDims.pDims = nullptr;
        }
        break;
    case DYNAMIC_SHAPE:
        if (dynamicInfo_.dyShape.pShapes != nullptr){
            free(dynamicInfo_.dyShape.pShapes);
            dynamicInfo_.dyShape.pShapes = nullptr;
        }
        break;
    }
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetStaticBatch(){
    FreeDymInfoMem();
    dynamicInfo_.dynamicType = STATIC_BATCH;
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetDynamicBatchsize(int batchsize){
    bool is_dymbatch = false;

    FreeDymInfoMem();

    CHECK_RET_EQ(processModel.CheckDynamicBatchSize(batchsize, is_dymbatch), SUCCESS);
    CHECK_RET_EQ(processModel.GetMaxBatchSize(dynamicInfo_.dyBatch.maxbatchsize), SUCCESS);

    for (size_t i = 0; i < modelDesc_.inTensorsDesc.size(); ++i) {
        if (find(modelDesc_.inTensorsDesc[i].shape.begin(), modelDesc_.inTensorsDesc[i].shape.end(), -1) != modelDesc_.inTensorsDesc[i].shape.end()){
            modelDesc_.inTensorsDesc[i].realsize = modelDesc_.inTensorsDesc[i].size * batchsize / dynamicInfo_.dyBatch.maxbatchsize;
        }
    }

    dynamicInfo_.dyBatch.batchSize = batchsize;
    dynamicInfo_.dynamicType = DYNAMIC_BATCH;
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetDynamicHW(int width, int height)
{
    bool is_dymHW;
    uint64_t maxDymHWSize;
    pair<uint64_t, uint64_t> dynamicHW = {width, height};

    FreeDymInfoMem();

    CHECK_RET_EQ(processModel.CheckDynamicHWSize(dynamicHW, is_dymHW), SUCCESS);
    CHECK_RET_EQ(processModel.GetMaxDynamicHWSize(dynamicInfo_.dyHW.maxHWSize), SUCCESS);

    for (size_t i = 0; i < modelDesc_.inTensorsDesc.size(); ++i) {
        if (find(modelDesc_.inTensorsDesc[i].shape.begin(), modelDesc_.inTensorsDesc[i].shape.end(), -1) != modelDesc_.inTensorsDesc[i].shape.end()){
            modelDesc_.inTensorsDesc[i].realsize = modelDesc_.inTensorsDesc[i].size * width * height / dynamicInfo_.dyHW.maxHWSize;
        }
    }

    dynamicInfo_.dyHW.imageSize.width = width;
    dynamicInfo_.dyHW.imageSize.height = height;
    dynamicInfo_.dynamicType = DYNAMIC_HW;
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetDynamicDims(std::string dymdimsStr)
{
    // 获取动态维度数量
    CHECK_RET_EQ(processModel.GetDynamicGearCount(dym_gear_count_), SUCCESS);

    FreeDymInfoMem();
    if (dynamicInfo_.dyDims.pDims == nullptr){
        dynamicInfo_.dyDims.pDims = (DyDimsInfo *)calloc(1, sizeof(DyDimsInfo));
    }

    // 如何释放数组 动态
    aclmdlIODims *dims = new aclmdlIODims[dym_gear_count_];
    Utils::SplitStringSimple(dymdimsStr, dynamicInfo_.dyDims.pDims->dym_dims, ';', ':', ',');

    if (dym_gear_count_ <= 0){
        printf("the dynamic_dims parameter is not specified for model conversion");
        delete [] dims;
        free(dynamicInfo_.dyDims.pDims);
        return APP_ERR_ACL_FAILURE;
    }

    Result ret =  processModel.CheckDynamicDims(dynamicInfo_.dyDims.pDims->dym_dims, dym_gear_count_, dims);
    if (ret != SUCCESS) {
        ERROR_LOG("check dynamic dims failed, please set correct dymDims paramenter");
        delete [] dims;
        free(dynamicInfo_.dyDims.pDims);
        return APP_ERR_ACL_FAILURE;
    }

    INFO_LOG("prepare dynamic dims successful");

    // update realsize according real shapes
    vector<string> dymdims_tmp;
    Utils::SplitStringWithPunctuation(dymdimsStr, dymdims_tmp, ';'); 

    std::map<string, int64_t> namedimsmap;
    ret = Utils::SplitStingGetNameDimsMulMap(dymdims_tmp, namedimsmap);
    if (ret != SUCCESS) {
        ERROR_LOG("split dims str failed\n");
        delete [] dims;
        free(dynamicInfo_.dyDims.pDims);
        return APP_ERR_ACL_FAILURE;
    }
    for (auto map : namedimsmap){
        if (modelDesc_.innames2Index.find(map.first) == modelDesc_.innames2Index.end()) {
            WARN_LOG("find no in names:%s\n", map.first.c_str());
            continue;
        }
        size_t inindex = modelDesc_.innames2Index[map.first];   // get intensors index by name
        modelDesc_.inTensorsDesc[inindex].realsize = map.second * aclDataTypeSize(static_cast<aclDataType>(modelDesc_.inTensorsDesc[inindex].datatype));
    }

    delete [] dims;

    dynamicInfo_.dynamicType = DYNAMIC_DIMS;
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetDynamicShape(std::string dymshapeStr)
{
    vector<string> dym_shape_tmp;
    Utils::SplitStringWithPunctuation(dymshapeStr, dym_shape_tmp, ';'); 

    FreeDymInfoMem();
    if (dynamicInfo_.dyShape.pShapes == nullptr){
        dynamicInfo_.dyShape.pShapes = (DyShapeInfo *)calloc(1, sizeof(DyShapeInfo));
    }

    std::map<string, std::vector<int64_t>> name2shapesmap;
    Result ret = processModel.CheckDynamicShape(dym_shape_tmp, name2shapesmap, dynamicInfo_.dyShape.pShapes->dims_num);
    if (ret != SUCCESS) {
        ERROR_LOG("check dynamic shape failed");
        free(dynamicInfo_.dyShape.pShapes);
        return APP_ERR_ACL_FAILURE;
    }

    dynamicInfo_.dyShape.pShapes->dym_shape_map = name2shapesmap;

    // update realsize according real shapes
    std::map<string, int64_t> namedimsmap;
    ret = Utils::SplitStingGetNameDimsMulMap(dym_shape_tmp, namedimsmap);
    if (ret != SUCCESS) {
        ERROR_LOG("split dims str failed");
        free(dynamicInfo_.dyShape.pShapes);
        return APP_ERR_ACL_FAILURE;
    }
    for (auto map : namedimsmap){
        if (modelDesc_.innames2Index.find(map.first) == modelDesc_.innames2Index.end()) {
            WARN_LOG("find no in names:%s\n", map.first.c_str());
            continue;
        }
        size_t inindex = modelDesc_.innames2Index[map.first];   // get intensors index by name
        modelDesc_.inTensorsDesc[inindex].realsize = map.second * aclDataTypeSize(static_cast<aclDataType>(modelDesc_.inTensorsDesc[inindex].datatype));
    }

    dynamicInfo_.dynamicType = DYNAMIC_SHAPE;
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetCustomOutTensorsSize(std::vector<int> customOutSize)
{
    customOutTensorSize_ = customOutSize;
    return APP_ERR_OK;
}

APP_ERROR ModelInferenceProcessor::SetDynamicInfo()
{
    pair<uint64_t, uint64_t> dynamicHW;
    switch (dynamicInfo_.dynamicType) {
    case DYNAMIC_BATCH:
        CHECK_RET_EQ(processModel.SetDynamicBatchSize(dynamicInfo_.dyBatch.batchSize), SUCCESS);
        break;
    case DYNAMIC_HW:
        dynamicHW = {dynamicInfo_.dyHW.imageSize.width, dynamicInfo_.dyHW.imageSize.height};
        CHECK_RET_EQ(processModel.SetDynamicHW(dynamicHW), SUCCESS);
        break;
    case DYNAMIC_DIMS:
        if (dynamicInfo_.dyDims.pDims == nullptr){
            WARN_LOG("error dynamic dims type but pdims is null\n");
        }else{
            CHECK_RET_EQ(processModel.SetDynamicDims(dynamicInfo_.dyDims.pDims->dym_dims), SUCCESS);
        }
        break;
    case DYNAMIC_SHAPE:
        if (dynamicInfo_.dyShape.pShapes == nullptr){
            WARN_LOG("error dynamic shapes type but pshapes is null\n");
        }else{
            CHECK_RET_EQ(processModel.SetDynamicShape(
                dynamicInfo_.dyShape.pShapes->dym_shape_map, dynamicInfo_.dyShape.pShapes->dims_num), SUCCESS);
        }
        break;
    }
    return APP_ERR_OK;
}

}  // namespace Base
