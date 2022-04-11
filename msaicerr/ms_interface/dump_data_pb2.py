# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dump_data.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='dump_data.proto',
  package='toolkit.dumpdata',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0f\x64ump_data.proto\x12\x10toolkit.dumpdata\"\x95\x01\n\nOriginalOp\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0coutput_index\x18\x02 \x01(\r\x12\x33\n\tdata_type\x18\x03 \x01(\x0e\x32 .toolkit.dumpdata.OutputDataType\x12.\n\x06\x66ormat\x18\x04 \x01(\x0e\x32\x1e.toolkit.dumpdata.OutputFormat\"\x14\n\x05Shape\x12\x0b\n\x03\x64im\x18\x01 \x03(\x04\"\xab\x02\n\x08OpOutput\x12\x33\n\tdata_type\x18\x01 \x01(\x0e\x32 .toolkit.dumpdata.OutputDataType\x12.\n\x06\x66ormat\x18\x02 \x01(\x0e\x32\x1e.toolkit.dumpdata.OutputFormat\x12&\n\x05shape\x18\x03 \x01(\x0b\x32\x17.toolkit.dumpdata.Shape\x12\x31\n\x0boriginal_op\x18\x04 \x01(\x0b\x32\x1c.toolkit.dumpdata.OriginalOp\x12\x0c\n\x04\x64\x61ta\x18\x05 \x01(\x0c\x12\x0c\n\x04size\x18\x06 \x01(\x04\x12/\n\x0eoriginal_shape\x18\x07 \x01(\x0b\x32\x17.toolkit.dumpdata.Shape\x12\x12\n\nsub_format\x18\x08 \x01(\x05\"\xf7\x01\n\x07OpInput\x12\x33\n\tdata_type\x18\x01 \x01(\x0e\x32 .toolkit.dumpdata.OutputDataType\x12.\n\x06\x66ormat\x18\x02 \x01(\x0e\x32\x1e.toolkit.dumpdata.OutputFormat\x12&\n\x05shape\x18\x03 \x01(\x0b\x32\x17.toolkit.dumpdata.Shape\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\x12\x0c\n\x04size\x18\x05 \x01(\x04\x12/\n\x0eoriginal_shape\x18\x06 \x01(\x0b\x32\x17.toolkit.dumpdata.Shape\x12\x12\n\nsub_format\x18\x07 \x01(\x05\"Y\n\x08OpBuffer\x12\x31\n\x0b\x62uffer_type\x18\x01 \x01(\x0e\x32\x1c.toolkit.dumpdata.BufferType\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12\x0c\n\x04size\x18\x03 \x01(\x04\"\xc1\x01\n\x08\x44umpData\x12\x0f\n\x07version\x18\x01 \x01(\t\x12\x11\n\tdump_time\x18\x02 \x01(\x04\x12*\n\x06output\x18\x03 \x03(\x0b\x32\x1a.toolkit.dumpdata.OpOutput\x12(\n\x05input\x18\x04 \x03(\x0b\x32\x19.toolkit.dumpdata.OpInput\x12*\n\x06\x62uffer\x18\x05 \x03(\x0b\x32\x1a.toolkit.dumpdata.OpBuffer\x12\x0f\n\x07op_name\x18\x06 \x01(\t*\xab\x03\n\x0eOutputDataType\x12\x10\n\x0c\x44T_UNDEFINED\x10\x00\x12\x0c\n\x08\x44T_FLOAT\x10\x01\x12\x0e\n\nDT_FLOAT16\x10\x02\x12\x0b\n\x07\x44T_INT8\x10\x03\x12\x0c\n\x08\x44T_UINT8\x10\x04\x12\x0c\n\x08\x44T_INT16\x10\x05\x12\r\n\tDT_UINT16\x10\x06\x12\x0c\n\x08\x44T_INT32\x10\x07\x12\x0c\n\x08\x44T_INT64\x10\x08\x12\r\n\tDT_UINT32\x10\t\x12\r\n\tDT_UINT64\x10\n\x12\x0b\n\x07\x44T_BOOL\x10\x0b\x12\r\n\tDT_DOUBLE\x10\x0c\x12\r\n\tDT_STRING\x10\r\x12\x14\n\x10\x44T_DUAL_SUB_INT8\x10\x0e\x12\x15\n\x11\x44T_DUAL_SUB_UINT8\x10\x0f\x12\x10\n\x0c\x44T_COMPLEX64\x10\x10\x12\x11\n\rDT_COMPLEX128\x10\x11\x12\x0c\n\x08\x44T_QINT8\x10\x12\x12\r\n\tDT_QINT16\x10\x13\x12\r\n\tDT_QINT32\x10\x14\x12\r\n\tDT_QUINT8\x10\x15\x12\x0e\n\nDT_QUINT16\x10\x16\x12\x0f\n\x0b\x44T_RESOURCE\x10\x17\x12\x11\n\rDT_STRING_REF\x10\x18\x12\x0b\n\x07\x44T_DUAL\x10\x19*\x82\x08\n\x0cOutputFormat\x12\x0f\n\x0b\x46ORMAT_NCHW\x10\x00\x12\x0f\n\x0b\x46ORMAT_NHWC\x10\x01\x12\r\n\tFORMAT_ND\x10\x02\x12\x12\n\x0e\x46ORMAT_NC1HWC0\x10\x03\x12\x14\n\x10\x46ORMAT_FRACTAL_Z\x10\x04\x12\x15\n\x11\x46ORMAT_NC1C0HWPAD\x10\x05\x12\x12\n\x0e\x46ORMAT_NHWC1C0\x10\x06\x12\x13\n\x0f\x46ORMAT_FSR_NCHW\x10\x07\x12\x19\n\x15\x46ORMAT_FRACTAL_DECONV\x10\x08\x12\x12\n\x0e\x46ORMAT_C1HWNC0\x10\t\x12#\n\x1f\x46ORMAT_FRACTAL_DECONV_TRANSPOSE\x10\n\x12)\n%FORMAT_FRACTAL_DECONV_SP_STRIDE_TRANS\x10\x0b\x12\x16\n\x12\x46ORMAT_NC1HWC0_C04\x10\x0c\x12\x18\n\x14\x46ORMAT_FRACTAL_Z_C04\x10\r\x12\x0f\n\x0b\x46ORMAT_CHWN\x10\x0e\x12*\n&FORMAT_FRACTAL_DECONV_SP_STRIDE8_TRANS\x10\x0f\x12\x0f\n\x0b\x46ORMAT_HWCN\x10\x10\x12\x16\n\x12\x46ORMAT_NC1KHKWHWC0\x10\x11\x12\x14\n\x10\x46ORMAT_BN_WEIGHT\x10\x12\x12\x16\n\x12\x46ORMAT_FILTER_HWCK\x10\x13\x12#\n\x1f\x46ORMAT_HASHTABLE_LOOKUP_LOOKUPS\x10\x14\x12 \n\x1c\x46ORMAT_HASHTABLE_LOOKUP_KEYS\x10\x15\x12!\n\x1d\x46ORMAT_HASHTABLE_LOOKUP_VALUE\x10\x16\x12\"\n\x1e\x46ORMAT_HASHTABLE_LOOKUP_OUTPUT\x10\x17\x12 \n\x1c\x46ORMAT_HASHTABLE_LOOKUP_HITS\x10\x18\x12\x14\n\x10\x46ORMAT_C1HWNCoC0\x10\x19\x12\r\n\tFORMAT_MD\x10\x1a\x12\x10\n\x0c\x46ORMAT_NDHWC\x10\x1b\x12\x15\n\x11\x46ORMAT_FRACTAL_ZZ\x10\x1c\x12\x15\n\x11\x46ORMAT_FRACTAL_NZ\x10\x1d\x12\x10\n\x0c\x46ORMAT_NCDHW\x10\x1e\x12\x10\n\x0c\x46ORMAT_DHWCN\x10\x1f\x12\x13\n\x0f\x46ORMAT_NDC1HWC0\x10 \x12\x17\n\x13\x46ORMAT_FRACTAL_Z_3D\x10!\x12\r\n\tFORMAT_CN\x10\"\x12\r\n\tFORMAT_NC\x10#\x12\x10\n\x0c\x46ORMAT_DHWNC\x10$\x12!\n\x1d\x46ORMAT_FRACTAL_Z_3D_TRANSPOSE\x10%\x12\x1a\n\x16\x46ORMAT_FRACTAL_ZN_LSTM\x10&\x12\x16\n\x12\x46ORMAT_FRACTAL_Z_G\x10\'\x12\x13\n\x0f\x46ORMAT_RESERVED\x10(\x12\x0f\n\nFORMAT_MAX\x10\xff\x01*\x14\n\nBufferType\x12\x06\n\x02L1\x10\x00\x62\x06proto3'
)

_OUTPUTDATATYPE = _descriptor.EnumDescriptor(
  name='OutputDataType',
  full_name='toolkit.dumpdata.OutputDataType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DT_UNDEFINED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_FLOAT', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_FLOAT16', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_INT8', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_UINT8', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_INT16', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_UINT16', index=6, number=6,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_INT32', index=7, number=7,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_INT64', index=8, number=8,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_UINT32', index=9, number=9,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_UINT64', index=10, number=10,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_BOOL', index=11, number=11,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_DOUBLE', index=12, number=12,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_STRING', index=13, number=13,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_DUAL_SUB_INT8', index=14, number=14,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_DUAL_SUB_UINT8', index=15, number=15,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_COMPLEX64', index=16, number=16,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_COMPLEX128', index=17, number=17,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_QINT8', index=18, number=18,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_QINT16', index=19, number=19,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_QINT32', index=20, number=20,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_QUINT8', index=21, number=21,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_QUINT16', index=22, number=22,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_RESOURCE', index=23, number=23,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_STRING_REF', index=24, number=24,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DT_DUAL', index=25, number=25,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1051,
  serialized_end=1478,
)
_sym_db.RegisterEnumDescriptor(_OUTPUTDATATYPE)

OutputDataType = enum_type_wrapper.EnumTypeWrapper(_OUTPUTDATATYPE)
_OUTPUTFORMAT = _descriptor.EnumDescriptor(
  name='OutputFormat',
  full_name='toolkit.dumpdata.OutputFormat',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NCHW', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NHWC', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_ND', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NC1HWC0', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_Z', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NC1C0HWPAD', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NHWC1C0', index=6, number=6,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FSR_NCHW', index=7, number=7,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_DECONV', index=8, number=8,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_C1HWNC0', index=9, number=9,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_DECONV_TRANSPOSE', index=10, number=10,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_DECONV_SP_STRIDE_TRANS', index=11, number=11,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NC1HWC0_C04', index=12, number=12,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_Z_C04', index=13, number=13,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_CHWN', index=14, number=14,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_DECONV_SP_STRIDE8_TRANS', index=15, number=15,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_HWCN', index=16, number=16,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NC1KHKWHWC0', index=17, number=17,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_BN_WEIGHT', index=18, number=18,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FILTER_HWCK', index=19, number=19,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_HASHTABLE_LOOKUP_LOOKUPS', index=20, number=20,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_HASHTABLE_LOOKUP_KEYS', index=21, number=21,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_HASHTABLE_LOOKUP_VALUE', index=22, number=22,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_HASHTABLE_LOOKUP_OUTPUT', index=23, number=23,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_HASHTABLE_LOOKUP_HITS', index=24, number=24,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_C1HWNCoC0', index=25, number=25,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_MD', index=26, number=26,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NDHWC', index=27, number=27,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_ZZ', index=28, number=28,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_NZ', index=29, number=29,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NCDHW', index=30, number=30,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_DHWCN', index=31, number=31,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NDC1HWC0', index=32, number=32,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_Z_3D', index=33, number=33,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_CN', index=34, number=34,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_NC', index=35, number=35,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_DHWNC', index=36, number=36,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_Z_3D_TRANSPOSE', index=37, number=37,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_ZN_LSTM', index=38, number=38,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_FRACTAL_Z_G', index=39, number=39,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_RESERVED', index=40, number=40,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FORMAT_MAX', index=41, number=255,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1481,
  serialized_end=2507,
)
_sym_db.RegisterEnumDescriptor(_OUTPUTFORMAT)

OutputFormat = enum_type_wrapper.EnumTypeWrapper(_OUTPUTFORMAT)
_BUFFERTYPE = _descriptor.EnumDescriptor(
  name='BufferType',
  full_name='toolkit.dumpdata.BufferType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='L1', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=2509,
  serialized_end=2529,
)
_sym_db.RegisterEnumDescriptor(_BUFFERTYPE)

BufferType = enum_type_wrapper.EnumTypeWrapper(_BUFFERTYPE)
DT_UNDEFINED = 0
DT_FLOAT = 1
DT_FLOAT16 = 2
DT_INT8 = 3
DT_UINT8 = 4
DT_INT16 = 5
DT_UINT16 = 6
DT_INT32 = 7
DT_INT64 = 8
DT_UINT32 = 9
DT_UINT64 = 10
DT_BOOL = 11
DT_DOUBLE = 12
DT_STRING = 13
DT_DUAL_SUB_INT8 = 14
DT_DUAL_SUB_UINT8 = 15
DT_COMPLEX64 = 16
DT_COMPLEX128 = 17
DT_QINT8 = 18
DT_QINT16 = 19
DT_QINT32 = 20
DT_QUINT8 = 21
DT_QUINT16 = 22
DT_RESOURCE = 23
DT_STRING_REF = 24
DT_DUAL = 25
FORMAT_NCHW = 0
FORMAT_NHWC = 1
FORMAT_ND = 2
FORMAT_NC1HWC0 = 3
FORMAT_FRACTAL_Z = 4
FORMAT_NC1C0HWPAD = 5
FORMAT_NHWC1C0 = 6
FORMAT_FSR_NCHW = 7
FORMAT_FRACTAL_DECONV = 8
FORMAT_C1HWNC0 = 9
FORMAT_FRACTAL_DECONV_TRANSPOSE = 10
FORMAT_FRACTAL_DECONV_SP_STRIDE_TRANS = 11
FORMAT_NC1HWC0_C04 = 12
FORMAT_FRACTAL_Z_C04 = 13
FORMAT_CHWN = 14
FORMAT_FRACTAL_DECONV_SP_STRIDE8_TRANS = 15
FORMAT_HWCN = 16
FORMAT_NC1KHKWHWC0 = 17
FORMAT_BN_WEIGHT = 18
FORMAT_FILTER_HWCK = 19
FORMAT_HASHTABLE_LOOKUP_LOOKUPS = 20
FORMAT_HASHTABLE_LOOKUP_KEYS = 21
FORMAT_HASHTABLE_LOOKUP_VALUE = 22
FORMAT_HASHTABLE_LOOKUP_OUTPUT = 23
FORMAT_HASHTABLE_LOOKUP_HITS = 24
FORMAT_C1HWNCoC0 = 25
FORMAT_MD = 26
FORMAT_NDHWC = 27
FORMAT_FRACTAL_ZZ = 28
FORMAT_FRACTAL_NZ = 29
FORMAT_NCDHW = 30
FORMAT_DHWCN = 31
FORMAT_NDC1HWC0 = 32
FORMAT_FRACTAL_Z_3D = 33
FORMAT_CN = 34
FORMAT_NC = 35
FORMAT_DHWNC = 36
FORMAT_FRACTAL_Z_3D_TRANSPOSE = 37
FORMAT_FRACTAL_ZN_LSTM = 38
FORMAT_FRACTAL_Z_G = 39
FORMAT_RESERVED = 40
FORMAT_MAX = 255
L1 = 0



_ORIGINALOP = _descriptor.Descriptor(
  name='OriginalOp',
  full_name='toolkit.dumpdata.OriginalOp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='toolkit.dumpdata.OriginalOp.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='output_index', full_name='toolkit.dumpdata.OriginalOp.output_index', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data_type', full_name='toolkit.dumpdata.OriginalOp.data_type', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='format', full_name='toolkit.dumpdata.OriginalOp.format', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=38,
  serialized_end=187,
)


_SHAPE = _descriptor.Descriptor(
  name='Shape',
  full_name='toolkit.dumpdata.Shape',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='dim', full_name='toolkit.dumpdata.Shape.dim', index=0,
      number=1, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=189,
  serialized_end=209,
)


_OPOUTPUT = _descriptor.Descriptor(
  name='OpOutput',
  full_name='toolkit.dumpdata.OpOutput',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='data_type', full_name='toolkit.dumpdata.OpOutput.data_type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='format', full_name='toolkit.dumpdata.OpOutput.format', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='shape', full_name='toolkit.dumpdata.OpOutput.shape', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='original_op', full_name='toolkit.dumpdata.OpOutput.original_op', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='toolkit.dumpdata.OpOutput.data', index=4,
      number=5, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='size', full_name='toolkit.dumpdata.OpOutput.size', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='original_shape', full_name='toolkit.dumpdata.OpOutput.original_shape', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='sub_format', full_name='toolkit.dumpdata.OpOutput.sub_format', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=212,
  serialized_end=511,
)


_OPINPUT = _descriptor.Descriptor(
  name='OpInput',
  full_name='toolkit.dumpdata.OpInput',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='data_type', full_name='toolkit.dumpdata.OpInput.data_type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='format', full_name='toolkit.dumpdata.OpInput.format', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='shape', full_name='toolkit.dumpdata.OpInput.shape', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='toolkit.dumpdata.OpInput.data', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='size', full_name='toolkit.dumpdata.OpInput.size', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='original_shape', full_name='toolkit.dumpdata.OpInput.original_shape', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='sub_format', full_name='toolkit.dumpdata.OpInput.sub_format', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=514,
  serialized_end=761,
)


_OPBUFFER = _descriptor.Descriptor(
  name='OpBuffer',
  full_name='toolkit.dumpdata.OpBuffer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='buffer_type', full_name='toolkit.dumpdata.OpBuffer.buffer_type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='toolkit.dumpdata.OpBuffer.data', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='size', full_name='toolkit.dumpdata.OpBuffer.size', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=763,
  serialized_end=852,
)


_DUMPDATA = _descriptor.Descriptor(
  name='DumpData',
  full_name='toolkit.dumpdata.DumpData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='version', full_name='toolkit.dumpdata.DumpData.version', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dump_time', full_name='toolkit.dumpdata.DumpData.dump_time', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='output', full_name='toolkit.dumpdata.DumpData.output', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='input', full_name='toolkit.dumpdata.DumpData.input', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='buffer', full_name='toolkit.dumpdata.DumpData.buffer', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='op_name', full_name='toolkit.dumpdata.DumpData.op_name', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=855,
  serialized_end=1048,
)

_ORIGINALOP.fields_by_name['data_type'].enum_type = _OUTPUTDATATYPE
_ORIGINALOP.fields_by_name['format'].enum_type = _OUTPUTFORMAT
_OPOUTPUT.fields_by_name['data_type'].enum_type = _OUTPUTDATATYPE
_OPOUTPUT.fields_by_name['format'].enum_type = _OUTPUTFORMAT
_OPOUTPUT.fields_by_name['shape'].message_type = _SHAPE
_OPOUTPUT.fields_by_name['original_op'].message_type = _ORIGINALOP
_OPOUTPUT.fields_by_name['original_shape'].message_type = _SHAPE
_OPINPUT.fields_by_name['data_type'].enum_type = _OUTPUTDATATYPE
_OPINPUT.fields_by_name['format'].enum_type = _OUTPUTFORMAT
_OPINPUT.fields_by_name['shape'].message_type = _SHAPE
_OPINPUT.fields_by_name['original_shape'].message_type = _SHAPE
_OPBUFFER.fields_by_name['buffer_type'].enum_type = _BUFFERTYPE
_DUMPDATA.fields_by_name['output'].message_type = _OPOUTPUT
_DUMPDATA.fields_by_name['input'].message_type = _OPINPUT
_DUMPDATA.fields_by_name['buffer'].message_type = _OPBUFFER
DESCRIPTOR.message_types_by_name['OriginalOp'] = _ORIGINALOP
DESCRIPTOR.message_types_by_name['Shape'] = _SHAPE
DESCRIPTOR.message_types_by_name['OpOutput'] = _OPOUTPUT
DESCRIPTOR.message_types_by_name['OpInput'] = _OPINPUT
DESCRIPTOR.message_types_by_name['OpBuffer'] = _OPBUFFER
DESCRIPTOR.message_types_by_name['DumpData'] = _DUMPDATA
DESCRIPTOR.enum_types_by_name['OutputDataType'] = _OUTPUTDATATYPE
DESCRIPTOR.enum_types_by_name['OutputFormat'] = _OUTPUTFORMAT
DESCRIPTOR.enum_types_by_name['BufferType'] = _BUFFERTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

OriginalOp = _reflection.GeneratedProtocolMessageType('OriginalOp', (_message.Message,), {
  'DESCRIPTOR' : _ORIGINALOP,
  '__module__' : 'dump_data_pb2'
  # @@protoc_insertion_point(class_scope:toolkit.dumpdata.OriginalOp)
  })
_sym_db.RegisterMessage(OriginalOp)

Shape = _reflection.GeneratedProtocolMessageType('Shape', (_message.Message,), {
  'DESCRIPTOR' : _SHAPE,
  '__module__' : 'dump_data_pb2'
  # @@protoc_insertion_point(class_scope:toolkit.dumpdata.Shape)
  })
_sym_db.RegisterMessage(Shape)

OpOutput = _reflection.GeneratedProtocolMessageType('OpOutput', (_message.Message,), {
  'DESCRIPTOR' : _OPOUTPUT,
  '__module__' : 'dump_data_pb2'
  # @@protoc_insertion_point(class_scope:toolkit.dumpdata.OpOutput)
  })
_sym_db.RegisterMessage(OpOutput)

OpInput = _reflection.GeneratedProtocolMessageType('OpInput', (_message.Message,), {
  'DESCRIPTOR' : _OPINPUT,
  '__module__' : 'dump_data_pb2'
  # @@protoc_insertion_point(class_scope:toolkit.dumpdata.OpInput)
  })
_sym_db.RegisterMessage(OpInput)

OpBuffer = _reflection.GeneratedProtocolMessageType('OpBuffer', (_message.Message,), {
  'DESCRIPTOR' : _OPBUFFER,
  '__module__' : 'dump_data_pb2'
  # @@protoc_insertion_point(class_scope:toolkit.dumpdata.OpBuffer)
  })
_sym_db.RegisterMessage(OpBuffer)

DumpData = _reflection.GeneratedProtocolMessageType('DumpData', (_message.Message,), {
  'DESCRIPTOR' : _DUMPDATA,
  '__module__' : 'dump_data_pb2'
  # @@protoc_insertion_point(class_scope:toolkit.dumpdata.DumpData)
  })
_sym_db.RegisterMessage(DumpData)


# @@protoc_insertion_point(module_scope)
