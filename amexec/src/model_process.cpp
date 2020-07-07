//Model_procccess.cpp
 
/**
* @file model_process.cpp
*
* Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
*/
#include "model_process.h"
#include "utils.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <cstddef>
 
using namespace std;
extern bool g_isDevice;
extern bool f_isTXT;
 
ModelProcess::ModelProcess() :modelId_(0), modelMemSize_(0), modelWeightSize_(0), modelMemPtr_(nullptr),
modelWeightPtr_(nullptr), loadFlag_(false), modelDesc_(nullptr), input_(nullptr), output_(nullptr)
{
}
 
ModelProcess::~ModelProcess()
{
    Unload();
    DestroyDesc();
    DestroyInput();
    DestroyOutput();
}
 
Result ModelProcess::LoadModelFromFileWithMem(const char *modelPath)
{
    if (loadFlag_) {
        ERROR_LOG("has already loaded a model");
        return FAILED;
    }
 
    aclError ret = aclmdlQuerySize(modelPath, &modelMemSize_, &modelWeightSize_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("query model failed, model file is %s", modelPath);
        return FAILED;
    }
 
    ret = aclrtMalloc(&modelMemPtr_, modelMemSize_, ACL_MEM_MALLOC_NORMAL_ONLY);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("malloc buffer for mem failed, require size is %zu", modelMemSize_);
        return FAILED;
    }
 
    ret = aclrtMalloc(&modelWeightPtr_, modelWeightSize_, ACL_MEM_MALLOC_NORMAL_ONLY);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("malloc buffer for weight failed, require size is %zu", modelWeightSize_);
        return FAILED;
    }
 
    ret = aclmdlLoadFromFileWithMem(modelPath, &modelId_, modelMemPtr_,
        modelMemSize_, modelWeightPtr_, modelWeightSize_);
    if (ret != ACL_ERROR_NONE) {
        ERROR_LOG("load model from file failed, model file is %s", modelPath);
        return FAILED;
   }
 
    loadFlag_ = true;
    INFO_LOG("load model %s success", modelPath);
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
 
void ModelProcess::DestroyDesc()
{
    if (modelDesc_ != nullptr) {
        (void)aclmdlDestroyDesc(modelDesc_);
        modelDesc_ = nullptr;
    }
}
 
Result ModelProcess::CreateInput(void *inputDataBuffer, size_t bufferSize)
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
 
void ModelProcess::DestroyInput()
{
    if (input_ == nullptr) {
        return;
    }
 
    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(input_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(input_, i);
        aclDestroyDataBuffer(dataBuffer);
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
 
        void *outputBuffer = nullptr;
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
 /*
void ModelProcess::DumpModelOutputResult()
{
    stringstream ss;
    size_t outputNum = aclmdlGetDatasetNumBuffers(output_);
	static int executeNum = 0;
    for (size_t i = 0; i < outputNum; ++i) {
        ss << "output" << ++executeNum << "_" << i << ".bin";
        string outputFileName = ss.str();
        FILE *outputFile = fopen(outputFileName.c_str(), "wb");
        if (outputFile) {
            aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
            void* data = aclGetDataBufferAddr(dataBuffer);
            uint32_t len = aclGetDataBufferSize(dataBuffer);
 
            void* outHostData = NULL;
            aclError ret = ACL_ERROR_NONE;
            if (!g_isDevice) {
                ret = aclrtMallocHost(&outHostData, len);
                if (ret != ACL_ERROR_NONE) {
                    ERROR_LOG("aclrtMallocHost failed, ret[%d]", ret);
                    return;
                }
 
                ret = aclrtMemcpy(outHostData, len, data, len, ACL_MEMCPY_DEVICE_TO_HOST);
                if (ret != ACL_ERROR_NONE) {
                    ERROR_LOG("aclrtMemcpy failed, ret[%d]", ret);
                    (void)aclrtFreeHost(outHostData);
                    return;
                }
 
                fwrite(outHostData, len, sizeof(char), outputFile);
 
                ret = aclrtFreeHost(outHostData);
                if (ret != ACL_ERROR_NONE) {
                    ERROR_LOG("aclrtFreeHost failed, ret[%d]", ret);
                    return;
                }
            } else {
                fwrite(data, len, sizeof(char), outputFile);
            }
            fclose(outputFile);
            outputFile = nullptr;
        } else {
            ERROR_LOG("create output file [%s] failed", outputFileName.c_str());
            return;
        }
    }
 
    INFO_LOG("dump data success");
    return;
}
 */
void ModelProcess::OutputModelResult(std::string& s,std::string& modelName,size_t index)
{
    const char* temp_s = s.c_str();
    if (NULL == opendir(temp_s)){
        mkdir(temp_s,0775);
    }
	std::string T = Utils::TimeLine();
	//std::string t = s.c_str()+"/"+T.c_str();
	//const char* time = t.c_str();
	string times = s+"/"+T+"_"+to_string(index);
	const char* time = times.c_str();
	cout << time <<endl;
	mkdir(time,0775);
    if (NULL == opendir(time))
    {
        ERROR_LOG("current user does not have permission");
        exit(0);
    }
 
    for (size_t i = 0; i < aclmdlGetDatasetNumBuffers(output_); ++i) {
        aclDataBuffer* dataBuffer = aclmdlGetDatasetBuffer(output_, i);
        void* data = aclGetDataBufferAddr(dataBuffer);
        uint32_t len = aclGetDataBufferSize(dataBuffer);
        aclDataType datatype = aclmdlGetOutputDataType(modelDesc_, i);
        void *dims = nullptr;
        aclmdlIODims *dim = nullptr;
        aclError ret = ACL_ERROR_NONE;
        if (!g_isDevice) { 
            ret = aclrtMallocHost(&dims, sizeof(aclmdlIODims));
            if (ret != ACL_ERROR_NONE) {
                ERROR_LOG("aclrtMallocHost failed, ret[%d]", ret);
                return;
            }
		}
		else {
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
 
        void *outHostData = NULL;
        ret = ACL_ERROR_NONE;
        void *outData = NULL;
        if (!g_isDevice) {
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
            switch (datatype)
            {
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
                default :
                    printf("undefined data type!\n");
                    break;
            }
            
        } else {
            outData = reinterpret_cast<float*>(data);
        }
        if (f_isTXT)
        {
            ofstream outstr(times+"/"+modelName+"_output_"+to_string(i)+".txt", ios::out);
            switch (datatype)
            {
                case 0:
                    for (int i = 0; i < len/sizeof(float); i++)
					{
						float out = *((float*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 1:
                    for (int i = 0; i < len/sizeof(aclFloat16); i++)
					{
						aclFloat16 out = *((aclFloat16*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 2:
                    for (int i = 0; i < len/sizeof(int8_t); i++)
					{
						int8_t out = *((int8_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 3:
                    for (int i = 0; i < len/sizeof(int); i++)
					{
						int out = *((int*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 4:
                    for (int i = 0; i < len/sizeof(uint8_t); i++)
					{
						uint8_t out = *((uint8_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 6:
                    for (int i = 0; i < len/sizeof(int16_t); i++)
					{
						int16_t out = *((int16_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 7:
                    for (int i = 0; i < len/sizeof(uint16_t); i++)
					{
						uint16_t out = *((uint16_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 8:
                    for (int i = 0; i < len/sizeof(uint32_t); i++)
					{
						uint32_t out = *((uint32_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 9:
                    for (int i = 0; i < len/sizeof(int64_t); i++)
					{
						int64_t out = *((int64_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 10:
                    for (int i = 0; i < len/sizeof(uint64_t); i++)
					{
						uint64_t out = *((uint64_t*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 11:
                    for (int i = 0; i < len/sizeof(double); i++)
					{
						double out = *((double*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                case 12:
                    for (int i = 0; i < len/sizeof(bool); i++)
					{
						int out = *((bool*)outData+i);
						outstr << out << " ";
						for (int j = 0; j < dim->dimCount; j++)
						{
							if (i !=0 && i%dim->dims[j] == 0 && dim->dims[j] > 10)
								{outstr << "\n" ;}
						}
					}
                    break;
                default :
                    printf("undefined data type!\n");
                    break;
            }
            outstr.close();
        }
        else
        {
            ofstream outstr(times+"/"+modelName+"_output_"+to_string(i)+".bin", ios::out|ios::binary);
     
	        outstr.write((char*)outData, len);
            outstr.close();
        }
 

        if (!g_isDevice) {
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
 
    if (modelMemPtr_ != nullptr) {
        aclrtFree(modelMemPtr_);
        modelMemPtr_ = nullptr;
        modelMemSize_ = 0;
	}
	if (modelWeightPtr_ != nullptr) {
		aclrtFree(modelWeightPtr_);
		modelWeightPtr_ = nullptr;
		modelWeightSize_ = 0;
	}
	
	loadFlag_ = false;
		INFO_LOG("unload model success, model Id is %u", modelId_);
}
