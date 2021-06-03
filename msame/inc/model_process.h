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
    Result GetDynamicIndex(size_t &dymTensorIndex);    

    /**
    * @brief check dynamic input dims valid
    */
    Result CheckDynamicDims(std::vector<std::string> dymDims, size_t gearCount, aclmdlIODims *dims);
    
    /**
    * @brief set dynamic input dims 
    */    
    Result SetDynamicDims(std::vector<std::string> dymDims);

    /**
    * @brief get dynamic input dims info
    */
    void GetDimInfo(size_t gearCount, aclmdlIODims *dims);

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
    void DestroyInput();

    /**
    * @brief create output buffer
    * @return result
    */
    Result CreateOutput();

    /**
    * @brief destroy output resource
    */
    void DestroyOutput();

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
    void OutputModelResult(std::string& s, std::string& modelName);

private:
    uint32_t modelId_;
    bool loadFlag_; // model load flag
    aclmdlDesc* modelDesc_;
    aclmdlDataset* input_;
    aclmdlDataset* output_;
    size_t numInputs_;
    size_t numOutputs_;
};
#endif