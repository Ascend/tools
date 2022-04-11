#!/usr/bin/env python
# coding=utf-8
"""
Function:
DumpDataParser class. This class mainly involves the parser_dump_data function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os
import struct
from google.protobuf.message import DecodeError
import numpy as np
from ms_interface import utils
from ms_interface.constant import Constant
import ms_interface.dump_data_pb2 as DD


class DumpDataParser:
    """
    The class for dump data parser
    """
    DATA_TYPE_TO_DTYPE_MAP = {
        DD.DT_FLOAT: {Constant.DTYPE: np.float32, Constant.STRUCT_FORMAT_KEY: 'f'},
        DD.DT_FLOAT16: {Constant.DTYPE: np.float16, Constant.STRUCT_FORMAT_KEY: 'e'},
        DD.DT_DOUBLE: {Constant.DTYPE: np.float64, Constant.STRUCT_FORMAT_KEY: 'd'},
        DD.DT_INT8: {Constant.DTYPE: np.int8, Constant.STRUCT_FORMAT_KEY: 'b'},
        DD.DT_INT16: {Constant.DTYPE: np.int16, Constant.STRUCT_FORMAT_KEY: 'h'},
        DD.DT_INT32: {Constant.DTYPE: np.int32, Constant.STRUCT_FORMAT_KEY: 'i'},
        DD.DT_INT64: {Constant.DTYPE: np.int64, Constant.STRUCT_FORMAT_KEY: 'q'},
        DD.DT_UINT8: {Constant.DTYPE: np.uint8, Constant.STRUCT_FORMAT_KEY: 'B'},
        DD.DT_UINT16: {Constant.DTYPE: np.uint16, Constant.STRUCT_FORMAT_KEY: 'H'},
        DD.DT_UINT32: {Constant.DTYPE: np.uint32, Constant.STRUCT_FORMAT_KEY: 'I'},
        DD.DT_UINT64: {Constant.DTYPE: np.uint64, Constant.STRUCT_FORMAT_KEY: 'Q'},
        DD.DT_BOOL: {Constant.DTYPE: np.bool_, Constant.STRUCT_FORMAT_KEY: '?'},
    }

    def __init__(self: any, input_path: str, op_name: str, kernel_name="") -> None:
        self.input_path = input_path
        self.op_name = op_name
        self.kernel_name = kernel_name

    # @staticmethod
    def _parse_dump_file(self: any, dump_file: str) -> any:
        """
        Parse the dump file path by big dump data format
        :param: dump_file the dump file
        :return: DumpData
        :exception when read or parse file error
        """
        utils.check_path_valid(dump_file)
        try:
            # get file size
            file_size = os.path.getsize(dump_file)
            # check file size > 8
            if file_size <= Constant.UINT64_SIZE:
                utils.print_error_log('The size of %s is at least greater then %d, but the file'
                                      ' size is %d. Please check the dump file.'
                                      % (dump_file, Constant.UINT64_SIZE, file_size))
                raise utils.AicErrException(
                    Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)
            with open(dump_file, 'rb') as dump_data_file:
                # read header length
                header_length = dump_data_file.read(Constant.UINT64_SIZE)
                header_length = struct.unpack(Constant.UINT64_FMT, header_length)[0]
                # check header_length <= file_size - 8
                if header_length > file_size - Constant.UINT64_SIZE:
                    utils.print_error_log(
                        'The header content size(%d) of %s must be less then '
                        'or equal to %d(file size) - %d(header length).'
                        ' Please check the dump file.'
                        % (header_length, dump_file, file_size,
                           Constant.UINT64_SIZE))
                    raise utils.AicErrException(
                        Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)
                # read header content
                return self._get_dump_data(dump_data_file, header_length, file_size)
        except IOError as io_error:
            utils.print_error_log('Failed to read the dump file %s. %s'
                                  % (dump_file, str(io_error)))
            raise utils.AicErrException(Constant.MS_AICERR_OPEN_FILE_ERROR)
        finally:
            pass

    @staticmethod
    def _check_dump_data_vaild(dump_data: any, dump_file: str, header_length: int, file_size: int) -> None:
        input_data_size = 0
        for item in dump_data.input:
            input_data_size += item.size
        output_data_size = 0
        for item in dump_data.output:
            output_data_size += item.size
        buffer_data_size = 0
        for item in dump_data.buffer:
            buffer_data_size += item.size
        # check 8 + content size + sum(input.data) + sum(output.data)
        # + sum(buffer.data) equal to file size
        if header_length + Constant.UINT64_SIZE + input_data_size \
                + output_data_size + buffer_data_size != file_size:
            utils.print_error_log(
                'The file size(%d) of %s is not equal to %d(header '
                'length) + %d(the size of header content) + %d(the sum'
                ' of input data) + %d(the sum of output data) + %d(the'
                ' sum of buffer data). Please check the dump file.'
                % (file_size, dump_file, Constant.UINT64_SIZE,
                   header_length, input_data_size, output_data_size,
                   buffer_data_size))
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)

    def _get_dump_data(self: any, dump_file: any, header_length: int, file_size: int) -> any:
        # read header content
        content = dump_file.read(header_length)
        dump_data = DD.DumpData()
        try:
            dump_data.ParseFromString(content)
        except DecodeError as de_error:
            utils.print_error_log('Failed to parse the serialized header content of %s. '
                                  'Please check the dump file. %s '
                                  % (dump_file, str(de_error)))
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)
        finally:
            pass
        self._check_dump_data_vaild(dump_data, dump_file, header_length, file_size)
        if len(dump_data.input) > 0:
            for (index, _) in enumerate(dump_data.input):
                dump_data.input[index].data = dump_file.read(
                    dump_data.input[index].size)
        if len(dump_data.output) > 0:
            for (index, _) in enumerate(dump_data.output):
                dump_data.output[index].data = dump_file.read(
                    dump_data.output[index].size)
        if len(dump_data.buffer) > 0:
            for (index, _) in enumerate(dump_data.buffer):
                dump_data.buffer[index].data = dump_file.read(
                    dump_data.buffer[index].size)
        return dump_data

    def check_arguments_valid(self: any) -> None:
        """
        Function Description: check arguments valid
        """
        utils.check_path_valid(self.input_path, isdir=True)

    def _get_dtype_by_data_type(self: any, data_type: any) -> any:
        if data_type not in self.DATA_TYPE_TO_DTYPE_MAP:
            utils.print_error_log("The output data type(%s) does not support." % data_type)
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)
        return self.DATA_TYPE_TO_DTYPE_MAP.get(data_type).get(Constant.DTYPE)

    def _save_tensor_to_file(self: any, tensor_list: list, tensor_type: str, dump_file: str) -> str:
        result_info = ''
        if len(tensor_list) == 0:
            utils.print_warn_log(
                'There is no %s in "%s".' % (tensor_type, dump_file))
            return result_info
        dump_file_path, _ = os.path.split(dump_file)
        for (index, tensor) in enumerate(tensor_list):
            try:
                array = np.frombuffer(tensor.data,
                                      dtype=self._get_dtype_by_data_type(
                                          tensor.data_type))
                npy_file_name = ".".join([self.kernel_name, tensor_type, str(index), "npy"])
                np.save(os.path.join(dump_file_path, npy_file_name), array)
                if (np.isinf(array).any() or np.isnan(array).any()) and tensor_type == "input":
                    result_info += '%s[%d] NaN/INF\n' % (tensor_type, index)
                    utils.print_error_log('%s[%d] NaN/INF\n' % (tensor_type, index))
                    raise utils.AicErrException(
                        Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)
            except (ValueError, IOError, OSError, MemoryError) as error:
                utils.print_error_log('Failed to parse the data of %s:%d of "%s". %s' % (
                    tensor_type, index, dump_file, error))
                raise utils.AicErrException(
                    Constant.MS_AICERR_INVALID_DUMP_DATA_ERROR)
            finally:
                pass

        return result_info

    def parse_dump_data(self: any, dump_file: str) -> str:
        """
        Function Description: convert dump data to numpy and bin file
        @param dump_file: the dump file
        """
        dump_data = self._parse_dump_file(dump_file)
        # 2. parse dump data
        result_info = self._save_tensor_to_file(dump_data.input, 'input',
                                                dump_file)
        result_info += self._save_tensor_to_file(dump_data.output, 'output',
                                                 dump_file)
        return result_info

    def parse(self: any) -> str:
        """
        Function Description: dump data parse.
        """
        # 1. check arguments valid
        self.check_arguments_valid()
        match_name = "".join(['.', self.op_name.replace('/', '_'), '.'])
        match_dump_list = []
        for top, _, files in os.walk(self.input_path):
            for name in files:
                if match_name in name:
                    match_dump_list.append(os.path.join(top, name))
        result_info_list = []
        for dump_file in match_dump_list:
            result_info_list.extend(['%s\n' % dump_file,
                                     self.parse_dump_data(dump_file)])
        result_info = "".join(result_info_list)
        if len(match_dump_list) == 0:
            utils.print_warn_log('There is no dump file for "%s". Please '
                                 'check the dump path.' % self.op_name)
        utils.print_info_log(f"Parse dump file finished,result_info:{result_info}")
        return result_info
