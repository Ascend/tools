cmake_minimum_required(VERSION 3.5)
project(PtdbgAscend)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_SKIP_RPATH TRUE)

if (NOT EXISTS  ${CMAKE_CURRENT_LIST_DIR}/tools/PYTHON_BIN_PATH)
    message(FATAL_ERROR "No validate configuration found. Did you forget to configure first?")
endif ()

file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/tools/PYTHON_BIN_PATH" PYTHON_BIN_PATH)

add_custom_target(ptdbg_ascend ALL
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_LIST_DIR}/src/python ${CMAKE_BINARY_DIR}/ptdbg_ascend
        COMMAND cd ${CMAKE_BINARY_DIR}/ptdbg_ascend && ${PYTHON_BIN_PATH} setup.py bdist_wheel
        VERBATIM
	)

install(CODE "execute_process(COMMAND ${PYTHON_BIN_PATH} -m pip install ${CMAKE_BINARY_DIR}/ptdbg_ascend/dist/ptdbg_ascend-2.3-py3-none-any.whl --upgrade)")
