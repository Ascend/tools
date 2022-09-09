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

#ifndef PY_MODEL_INFFER
#define PY_MODEL_INFFER

#include <iostream>
#include <vector>
#include <string>
#include <memory>

#ifdef COMPILE_PYTHON_MODULE
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#endif

#include "Base/ModelInfer/SessionOptions.h"

#include "Base/ModelInfer/ModelInferenceProcessor.h"
#include "Base/Tensor/TensorBase/TensorBase.h"

namespace Base {


class PyInferenceSession
{
public:
    PyInferenceSession(const std::string &modelPath, const uint32_t &deviceId, std::shared_ptr<SessionOptions> options);
    ~PyInferenceSession();
    
    std::vector<TensorBase> InferMap(std::vector<std::string>& output_names, std::map<std::string, TensorBase>& feeds);
    std::vector<TensorBase> InferVector(std::vector<std::string>& output_names, std::vector<TensorBase>& feeds);

    std::vector<std::vector<uint64_t>> GetDynamicHW();
    std::vector<int64_t> GetDynamicBatch();

    const std::vector<Base::TensorDesc>& GetInputs();
    const std::vector<Base::TensorDesc>& GetOutputs();

    uint32_t GetDeviceId() const;
    std::string GetDesc();

    std::shared_ptr<SessionOptions> GetOptions();

    const InferSumaryInfo& GetSumaryInfo();

    int ResetSumaryInfo();
    int SetStaticBatch();
    int SetDynamicBatchsize(int batchsize);
    int SetDynamicHW(int width, int height);
    int SetDynamicDims(std::string dymdimsStr);

    int SetDynamicShape(std::string dymshapeStr);
    int SetCustomOutTensorsSize(std::vector<int> customOutSize);

    int InferVector_SetInputs(std::vector<TensorBase>& feeds);
    int InferMap_SetInputs(std::map<std::string, TensorBase>& feeds);
    int Infer_Execute(int loop);
    std::vector<TensorBase> Infer_GetOutputs(std::vector<std::string>& output_names);

    Base::ModelInferenceProcessor modelInfer_ = {};

private:
    void Init(const std::string &modelPath, std::shared_ptr<SessionOptions> options);
private:
    uint32_t deviceId_ = 0;
    Base::ModelDesc modelDesc_ = {};
};
}

#ifdef COMPILE_PYTHON_MODULE
    namespace py = pybind11;

    void RegistInferenceSession(py::module &m);
#endif

#endif

