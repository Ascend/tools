#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
runtime api module
"""

import os
import time
import math
import ctypes
from typing import Union

from op_test_frame.utils import file_util
from op_test_frame.common import logger
from . import rts_info


# 'pylint: disable=too-few-public-methods,too-many-instance-attributes
# 'pylint: disable=invalid-name,unused-variable,no-self-use
# 'pylint: disable=too-many-arguments,too-many-public-methods
class rtDevBinary_t(ctypes.Structure):
    """
    Class rtDevBinary_t
    """
    _fields_ = [('magic', ctypes.c_uint32),
                ('version', ctypes.c_uint32),
                ('data', ctypes.c_char_p),
                ('length', ctypes.c_uint64)]


class rtProfDataInfo_t(ctypes.Structure):
    """
    Class rtProfDataInfo_t
    """
    ONLINE_PROF_MAX_PMU_NUM = 8
    _fields_ = [('stubfunc', ctypes.c_void_p),
                ('blockDim', ctypes.c_uint32),
                ('args', ctypes.c_void_p),
                ('argsSize', ctypes.c_uint32),
                ('smDesc', ctypes.c_void_p),
                ('stream', ctypes.c_uint64),
                ('totalcycle', ctypes.c_uint64),
                ('ovcycle', ctypes.c_uint64),
                ('pmu_cnt', ctypes.c_uint64 * ONLINE_PROF_MAX_PMU_NUM)]


class rtDeviceInfo_t(ctypes.Structure):
    """
    Class rtDeviceInfo_t
    """
    _fields_ = [('env_type', ctypes.c_uint8),
                ('ctrl_cpu_ip', ctypes.c_uint32),
                ('ctrl_cpu_core_num', ctypes.c_uint32),
                ('ctrl_cpu_endian_little', ctypes.c_uint32),
                ('ts_cpu_core_num', ctypes.c_uint32),
                ('ai_cpu_core_num', ctypes.c_uint32),
                ('ai_core_num', ctypes.c_uint32),
                ('ai_core_freq', ctypes.c_uint32),
                ('ai_cpu_core_id', ctypes.c_uint32),
                ('aicpu_occupy_bitmap', ctypes.c_uint32),
                ('hardware_version', ctypes.c_uint32),
                ('ts_num', ctypes.c_uint32), ]


_MODEL_SO_LIST = {
    "pv": ("lib_pvmodel.so", "libtsch.so", "libnpu_drv_pvmodel.so", "libruntime_cmodel.so"),
    "ca": ("libcamodel.so", "libtsch_camodel.so", "libnpu_drv_camodel.so", "libruntime_camodel.so"),
    "tm": ("libpem_davinci.so", "libtsch.so", "libnpu_drv_pvmodel.so", "libruntime_cmodel.so"),
    "esl": ("libnpu_drv_camodel.so", "libruntime_camodel.so")
}

# to avoid release kernel name pointer
kernel_name_cache = []


class AscendRTSApi:
    """
    Class AscendRTSApi
    """
    def __init__(self, simulator_mode: str = None, soc_version: str = None, simulator_lib_path: str = None,
                 simulator_dump_path: str = "./model"):
        """
        call rts by this api
        if simulator mode is None, will call real ascend device
        simulator can be "ca/pv/tm"

        Parameters
        ----------
        simulator_mode : str, option
            can be None/pv/ca/tm
        soc_version : str, option
            soc version like Ascend910, Ascend310
        simulator_lib_path : str, option
            simulator library path, usually is /usr/local/Ascend/toolkit/tools/simulator
        simulator_dump_path : str, option
            simulator dump path, where to save simulator dump data
        """

        logger.log_info("Load RTS shared library...")
        self.rtsdll = None
        self._simulator_mode = simulator_mode
        if simulator_mode is None:
            self._load_runtime_so()
        else:
            self._simulator_dlls = []
            self._load_simulator_so(simulator_mode, soc_version, simulator_lib_path, simulator_dump_path)
        self.device_id = None
        self.context = None
        self.camodel = simulator_mode == "ca"
        self.kernel_binary_storage = {}
        self.kernel_name_storage = {}
        self.context_storage = []

    def _clear_env(self):
        if self._simulator_mode:
            all_ld_path = os.environ['LD_LIBRARY_PATH']
            all_ld_paths = all_ld_path.split(":")
            if len(all_ld_paths) > 2:
                all_ld_paths = all_ld_paths[:-2]
            os.environ['LD_LIBRARY_PATH'] = ":".join(all_ld_paths)

    def _load_runtime_so(self):
        def _find_runtime_so():
            ld_lib_paths = os.environ['LD_LIBRARY_PATH']
            if not ld_lib_paths:
                raise RuntimeError("LD_LIBRARY_PATH is empty can't find runtime.so")
            ld_lib_path_list = ld_lib_paths.split(":")
            for ld_lib_path in ld_lib_path_list:
                runtime_so_path_tmp = os.path.join(ld_lib_path, "libruntime.so")
                if os.path.exists(runtime_so_path_tmp):
                    return runtime_so_path_tmp
            return None

        rts_so_path = _find_runtime_so()
        if not rts_so_path:
            raise RuntimeError("Not found libruntime.so, please check your LD_LIBRARY_PATH")
        logger.log_info("find runtime so path is: %s" % rts_so_path)
        self.rtsdll = ctypes.CDLL(rts_so_path)

    def _init_simulator_so_path(self, simulator_mode, soc_version, simulator_lib_path):
        simulator_lib_realpath = os.path.realpath(simulator_lib_path)
        simulator_lib_dir = os.path.join(simulator_lib_realpath, soc_version, "lib")
        if not os.path.exists(simulator_lib_dir):
            raise RuntimeError(
                "Simulator lib path([simulator_lib_path]/[soc_version]/lib) is not exist, path: %s." %
                simulator_lib_dir
            )

        simulator_so_list = _MODEL_SO_LIST[simulator_mode]
        so_full_path_list = []
        for so_name in simulator_so_list:
            so_path = os.path.join(simulator_lib_dir, so_name)
            if not os.path.exists(so_path):
                raise RuntimeError("Simulator so is not exist, path: %s" % so_path)
            so_full_path_list.append(so_path)
        common_data_path = os.path.join(simulator_lib_realpath, "common", "data")
        if not os.path.exists(common_data_path):
            raise RuntimeError("Simulator common data path is not exist, path: %s" % common_data_path)
        addition_ld_lib_path = simulator_lib_dir + ":" + common_data_path
        return so_full_path_list, addition_ld_lib_path

    def _dll_simulator_so(self, so_path_list, addition_ld_lib_paths, simulator_dump_path):
        os.environ['LD_LIBRARY_PATH'] += ":" + addition_ld_lib_paths
        os.environ['CAMODEL_LOG_PATH'] = simulator_dump_path
        so_path = ''
        for so_path in so_path_list[:-1]:
            try:
                so_handler = ctypes.CDLL(so_path, mode=ctypes.RTLD_GLOBAL)
            except BaseException as cdll_err:
                raise RuntimeError("CDLL so failed, so_path: %s" % so_path) from cdll_err
            self._simulator_dlls.append(so_handler)

        try:
            so_handler = ctypes.CDLL(so_path_list[-1], mode=ctypes.RTLD_GLOBAL)
        except BaseException as cdll_err:
            raise RuntimeError("CDLL so failed, so_path: %s" % so_path) from cdll_err
        self.rtsdll = so_handler

    def _load_simulator_so(self, simulator_mode: str = None, soc_version: str = None, simulator_lib_path: str = None,
                           simulator_dump_path: str = "./model"):
        logger.log_info("start load ascend simulator")
        if not isinstance(simulator_mode, str):
            raise TypeError("simulator_mode need to be a str, actual is: %s." % str(type(simulator_mode)))
        if simulator_mode not in _MODEL_SO_LIST.keys():
            raise ValueError(
                "simulator_mode need to be %s, actual is %s" % ("/".join(_MODEL_SO_LIST.keys()), simulator_mode))
        simulator_dump_path = os.path.realpath(simulator_dump_path)
        if not os.path.exists(simulator_dump_path):
            raise RuntimeError("simulator_dump_path is not exist.")

        so_path_list, addition_ld_paths = self._init_simulator_so_path(simulator_mode, soc_version, simulator_lib_path)
        self._dll_simulator_so(so_path_list, addition_ld_paths, simulator_dump_path)
        logger.log_info("Load ascend simulator success.")

    def set_device(self, device_id: int) -> None:
        """
        Set device_id for current thread

        Parameters
        ----------
        device_id : int
            device id you want to switch to

        Returns
        -------
        None

        """
        self.rtsdll.rtSetDevice.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtSetDevice(device_id)
        self.parse_error(rt_error, "rtSetDevice")
        self.device_id = device_id

    def get_device_info(self, device_id: int, module_type: str, info_type: str):
        """
        get device info
        """
        c_info = (ctypes.c_int64 * 8)()
        module_type = rts_info.RT_MODULE_TYPE[module_type]
        info_type = rts_info.RT_INFO_TYPE[info_type]
        self.rtsdll.rtGetDeviceInfo.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtGetDeviceInfo(ctypes.c_uint32(device_id),
                                               ctypes.c_int32(module_type),
                                               ctypes.c_int32(info_type),
                                               c_info)
        self.parse_error(rt_error, "rtGetDeviceInfo")
        result = int(c_info[0])
        if info_type == rts_info.RT_INFO_TYPE["INFO_TYPE_ENV"]:
            info_dict = {
                0: "FPGA",
                1: "EMU",
                2: "ESL",
                3: "ASIC"
            }
            if result in info_dict:
                return info_dict[result]
        return result

    def create_context(self, context_mode: str) -> ctypes.c_void_p:
        """
        Create a context and bind it with current thread

        Parameters
        ----------
        context_mode: str
            check runtime.rts_info for available context mode

        Returns
        -------
        None
        """
        c_context = ctypes.c_void_p()
        c_context_p = ctypes.c_void_p(ctypes.addressof(c_context))
        self.rtsdll.rtCtxCreate.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtCtxCreate(c_context_p,
                                           ctypes.c_uint32(rts_info.RT_CONTEXT_MODE[context_mode]),
                                           ctypes.c_int32(self.device_id))
        self.parse_error(rt_error, "rtCtxCreate")
        self.context = c_context
        self.context_storage.append(c_context)
        return c_context

    def destroy_context(self, c_context: ctypes.c_void_p = None) -> None:
        """
        Destroy context, if c_context is None will destroy self.context

        Parameters
        ----------
        c_context : ctypes.c_void_p, optional
            c_context which you want to destroy, can be None

        Returns
        -------
        None
        """
        self.rtsdll.rtCtxDestroy.restype = ctypes.c_uint64
        if c_context is None:
            if self.context not in self.context_storage:
                raise ValueError("Input context does not exist in current interface's context storage")
            rt_error = self.rtsdll.rtCtxDestroy(self.context)
        else:
            if c_context not in self.context_storage:
                raise ValueError("Input context does not exist in current interface's context storage")
            rt_error = self.rtsdll.rtCtxDestroy(c_context)
        self.parse_error(rt_error, "rtCtxDestroy")
        self.context = None

    def set_context(self, c_context: ctypes.c_void_p):
        """
        Bind context to current thread

        Parameters
        ----------
        c_context: ctypes.c_void_p
            context pointer

        Returns
        -------
        None
        """
        if c_context not in self.context_storage:
            raise ValueError("Input context does not exist in current interface's context storage")
        self.rtsdll.rtCtxSetCurrent.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtCtxSetCurrent(c_context)
        self.parse_error(rt_error, "rtCtxSetCurrent")
        self.context = c_context

    def create_stream(self, priority: int = 0) -> ctypes.c_void_p:
        """
        Create a new stream on current thread

        Parameters
        ----------
        priority: int, optional
            stream's priority

        Returns
        -------
        stream pointer: ctypes.c_void_p
        """
        c_stream = ctypes.c_void_p()
        c_stream_p = ctypes.c_void_p(ctypes.addressof(c_stream))
        self.rtsdll.rtStreamCreate.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtStreamCreate(c_stream_p, priority)
        self.parse_error(rt_error, "rtStreamCreate")
        return c_stream

    def destroy_stream(self, stream: ctypes.c_void_p):
        """
        destroy stream

        Parameters
        ----------
        stream: ctypes.c_void_p
            stream pointer

        Returns
        -------
        None
        """
        self.rtsdll.rtStreamDestroy.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtStreamDestroy(stream)
        self.parse_error(rt_error, "rtStreamDestroy")

    def register_device_binary_kernel(self, kernel_path: str, magic="RT_DEV_BINARY_MAGIC_ELF"):
        """
        Register device kernel on current thread

        Parameters
        ----------
        kernel_path: str
            path to device kernel binary
        magic: str
            kernel magic, see kernel.json after compile op

        Returns
        -------
        rts_binary_handle : a void pointer
        """
        if not magic:
            magic = "RT_DEV_BINARY_MAGIC_ELF"
        kernel = file_util.read_file(kernel_path)
        c_kernel_p = ctypes.c_char_p(kernel)
        rts_device_binary = rtDevBinary_t(data=c_kernel_p,
                                          length=ctypes.c_uint64(len(kernel)),
                                          version=ctypes.c_uint32(0),
                                          magic=ctypes.c_uint32(rts_info.MAGIC_MAP[magic]))
        rts_binary_handle = ctypes.c_void_p()
        self.rtsdll.rtDevBinaryRegister.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtDevBinaryRegister(ctypes.c_void_p(ctypes.addressof(rts_device_binary)),
                                                   ctypes.c_void_p(ctypes.addressof(rts_binary_handle)))
        self.parse_error(rt_error, "rtDevBinaryRegister")
        self.kernel_binary_storage[rts_binary_handle.value] = kernel
        return rts_binary_handle

    def unregister_device_binary_kernel(self, rts_binary_handle: ctypes.c_void_p):
        """
        UnRegister device kernel on current thread

        Parameters
        ----------
        rts_binary_handle: ctypes.c_void_p,
            binary handle pointer

        Returns
        -------
        None
        """
        self.rtsdll.rtDevBinaryUnRegister.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtDevBinaryUnRegister(rts_binary_handle)
        self.parse_error(rt_error, "rtDevBinaryUnRegister")
        del self.kernel_binary_storage[rts_binary_handle.value]
        if rts_binary_handle.value in self.kernel_name_storage:
            self.kernel_name_storage[rts_binary_handle.value].clear()
            del self.kernel_name_storage[rts_binary_handle.value]

    def register_function(self, rts_binary_handle: ctypes.c_void_p, kernel_name: str,
                          func_mode: int) -> ctypes.c_char_p:
        """
        Register function

        Parameters
        ----------
        rts_binary_handle:  ctypes.c_void_p
            rts_binary_handle pointer
        kernel_name: str
            kernel_name str
        func_mode: int
            function mode

        Returns
        -------
        function pointer
        """
        if rts_binary_handle.value not in self.kernel_name_storage:
            self.kernel_name_storage[rts_binary_handle.value] = []
        kernel_name_bytes = kernel_name.encode("UTF-8")
        c_kernel_name_p = ctypes.c_char_p(kernel_name_bytes)
        c_func_mode = ctypes.c_uint32(func_mode)
        self.rtsdll.rtFunctionRegister.restype = ctypes.c_uint64
        kernel_name_cache.append(c_kernel_name_p)
        rt_error = self.rtsdll.rtFunctionRegister(rts_binary_handle,
                                                  c_kernel_name_p,
                                                  c_kernel_name_p,
                                                  c_kernel_name_p,
                                                  c_func_mode)
        self.parse_error(rt_error, "rtFunctionRegister", ", kernel_name is: %s" % kernel_name)
        self.kernel_name_storage[rts_binary_handle.value].append(kernel_name_bytes)
        return c_kernel_name_p

    def copy_bin_file_to_hbm(self, bin_path: str) -> ctypes.c_void_p:
        """
        Copy bin file to hbm

        Parameters
        ----------
        bin_path: str
            path to bin file

        Returns
        -------
        hbm buffer pointer
        """
        data = file_util.read_file(bin_path, 34359738368)
        return self.copy_bin_to_hbm(data)

    def copy_bin_to_hbm(self, data: bytes) -> ctypes.c_void_p:
        """
        Copy bin data to hbm

        Parameters
        ----------
        data: bytes
            binary data

        Returns
        -------
        hbm buffer pointer

        """
        if not isinstance(data, bytes):
            raise TypeError("Copy binary to hbm supports bytes only, reveviced %s" % str(type(data)))

        try:
            c_memory_p = self.malloc(int(math.ceil(len(data) / 32) * 32 + 32), "RT_MEMORY_HBM")
        except BaseException as e:
            logger.log_err("rtMalloc on HBM failed, HBM memory info:  %s"
                           % str(self.get_memory_info_ex("RT_MEMORYINFO_HBM")))
            raise
        self.memcpy(c_memory_p, int(math.ceil(len(data) / 32) * 32 + 32), data, len(data), "RT_MEMCPY_HOST_TO_DEVICE")
        return c_memory_p

    def get_data_from_hbm(self,
                          c_memory_p: ctypes.c_void_p,
                          data_size: int):
        """
        Get data from hbm

        Parameters
        ----------
        c_memory_p: ctypes.c_void_p
            a void* which points to the hbm address you want to access
        data_size: int
            data size in bytes

        Returns
        -------
        data: bytes
            binary data
        pointer: ctypes.c_void_p
            hbm buffer pointer
        """
        if not isinstance(c_memory_p, ctypes.c_void_p):
            c_memory_p = ctypes.c_void_p(c_memory_p)
        c_buffer_p = self.host_malloc(data_size)
        self.memcpy(c_buffer_p,
                    data_size, c_memory_p, data_size,
                    "RT_MEMCPY_DEVICE_TO_HOST")
        if data_size > 8192:
            c_buffer = (ctypes.c_char * data_size).from_address(c_buffer_p.value)
        else:
            c_buffer = ctypes.string_at(c_buffer_p, data_size)
        return c_buffer, c_buffer_p

    # 'pylint: disable=unused-argument
    def memcpy(self, c_memory_p: ctypes.c_void_p, memory_size: int,
               data: Union[bytes, ctypes.c_void_p], data_size: int,
               memcpy_kind: str = "RT_MEMCPY_HOST_TO_HOST", retry_count: int = 0) -> None:
        """
        Do memory copy on Ascend

        Parameters
        ----------
        c_memory_p: ctypes.c_void_p
            copy data to this buffer pointer
        memory_size: int
            copy size
        data: Union[bytes, ctypes.c_void_p]
            which data need to copy, can be bytes data or a buffer pointer
        data_size: int
            data size
        memcpy_kind: str, optional
            memcpy_kind default is "RT_MEMCPY_HOST_TO_HOST", see rts_info.rt_memcpy_kind
        retry_count: int, optional
            retry count, don't set it, if failed will retry 3 times
        Returns
        -------

        """
        if isinstance(data, bytes):
            c_data_p = ctypes.c_char_p(data)
        elif isinstance(data, ctypes.c_void_p):
            c_data_p = data
        else:
            raise TypeError("Runtime function memcpy supports bytes or c_void_p only!")
        c_data_size = ctypes.c_uint64(data_size)
        c_memory_size = ctypes.c_uint64(memory_size)
        self.rtsdll.rtMemcpy.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtMemcpy(c_memory_p, c_memory_size,
                                        c_data_p, c_data_size,
                                        rts_info.RT_MEMCPY_KIND[memcpy_kind])
        try:
            self.parse_error(rt_error, "rtMemcpy")
        except RuntimeError as err:
            if retry_count < 3:
                retry_count += 1
                time.sleep(1)
                self.memcpy(c_memory_p, memory_size, data, data_size, memcpy_kind, retry_count)
            else:
                raise RuntimeError("After three retrys,memcpy still fails")

    def memset(self,
               c_memory_p: ctypes.c_void_p, memory_size: int,
               data: int, count: int):
        """
        Set memory value with uint32_t value

        Parameters
        ----------
        c_memory_p: ctypes.c_void_p
            a void* to the memory
        memory_size: int
            size of the memory
        data: int
            uint32_t value used to fill the memory
        count: int
            number of values you want to fill

        Returns
        -------
        None
        """
        if 0xFFFFFFFF < data < 0:
            raise RuntimeError("Invalid memset value, out of uint32_t range: %d" % data)
        c_data_size = ctypes.c_uint64(count)
        c_data = ctypes.c_uint32(data)
        c_memory_size = ctypes.c_uint64(memory_size)
        self.rtsdll.rtMemset.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtMemset(c_memory_p, c_memory_size,
                                        c_data, c_data_size)
        self.parse_error(rt_error, "rtMemset")

    def malloc(self,
               memory_size: int,
               memory_type: str = "RT_MEMORY_DEFAULT",
               memory_policy: str = "RT_MEMORY_POLICY_NONE") -> ctypes.c_void_p:
        """
        Malloc a buffer on device

        Parameters
        ----------
        memory_size: int
            memory size
        memory_type: str, optional
            memory type
        memory_policy: str, optional
            memory police

        Returns
        -------
        hbm buffer pointer
        """
        c_memory_p = ctypes.c_void_p()
        c_memory_size = ctypes.c_uint64(memory_size)
        self.rtsdll.rtMalloc.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtMalloc(ctypes.c_void_p(ctypes.addressof(c_memory_p)),
                                        c_memory_size,
                                        rts_info.RT_MEMORY_TYPE[memory_type]
                                        | rts_info.RT_MEMORY_POLICY[memory_policy])
        self.parse_error(rt_error, "rtMalloc", ", trying to allocate %d bytes" % memory_size)
        return c_memory_p

    def host_malloc(self, memory_size: int) -> ctypes.c_void_p:
        """
        Malloc a buffer on host

        Parameters
        ----------
        memory_size: int
            memory size


        Returns
        -------
        hbm buffer pointer
        """
        c_memory_p = ctypes.c_void_p()
        c_memory_size = ctypes.c_uint64(memory_size)
        self.rtsdll.rtMallocHost.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtMallocHost(ctypes.c_void_p(ctypes.addressof(c_memory_p)),
                                            c_memory_size)
        self.parse_error(rt_error, "rtMallocHost", ", try to  allocate %d bytes" % memory_size)
        return c_memory_p

    def free(self, c_memory_p: ctypes.c_void_p):
        """
        free
        """
        self.rtsdll.rtFree.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtFree(c_memory_p)
        self.parse_error(rt_error, "rtFree")

    def host_free(self, c_memory_p: ctypes.c_void_p):
        """
        host free
        """
        self.rtsdll.rtFreeHost.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtFreeHost(c_memory_p)
        self.parse_error(rt_error, "rtFreeHost")

    def launch_kernel(self,
                      stub_func: ctypes.c_void_p,
                      block_dim: int,
                      args: tuple, s_args: int,
                      sm_desc: ctypes.c_uint64, stream: ctypes.c_uint64) -> None:
        """
        launch kernel
        """
        c_block_dim = ctypes.c_uint32(block_dim)
        c_args = ctypes.c_uint64 * s_args
        c_args_p = c_args(*args)
        c_s_args = ctypes.c_uint32(s_args * 8)
        c_sm_dec = ctypes.c_void_p(sm_desc)
        self.rtsdll.rtKernelLaunch.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtKernelLaunch(stub_func,
                                              c_block_dim,
                                              ctypes.c_void_p(ctypes.addressof(c_args_p)),
                                              c_s_args,
                                              c_sm_dec,
                                              stream)
        self.parse_error(rt_error, "rtKernelLaunch")

    def synchronize_with_stream(self, stream: ctypes.c_uint64) -> None:
        """
        synchronize with stream
        """
        self.rtsdll.rtStreamSynchronize.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtStreamSynchronize(stream)
        self.parse_error(rt_error, "rtStreamSynchronize")

    def reset(self, device_id=None):
        """
        reset
        """
        if device_id is None:
            device_id = self.device_id
        self.rtsdll.rtDeviceReset.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtDeviceReset(ctypes.c_int32(device_id))
        self.parse_error(rt_error, "rtDeviceReset")
        self._clear_env()

    def start_online_profiling(self, stream: ctypes.c_uint64, profiling_count: int):
        """
        start online profiling
        """
        self.rtsdll.rtStartOnlineProf.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtStartOnlineProf(stream, ctypes.c_uint32(profiling_count))
        self.parse_error(rt_error, "rtStartOnlineProf")

    def stop_online_profiling(self, stream: ctypes.c_uint64):
        """
        stop online profiling
        """
        self.rtsdll.rtStopOnlineProf.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtStopOnlineProf(stream)
        self.parse_error(rt_error, "rtStopOnlineProf")

    def get_online_profiling_data(self, stream: ctypes.c_uint64, profiling_count: int):
        """
        get online profiling data
        """
        c_structs = (rtProfDataInfo_t * profiling_count)()
        c_structs_p = ctypes.cast(c_structs, ctypes.POINTER(rtProfDataInfo_t))
        c_profdata_id = ctypes.c_uint32(profiling_count)
        self.rtsdll.rtGetOnlineProfData.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtGetOnlineProfData(stream, c_structs_p, c_profdata_id)
        self.parse_error(rt_error, "rtGetOnlineProfData")
        return c_structs_p

    def _parse_error_code(self, error_type: int, error_code: int) -> str:
        if self.camodel:
            if error_code == 3:
                return "CAMODEL_NULL_CONTEXT"
        if error_code >= len(rts_info.RT_ERROR_CODE_DICT[error_type]):
            raise RuntimeError("Received invalid runtime error code: " + hex(0x07000000 + error_type + error_code))
        return rts_info.RT_ERROR_CODE_DICT[error_type][error_code]

    def parse_error(self, rt_error: ctypes.c_uint64, rt_api_name: str, extra_info: str = "") -> None:
        """
        parse error
        """
        if isinstance(rt_error, ctypes.c_uint64):
            rt_error = rt_error.value
        elif isinstance(rt_error, int):
            pass
        else:
            raise TypeError("Invalid rt_error type %s" % str(type(rt_error)))

        if rt_error == 0x00:
            logger.log_info("Runtime API call %s() success." % rt_api_name)
            return

        rt_error_magic = rt_error & 0xFF000000
        if rt_error_magic != 0x07000000 and not self.camodel:
            raise RuntimeError("Received invalid runtime error code:" + hex(rt_error) + extra_info)
        rt_error_type = rt_error & 0x00FF0000
        if rt_error_type not in rts_info.RT_ERROR_CODE_DICT and not self.camodel:
            raise RuntimeError("Received invalid runtime error type: " + hex(rt_error) + extra_info)
        rt_error_code = rt_error & 0x0000FFFF
        raise RuntimeError("Runtime API call " + "() failed:"
                           + self._parse_error_code(rt_error_type, rt_error_code) + extra_info)

    def get_memory_info_ex(self, memory_info_type: str):
        """
        get memory info ex
        """
        if memory_info_type not in rts_info.MEMORY_INFO_TYPE:
            raise RuntimeError("Invalid memory info type: %s" % memory_info_type)
        _free = (ctypes.c_size_t * 1)()
        _total = (ctypes.c_size_t * 1)()
        self.rtsdll.rtMemGetInfoEx.restype = ctypes.c_uint64
        rt_error = self.rtsdll.rtMemGetInfoEx(rts_info.MEMORY_INFO_TYPE[memory_info_type],
                                              _free,
                                              _total)
        self.parse_error(rt_error, "rtMemGetInfoEx")
        return _free[0], _total[0]
