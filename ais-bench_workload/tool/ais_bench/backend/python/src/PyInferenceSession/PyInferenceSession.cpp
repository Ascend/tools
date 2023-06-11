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
#include "PyInferenceSession/PyInferenceSession.h"

#include <exception>

#include "Base/DeviceManager/DeviceManager.h"
#include "Base/Tensor/TensorBuffer/TensorBuffer.h"
#include "Base/Tensor/TensorShape/TensorShape.h"
#include "Base/Tensor/TensorContext/TensorContext.h"
#include "Base/ErrorCode/ErrorCode.h"
#include "Base/Log/Log.h"

namespace Base {
PyInferenceSession::PyInferenceSession(const std::string &modelPath, const uint32_t &deviceId, std::shared_ptr<SessionOptions> options) : deviceId_(deviceId)
{
    Init(modelPath, options);
}

int PyInferenceSession::Destroy()
{
    if (InitFlag_ == false) {
        return APP_ERR_OK;
    }
    APP_ERROR ret = TensorContext::GetInstance()->SetContext(deviceId_);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("TensorContext::SetContext failed. ret=%d", ret);
        return ret;
    }
    ret = modelInfer_.DeInit();
    if (ret != APP_ERR_OK) {
        ERROR_LOG("ModelInfer Deinit failed. ret=%d", ret);
        return ret;
    }
    DEBUG_LOG("PyInferSession DestroySession successfully!");
    InitFlag_ = false;
    return APP_ERR_OK;
}

int PyInferenceSession::Finalize()
{
    APP_ERROR ret = TensorContext::GetInstance()->SetContext(deviceId_);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("TensorContext::SetContext failed. ret=%d", ret);
        return ret;
    }

    ret = Destroy();
    if (ret != APP_ERR_OK) {
        ERROR_LOG("TensorContext::Finalize. ret=%d", ret);
        return ret;
    }
    ret = TensorContext::GetInstance()->Finalize();
    if (ret != APP_ERR_OK) {
        ERROR_LOG("TensorContext::Finalize. ret=%d", ret);
        return ret;
    }
    DEBUG_LOG("PyInferSession Finalize successfully!");
    return APP_ERR_OK;
}

PyInferenceSession::~PyInferenceSession()
{
    Destroy();
}

void PyInferenceSession::Init(const std::string &modelPath, std::shared_ptr<SessionOptions> options)
{
    DeviceManager::GetInstance()->SetAclJsonPath(options->aclJsonPath);

    APP_ERROR ret = TensorContext::GetInstance()->SetContext(deviceId_);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }

    ret = modelInfer_.Init(modelPath, options, deviceId_);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    InitFlag_ = true;

}

std::vector<TensorBase> PyInferenceSession::InferMap(std::vector<std::string>& output_names, std::map<std::string, TensorBase>& feeds)
{
    DEBUG_LOG("start to ModelInference feeds");

    std::vector<TensorBase> outputs = {};
    APP_ERROR ret = modelInfer_.Inference(feeds, output_names, outputs);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }

    return outputs;
}

std::vector<TensorBase> PyInferenceSession::InferVector(std::vector<std::string>& output_names, std::vector<TensorBase>& feeds)
{
    DEBUG_LOG("start to ModelInference");

    std::vector<TensorBase> outputs = {};
    APP_ERROR ret = modelInfer_.Inference(feeds, output_names, outputs);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }

    return outputs;
}

std::string GetShapeDesc(std::vector<int64_t> shape)
{
    std::string shapeStr = "(";
    for (size_t i = 0; i < shape.size(); ++i) {
        shapeStr += std::to_string(shape.at(i));
        if (i != shape.size() - 1) {
            shapeStr += ", ";
        }
    }
    shapeStr += ")";
    return shapeStr;
}

std::string GetTensorDesc(Base::TensorDesc desc)
{
    return GetShapeDesc(desc.shape) + "  " + Base::GetTensorDataTypeDesc(desc.datatype) + "  " + std::to_string(desc.size) + "  " + std::to_string(desc.realsize);
}

uint32_t PyInferenceSession::GetDeviceId() const
{
    return deviceId_;
}

const std::vector<Base::TensorDesc>& PyInferenceSession::GetInputs()
{
    return modelInfer_.GetInputs();

}

const std::vector<Base::TensorDesc>& PyInferenceSession::GetOutputs()
{
    return modelInfer_.GetOutputs();
}

std::shared_ptr<SessionOptions> PyInferenceSession::GetOptions()
{
    return modelInfer_.GetOptions();
}

std::string PyInferenceSession::GetDesc()
{
    std::string inputStr = "input:\n";
    std::string outputStr = "output:\n";
    auto &inTensorsDesc = modelInfer_.GetInputs();

    for (size_t i = 0; i < inTensorsDesc.size(); ++i) {
        inputStr += "  #" + std::to_string(i) + "  ";
        inputStr += "  " + inTensorsDesc[i].name + "  ";
        inputStr += GetTensorDesc(inTensorsDesc[i]) + "\n";
    }

    auto &outTensorsDesc = modelInfer_.GetOutputs();
    for (size_t i = 0; i < outTensorsDesc.size(); ++i) {
        outputStr += "  #" + std::to_string(i) + "  ";
        outputStr += "  " + outTensorsDesc[i].name + "  ";
        outputStr += GetTensorDesc(outTensorsDesc[i]) + "\n";
    }

    return "<Model>\ndevice:\t" + std::to_string(GetDeviceId()) + "\n" + inputStr + outputStr;
}

const InferSumaryInfo& PyInferenceSession::GetSumaryInfo()
{
    return modelInfer_.GetSumaryInfo();
}

int PyInferenceSession::ResetSumaryInfo()
{
    APP_ERROR ret = modelInfer_.ResetSumaryInfo();
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

int PyInferenceSession::SetStaticBatch()
{
    APP_ERROR ret = modelInfer_.SetStaticBatch();
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

int PyInferenceSession::SetDynamicBatchsize(int batchsize)
{
    APP_ERROR ret = modelInfer_.SetDynamicBatchsize(batchsize);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

int PyInferenceSession::SetDynamicHW(int width, int height)
{
    APP_ERROR ret = modelInfer_.SetDynamicHW(width, height);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

int PyInferenceSession::SetDynamicDims(std::string dymdimsStr)
{
    APP_ERROR ret = modelInfer_.SetDynamicDims(dymdimsStr);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

int PyInferenceSession::SetDynamicShape(std::string dymshapeStr)
{
    APP_ERROR ret = modelInfer_.SetDynamicShape(dymshapeStr);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

int PyInferenceSession::SetCustomOutTensorsSize(std::vector<size_t> customOutSize)
{
    APP_ERROR ret = modelInfer_.SetCustomOutTensorsSize(customOutSize);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    return APP_ERR_OK;
}

std::vector<TensorBase> PyInferenceSession::InferBaseTensorVector(std::vector<std::string>& output_names, std::vector<Base::BaseTensor>& feeds)
{
    DEBUG_LOG("start to ModelInference base_tensor");

    std::vector<MemoryData> memorys = {};
    std::vector<BaseTensor> inputs = {};
    for (auto &info : feeds) {
        MemoryData mem = CopyMemory2DeviceMemory(info.buf, info.size, deviceId_);
        memorys.push_back(mem);
        BaseTensor tensor(mem.ptrData, mem.size);
        inputs.push_back(tensor);
    }

    std::vector<TensorBase> outputs = {};
    APP_ERROR ret = modelInfer_.Inference(inputs, output_names, outputs);
    if (ret != APP_ERR_OK) {
        throw std::runtime_error(GetError(ret));
    }
    for (auto &mem : memorys) {
        MemoryHelper::Free(mem);
    }
    return outputs;
}

TensorBase PyInferenceSession::CreateTensorFromFilesList(Base::TensorDesc &dstTensorDesc, std::vector<std::string>& filesList)
{
    std::vector<uint32_t> u32shape;
    for (size_t j = 0; j < dstTensorDesc.shape.size(); ++j) {
        u32shape.push_back((uint32_t)(dstTensorDesc.shape[j]));
    }
    // malloc
    TensorBase dstTensor = TensorBase(u32shape, dstTensorDesc.datatype,
        MemoryData::MemoryType::MEMORY_HOST, -1);
    APP_ERROR ret = Base::TensorBase::TensorBaseMalloc(dstTensor);
    if (ret != APP_ERR_OK) {
        ERROR_LOG("TensorBaseMalloc failed ret:%d", ret);
        throw std::runtime_error(GetError(ret));
    }
    // copy
    size_t offset = 0;
    char *ptr = (char *)dstTensor.GetBuffer();
    for (uint32_t i = 0; i < filesList.size(); i++) {
        Result ret = Utils::FillFileContentToMemory(filesList[i], ptr, dstTensor.GetByteSize(), offset);
        if (ret != SUCCESS) {
            ERROR_LOG("TensorBaseMalloc i:%d file:%s failed ret:%d", i, filesList[i].c_str(), ret);
            throw std::runtime_error(GetError(ret));
        }
    }
    dstTensor.ToDevice(deviceId_);
    return dstTensor;
}

}

std::shared_ptr<Base::PyInferenceSession> CreateModelInstance(const std::string &modelPath, const uint32_t &deviceId, std::shared_ptr<Base::SessionOptions> options)
{
    return std::make_shared<Base::PyInferenceSession>(modelPath, deviceId, options);
}

#ifdef COMPILE_PYTHON_MODULE
void RegistInferenceSession(py::module &m)
{
    using namespace pybind11::literals;

    py::class_<Base::BaseTensor>(m, "BaseTensor")
        .def(py::init<int64_t, int64_t>())
        .def_readwrite("buf", &Base::BaseTensor::buf)
        .def_readwrite("size", &Base::BaseTensor::size);

    py::class_<Base::SessionOptions, std::shared_ptr<Base::SessionOptions>>(m, "session_options")
    .def(py::init([]() { return std::make_shared<Base::SessionOptions>(); }))
    .def_readwrite("loop", &Base::SessionOptions::loop)
    .def_readwrite("log_level", &Base::SessionOptions::log_level)
    .def_readwrite("acl_json_path", &Base::SessionOptions::aclJsonPath);

    py::class_<Base::TensorDesc>(m, "tensor_desc")
    .def(pybind11::init<>())
    .def_readwrite("name", &Base::TensorDesc::name)
    .def_readwrite("datatype", &Base::TensorDesc::datatype)
    .def_readwrite("format", &Base::TensorDesc::format)
    .def_readwrite("shape", &Base::TensorDesc::shape)
    .def_readwrite("realsize", &Base::TensorDesc::realsize)
    .def_readwrite("size", &Base::TensorDesc::size);

    py::class_<Base::InferSumaryInfo>(m, "sumary")
    .def(pybind11::init<>())
    .def_readwrite("exec_time_list", &Base::InferSumaryInfo::execTimeList);

    auto model = py::class_<Base::PyInferenceSession, std::shared_ptr<Base::PyInferenceSession>>(m, "InferenceSession");
    model.def(py::init<std::string&, int, std::shared_ptr<Base::SessionOptions>>());
    model.def("run", &Base::PyInferenceSession::InferVector);
    model.def("run", &Base::PyInferenceSession::InferMap);
    model.def("run", &Base::PyInferenceSession::InferBaseTensorVector);
    model.def("__str__", &Base::PyInferenceSession::GetDesc);
    model.def("__repr__", &Base::PyInferenceSession::GetDesc);

    model.def("options", &Base::PyInferenceSession::GetOptions, py::return_value_policy::reference);

    model.def("sumary", &Base::PyInferenceSession::GetSumaryInfo, py::return_value_policy::reference);
    model.def("get_inputs", &Base::PyInferenceSession::GetInputs, py::return_value_policy::reference);
    model.def("get_outputs", &Base::PyInferenceSession::GetOutputs, py::return_value_policy::reference);

    model.def("reset_sumaryinfo", &Base::PyInferenceSession::ResetSumaryInfo);
    model.def("set_staticbatch", &Base::PyInferenceSession::SetStaticBatch);
    model.def("set_dynamic_batchsize", &Base::PyInferenceSession::SetDynamicBatchsize);
    model.def("set_dynamic_hw", &Base::PyInferenceSession::SetDynamicHW);
    model.def("set_dynamic_dims", &Base::PyInferenceSession::SetDynamicDims);
    model.def("set_dynamic_shape", &Base::PyInferenceSession::SetDynamicShape);
    model.def("set_custom_outsize", &Base::PyInferenceSession::SetCustomOutTensorsSize);

    model.def("create_tensor_from_fileslist", &Base::PyInferenceSession::CreateTensorFromFilesList);
    model.def("finalize", &Base::PyInferenceSession::Finalize);

    m.def("model", &CreateModelInstance, "modelPath"_a, "deviceId"_a = 0, "options"_a=py::none());
}
#endif
