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

#ifndef MODLE_INFERENCEPROCESSOR_H
#define MODLE_INFERENCEPROCESSOR_H

#include <memory>
#include <vector>
#include "Base/ErrorCode/ErrorCode.h"
#include "Base/Tensor/TensorBase/TensorBase.h"

#include "Base/ModelInfer/SessionOptions.h"
#include "Base/ModelInfer/model_process.h"

#define CHECK_RET_EQ(func, expect_value) \
{ \
auto ret = (func); \
if (ret != expect_value) { \
    WARN_LOG("Check failed:%s, ret:%d\n", #func, ret); \
    return ret; \
} \
}

namespace Base {

struct BaseTensor {
    void* buf;
    std::vector<int64_t> shape;
    size_t size;
    size_t len;
};

struct TensorDesc
{
    std::string name;
    TensorDataType datatype;
    size_t format;
    std::vector<int64_t> shape;
    size_t size;
    size_t realsize;    // 针对动态shape 动态分档场景 实际需要的大小
};

enum DataFormat {
    NCHW = 0,
    NHWC = 1
};

enum DynamicType {
    STATIC_BATCH = 0,
    DYNAMIC_BATCH = 1,
    DYNAMIC_HW = 2,
    DYNAMIC_DIMS = 3,
    DYNAMIC_SHAPE = 4,
};

struct ImageSize {
    size_t height;
    size_t width;

    ImageSize() = default;

    ImageSize(size_t height, size_t width)
    {
        this->width = width;
        this->height = height;
    }
};

struct DyDimsInfo {
    std::vector<std::string> dym_dims;
};

struct DyShapeInfo {
    std::vector<int64_t> dims_num;
    std::map<string, std::vector<int64_t>> dym_shape_map;
};

struct DynamicInfo {
    DynamicType dynamicType = STATIC_BATCH;
    union{
        struct {
            uint64_t batchSize;
        }staticBatch;
        struct {
            uint64_t batchSize;
            uint64_t maxbatchsize;
        }dyBatch;
        struct {
            ImageSize imageSize;
            uint64_t maxHWSize;
        }dyHW;
        struct {
            DyDimsInfo* pDims;
        }dyDims;
        struct {
            DyShapeInfo* pShapes;
        }dyShape;
    };
};

struct ModelDesc {

    std::vector<Base::TensorDesc> inTensorsDesc;   // 所有 intensors信息 不包括dynamic index
    std::vector<Base::TensorDesc> outTensorsDesc;  // 所有out tensors信息

    std::map<std::string, size_t> innames2Index;

    std::map<std::string, size_t> outnames2Index;
};

struct InferSumaryInfo {
    std::vector<float> execTimeList;
};

class ModelInferenceProcessor {
public:
    /**
     * @description Init
     * 1.Loading  Model
     * 2.Get input sizes and output sizes
     * @return APP_ERROR error code
     */
    APP_ERROR Init(const std::string& modelPath, std::shared_ptr<SessionOptions> options, const int32_t &deviceId);

    /**
     * @description Unload Model
     * @return APP_ERROR error code
     */
    APP_ERROR DeInit(void);

    /**
     * @description ModelInference
     * 1.Get model description
     * 2.Execute model infer
     * @return APP_ERROR error code
     */
    APP_ERROR Inference(const std::vector<TensorBase>& feeds, std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors);

    APP_ERROR Inference(const std::map<std::string, TensorBase>& feeds, std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors);

    APP_ERROR ModelInference_Inner(std::vector<BaseTensor> &inputs, std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors);

    /**
     * @description get modelDesc
     */
    const std::vector<Base::TensorDesc>& GetInputs() const;
    const std::vector<Base::TensorDesc>& GetOutputs() const;

    std::shared_ptr<SessionOptions> GetOptions();

    APP_ERROR ResetSumaryInfo();
    const InferSumaryInfo& GetSumaryInfo();

    APP_ERROR SetStaticBatch();
    APP_ERROR SetDynamicBatchsize(int batchsize);
    APP_ERROR SetDynamicHW(int width, int height);
    APP_ERROR SetDynamicDims(std::string dymdimsStr);
    APP_ERROR SetDynamicShape(std::string dymshapeStr);
    APP_ERROR SetCustomOutTensorsSize(std::vector<int> customOutSize);

    APP_ERROR Inference_SetInputs(const std::vector<TensorBase>& feeds);
    APP_ERROR Inference_SetInputs(const std::map<std::string, TensorBase>& feeds);
    APP_ERROR Inference_Execute();
    APP_ERROR Inference_GetOutputs(std::vector<std::string> outputNames, std::vector<TensorBase> &outputTensors);

private:

    APP_ERROR SetDynamicInfo();

    APP_ERROR AllocDyIndexMem();
    APP_ERROR FreeDyIndexMem();
    APP_ERROR FreeDymInfoMem();

    APP_ERROR DestroyOutMemoryData(std::vector<MemoryData>& outputs);
    APP_ERROR CreateOutMemoryData(std::vector<MemoryData>& outputs);
    APP_ERROR AddOutTensors(std::vector<MemoryData>& outputs, std::vector<std::string> outputNames, std::vector<TensorBase>& outputTensors);

    APP_ERROR GetModelDescInfo();
    APP_ERROR DestroyInferCacheData();
    APP_ERROR SetInputsData(std::vector<BaseTensor> &inputs);
    APP_ERROR CheckInVectorAndFillBaseTensor(const std::vector<TensorBase>& feeds, std::vector<BaseTensor> &inputs);
    APP_ERROR CheckInMapAndFillBaseTensor(const std::map<std::string, TensorBase>& feeds, std::vector<BaseTensor> &inputs);

private:
    ModelDesc modelDesc_;

    InferSumaryInfo sumaryInfo_ = {};
    ModelProcess processModel;
    DynamicInfo dynamicInfo_ = {};

    size_t dynamicIndex_ = -1;
    MemoryData dynamicIndexMemory_;

    size_t dym_gear_count_;

    std::shared_ptr<SessionOptions> options_;
    int32_t deviceId_;

    std::vector<int> customOutTensorSize_;
    std::vector<MemoryData> outputsMemDataQue_;
};
}  // namespace Base
#endif
