cmake_minimum_required(VERSION 3.14)
project(TfdbgAscend)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_C_FLAGS "-D_FORTIFY_SOURCE=2 -O2 -DNDEBUG -Wno-deprecated-declarations -Wall -fPIC -fstack-protector-all -Wl,--no-as-needed -Wl,-z,relro,-z,now,-z,noexecstack -s -fno-common -pipe ${CMAKE_C_FLAGS}")
set(CMAKE_CXX_FLAGS "-D_FORTIFY_SOURCE=2 -O2 -DNDEBUG -Wno-deprecated-declarations -Wall -fPIC -fstack-protector-all -Wl,--no-as-needed -Wl,-z,relro,-z,now,-z,noexecstack -s -fno-common -pipe ${CMAKE_CXX_FLAGS}")
set(CMAKE_SKIP_RPATH TRUE)

IF (${CMAKE_CXX_COMPILER_ID} STREQUAL GNU)
    add_definitions(-Wno-builtin-macro-redefined)
ENDIF ()

if (NOT EXISTS ${CMAKE_CURRENT_LIST_DIR}/tools/COMPILE_FLAGS OR NOT EXISTS
        ${CMAKE_CURRENT_LIST_DIR}/tools/TF_INSTALLED_PATH OR NOT EXISTS
        ${CMAKE_CURRENT_LIST_DIR}/tools/PYTHON_BIN_PATH)
    message(FATAL_ERROR "No validate configuration found. Did you forget to configure first?")
endif ()

file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/tools/TF_INSTALLED_PATH" TF_INSTALLED_PATH)
file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/tools/PYTHON_BIN_PATH" PYTHON_BIN_PATH)

file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/tools/COMPILE_FLAGS" CUSTOM_COMPILE_FLAGS)
foreach (COMPILE_FLAG ${CUSTOM_COMPILE_FLAGS})
    set(CMAKE_C_FLAGS "${COMPILE_FLAG} ${CMAKE_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${COMPILE_FLAG} ${CMAKE_CXX_FLAGS}")
endforeach (COMPILE_FLAG)

# Find pybind11
find_package(pybind11 REQUIRED)
INCLUDE_DIRECTORIES(${pybind11_INCLUDE_DIRS} ./)
set(PYBIND11_CPP_STANDARD -std=c++11)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/tensorflow/module.cmake)

set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR}/dist/libs)

file(GLOB_RECURSE SOURCES ${CMAKE_CURRENT_LIST_DIR}/src/*.cpp)
foreach (CPP_SOURCE ${SOURCES})
    file(RELATIVE_PATH RELATIVE_CPP_SOURCE ${CMAKE_CURRENT_SOURCE_DIR} ${CPP_SOURCE})
    set_property(SOURCE ${CPP_SOURCE} PROPERTY COMPILE_DEFINITIONS __FILE__=\"${RELATIVE_CPP_SOURCE}\")
endforeach (CPP_SOURCE)

add_library(_tfdbg_ascend MODULE EXCLUDE_FROM_ALL ${SOURCES})
set_target_properties(_tfdbg_ascend PROPERTIES PREFIX "")
target_link_libraries(_tfdbg_ascend PRIVATE tensorflow_libs pybind11::module)
add_custom_target(tfdbg_ascend ALL
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_LIST_DIR}/src/python ${CMAKE_BINARY_DIR}/dist/tfdbg_ascend
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/dist/libs/_tfdbg_ascend.so ${CMAKE_BINARY_DIR}/dist/tfdbg_ascend/tfdbg_ascend
        COMMAND cd ${CMAKE_BINARY_DIR}/dist/tfdbg_ascend && ${PYTHON_BIN_PATH} setup.py bdist_wheel
        DEPENDS _tfdbg_ascend
        VERBATIM
        )

install(CODE "execute_process(COMMAND ${PYTHON_BIN_PATH} -m pip install ${CMAKE_BINARY_DIR}/dist/tfdbg_ascend/dist/tfdbg_ascend-0.2-py3-none-any.whl --upgrade)")
