cmake_minimum_required(VERSION 3.0.0)
project(ais_bench_infer VERSION 0.1.0)

# Compile options
add_compile_options(-std=c++11)

add_definitions(-DENABLE_DVPP_INTERFACE)

set(CMAKE_CXX_FLAGS_DEBUG "-fPIC -O0 -g -Wall")
set(CMAKE_CXX_FLAGS_RELEASE "-fPIC -O2 -Wall")

# set_env_path=os.getenv("CANN_PATH", "")
# atlas_nnae_path = "/usr/local/Ascend/nnae/latest/"
# atlas_toolkit_path = "/usr/local/Ascend/ascend-toolkit/latest/"
# hisi_fwk_path = "/usr/local/Ascend/"
# check_file_path = "acllib/lib64/stub/libascendcl.so"

# set(CHECK_FILE_PATH "acllib/lib64/stub/libascendcl.so")

# if (EXISTS ${CHECK_FILE_PATH})

set(BACKEND_PATH ../)

set(INC_PATH $ENV{DDK_PATH})

if (NOT DEFINED ENV{DDK_PATH})
    set(INC_PATH "/usr/local/Ascend/ascend-toolkit/latest")
    message(STATUS "set default INC_PATH: ${INC_PATH}")
else ()
    message(STATUS "env INC_PATH: ${INC_PATH}")
endif()

set(LIB_PATH $ENV{NPU_HOST_LIB})

if (NOT DEFINED ENV{NPU_HOST_LIB})
    set(LIB_PATH "/usr/local/Ascend/ascend-toolkit/latest/acllib/lib64/")
    message(STATUS "set default LIB_PATH: ${LIB_PATH}")
else ()
    message(STATUS "env LIB_PATH: ${LIB_PATH}")
endif()

# Header path
include_directories(
    ${INC_PATH}/acllib/include/
)

# add host lib path
link_directories(
    ${LIB_PATH}
)

# Header path
include_directories(
    ${BACKEND_PATH}/python/include/
    ${BACKEND_PATH}/base/include/
    ${BACKEND_PATH}/base/include/Base/ModelInfer/   
)

include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR})

add_executable(ais_bench_infer
        ${BACKEND_PATH}/base/module/DeviceManager/DeviceManager.cpp
        ${BACKEND_PATH}/base/module/ErrorCode/ErrorCode.cpp
        ${BACKEND_PATH}/base/module/Log/Log.cpp
        ${BACKEND_PATH}/base/module/MemoryHelper/MemoryHelper.cpp
        ${BACKEND_PATH}/base/module/Tensor/TensorBase/TensorBase.cpp
        ${BACKEND_PATH}/base/module/Tensor/TensorBuffer/TensorBuffer.cpp
        ${BACKEND_PATH}/base/module/Tensor/TensorContext/TensorContext.cpp
        ${BACKEND_PATH}/base/module/ModelInfer/model_process.cpp
        ${BACKEND_PATH}/base/module/ModelInfer/utils.cpp
        ${BACKEND_PATH}/base/module/ModelInfer/SessionOptions.cpp
        ${BACKEND_PATH}/base/module/ModelInfer/ModelInferenceProcessor.cpp
        ${BACKEND_PATH}/python/src/PyInferenceSession/PyInferenceSession.cpp
        ais_bench_infer.cpp)

target_link_libraries(ais_bench_infer ascendcl acl_cblas acl_dvpp stdc++ pthread)
