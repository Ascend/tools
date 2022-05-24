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

#ifndef _MODEL_PROCESS_H_
#define _MODEL_PROCESS_H_
#include "acl/acl.h"
#include "utils.h"
#include <string>
#include "Base/Tensor/TensorBase/TensorBase.h"

/**
 * ModelProcess
 */
class ModelProcess {
public:
    /**
    * @brief Constructor
    */
    ModelProcess();

    /**
    * @brief Destructor
    */
    ~ModelProcess();

    /**
    * @brief load model from file with mem
    * @param [in] modelPath: model path
    * @return result
    */
    Result LoadModelFromFile(const std::string& modelPath);

    /**
    * @brief unload model
    */
    void Unload();

    /**
    * @brief create model desc
    * @return result
    */
    Result CreateDesc();

    /**
    * @brief PrintDesc
    */
    Result PrintDesc();

    /**
    * @brief get dynamic gear conut
    */
    Result GetDynamicGearCount(size_t &dymGearCount);

    /**
    * @brief get dynamic index
    */
    Result GetDynamicIndex(size_t &dymindex);    

    /**
    * @brief check dynamic input dims valid
    */
    Result CheckDynamicDims(std::vector<std::string> dym_dims, size_t gearCount, aclmdlIODims* dims);

    /**
    * @brief check dynamic input batch valid
    */
    Result CheckDynamicBatchSize(uint64_t dymbatch, bool& is_dymbatch);

    /**
    * @brief check dynamic input image size valid
    */
    Result CheckDynamicHWSize(std::pair<int, int> dynamicPair, bool& is_dymHW);
 
    /**
    * @brief set dynamic input dims 
    */    
    Result SetDynamicDims(std::vector<std::string> dym_dims);

    /**
    * @brief check dynamic input image size valid
    */
    Result CheckDynamicShape(std::vector<std::string> dym_shape_tmp, std::map<std::string, std::vector<int64_t>> &dym_shape_map, std::vector<int64_t> &dims_num);
    
    /**
    * @brief set dynamic input dims 
    */    
    Result SetDynamicShape(std::map<std::string, std::vector<int64_t>> dym_shape_map, std::vector<int64_t> &dims_num);

    /**
    * @brief set dynamic batch size
    */    
    Result SetDynamicBatchSize(uint64_t batchSize);
    
    /**
    * @brief get max dynamic batch size
    */    
    Result GetMaxBatchSize(uint64_t& maxBatchSize);

    /**
    * @brief set dynamic image size
    */
    Result SetDynamicHW(std::pair<uint64_t , uint64_t > dynamicPair);

    /**
    * @brief get dynamic input dims info
    */
    void GetDimInfo(size_t gearCount, aclmdlIODims* dims);

    /**
    * @brief get dynamic input batch info
    */
    void GetDymBatchInfo();

    /**
    * @brief get dynamic image size info
    */
    void GetDymHWInfo();

    /**
    * @brief destroy desc
    */
    void DestroyDesc();
    
    /**
    * @brief create model input
    * @return result
    */
    Result CreateDymInput(size_t index);

    /**
    * @brief create model input
    * @param [in] inputDataBuffer: input buffer
    * @param [in] bufferSize: input buffer size
    * @return result
    */
    Result CreateInput(void* inputDataBuffer, size_t bufferSize);

    /**
    * @brief create model input
    * @return result
    */
    Result CreateZeroInput();

    /**
    * @brief destroy input resource
    */
    void DestroyInput(bool free_memory_flag);

    /**
    * @brief create output buffer
    * @return result
    */
    Result CreateOutput();

    /**
    * @brief destroy output resource
    */
    void DestroyOutput(bool free_memory_flag);

    /**
    * @brief model execute
    * @return result
    */
    Result Execute();

    /**
    * @brief dump model output result to file
    */
    void DumpModelOutputResult();

    /**
    * @brief get model output result
    */
    void OutputModelResult(std::string& s, std::string& modelName, std::uint64_t dymbatch_size, bool is_dymshape);

    /**
    * @brief get current output dims mul
    */
    Result GetCurOutputDimsMul(size_t index,  std::vector<int64_t>& curOutputDimsMul);

    Result CreateOutput(void* outputBuffer, size_t bufferSize);

    size_t GetNumInputs();
    size_t GetNumOutputs();

    Result GetInTensorDesc(size_t i, std::string& name, int& datatype, size_t& format, std::vector<int64_t>& shape, size_t& size);
    Result GetOutTensorDesc(size_t i, std::string& name, int& datatype, size_t& format, std::vector<int64_t>& shape, size_t& size);

    int GetOutTensorLen(size_t i, bool is_dymshape, float sizeRatio);

    Result GetCurOutputShape(size_t index, std::vector<int64_t>& shape);

    Result GetMaxDynamicHWSize(size_t &outsize);

private:
    uint32_t modelId_;
    bool loadFlag_; // model load flag
    aclmdlDesc* modelDesc_;
    aclmdlDataset* input_;
    aclmdlDataset* output_;
    size_t numInputs_;
    size_t numOutputs_;
    size_t g_dymindex;
};
#endif
