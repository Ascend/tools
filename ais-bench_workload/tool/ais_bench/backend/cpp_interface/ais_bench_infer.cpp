#include <iostream>
#include <random>
#include <memory>

#include <unistd.h>
#include <assert.h>

#include "Base/Tensor/TensorBuffer/TensorBuffer.h"
#include "Base/Tensor/TensorShape/TensorShape.h"
#include "Base/Tensor/TensorContext/TensorContext.h"
#include "Base/Tensor/TensorBase/TensorBase.h"

#include "Base/ModelInfer/SessionOptions.h"
#include "PyInferenceSession/PyInferenceSession.h"

int create_pure_input_tensors(std::vector<Base::TensorDesc> descs, int deviceId, std::vector<Base::TensorBase>& intensors)
{
    for (const auto& desc : descs) {
        std::vector<uint32_t> i32shape;
        for (const auto& shape : desc.shape) {
            i32shape.push_back((uint32_t)shape);
        }
        Base::TensorBase tensor(i32shape, desc.datatype);
        APP_ERROR ret = Base::TensorBase::TensorBaseMalloc(tensor);
        if (ret != APP_ERR_OK) {
            std::cout << "TensorBaseMalloc failed. ret=" << ret << std::endl;
            throw std::runtime_error(GetError(ret));
        }
        ret = tensor.ToDevice(deviceId);
        intensors.push_back(std::move(tensor));
    }
    return 0;
}

int str2num(char* str)
{
    int n = 0;
    int flag = 0;
    while (*str >= '0' && *str <= '9') {
        n = n * 10 + (*str - '0');
        str++;
    }
    if (flag == 1) {
        n = -n;
    }
    return n;
}


int main(int argc, char **argv) {
    std::string modelPath = argv[1];
    int loop = str2num(argv[2]);
    std::string input;
    if (argc > 3) {
        input = argv[3];
    }

    std::shared_ptr<Base::SessionOptions> options = std::make_shared<Base::SessionOptions>();
    options->loop = loop;
    options->log_level = 1;

    int deviceId = 0;
    std::shared_ptr<Base::PyInferenceSession> session = std::make_shared<Base::PyInferenceSession>(modelPath, deviceId, options);
    std::vector<Base::TensorDesc> indescs = session->GetInputs();
    std::vector<Base::TensorDesc> outdescs = session->GetOutputs();
    std::vector<Base::TensorBase> intensors = {};

    std::vector<std::string> output_names;
    for (const auto& desc : outdescs) {
        output_names.push_back(desc.name);
    }

    create_pure_input_tensors(indescs, deviceId, intensors);
    for (const auto& tensor : intensors) {
        printf("in tensor type:%d size:%lld isDevice:%d\n", 
            tensor.GetTensorType(), tensor.GetSize(), tensor.IsDevice());
    }
    if (input.size() != 0){
        std::vector<std::string> fileName_vec;
        std::vector<std::vector<std::vector<std::string>>> infilesList;
        printf("lcm debug ignore\n");
        // Utils::ScanFiles(fileName_vec, input);
        // for (auto &filename : fileName_vec){
        //     std::vector<std::string> file;
        //     file.push_back(input + filename);
        //     std::vector<std::vector<std::string>> files;
        //     files.push_back(file);
        //     infilesList.push_back(files);
        // }
        // session->Infer_InFilesLists_msame(infilesList);
    }else{
        std::vector<Base::TensorBase> outtensors = session->InferVector(output_names, intensors);
        for (const auto& tensor : outtensors) {
            printf("out tensor type:%d size:%lld isDevice:%d\n", 
                tensor.GetTensorType(), tensor.GetSize(), tensor.IsDevice());
        }
    }

    Base::InferSumaryInfo sumary = session->GetSumaryInfo();
    float sum = std::accumulate(std::begin(sumary.execTimeList), std::end(sumary.execTimeList), 0.0);  
    float mean =  sum / sumary.execTimeList.size(); //均值  
    printf("lcm debug avg:%f count:%d\n", mean, sumary.execTimeList.size());
    return 0;
}
