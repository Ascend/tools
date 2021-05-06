# coding=utf-8
import os

# Dump config '0|5|10'
TF_DUMP_STEP = '0'

# path to run package operator cmp compare
# default may be /usr/local/Ascend/
CMD_ROOT_PATH = '/usr/local/'

# ASCEND Log Path
ASCEND_LOG_PATH = '/root/ascend/log/plog/'

# TOOL CONFIG
LOG_LEVEL = "NOTSET"
ROOT_DIR = './'


# Static dirs, do not change
DATA_ROOT_DIR = os.path.join(ROOT_DIR, 'precision_data')
# Fusion switch
FUSION_SWITCH_FILE = os.path.join(DATA_ROOT_DIR, 'fusion_switch.cfg')

# graph
GRAPH_DIR = os.path.join(DATA_ROOT_DIR, 'graph')
GRAPH_DIR_ALL = os.path.join(GRAPH_DIR, 'all')
GRAPH_DIR_BUILD = os.path.join(GRAPH_DIR, 'json')
GRAPH_CPU = os.path.join(GRAPH_DIR, 'cpu')
# fusion
FUSION_DIR = os.path.join(DATA_ROOT_DIR, 'fusion')

# dump
DUMP_DIR = os.path.join(DATA_ROOT_DIR, 'dump')
DUMP_FILES_NPU = os.path.join(DUMP_DIR, 'npu')
DUMP_FILES_OVERFLOW = os.path.join(DUMP_DIR, 'overflow')
DUMP_FILES_CPU_DEBUG = os.path.join(DUMP_DIR, 'cpu_debug')
DUMP_FILES_CPU = os.path.join(DUMP_DIR, 'cpu')

# dump temp dir
DUMP_TMP_DIR = os.path.join(DUMP_DIR, 'temp')
OP_GRAPH_DIR = os.path.join(DUMP_TMP_DIR, 'op_graph')
DUMP_FILES_OVERFLOW_DECODE = os.path.join(DUMP_TMP_DIR, 'overflow_decode')
DUMP_FILES_CPU_LOG = os.path.join(DUMP_TMP_DIR, 'cpu_tf_dump_log.txt')
DUMP_FILES_CPU_NAMES = os.path.join(DUMP_TMP_DIR, 'cpu_tf_tensor_names.txt')
DUMP_FILES_CPU_CMDS = os.path.join(DUMP_TMP_DIR, 'cpu_tf_tensor_cmd.txt')
DUMP_FILES_DECODE = os.path.join(DUMP_TMP_DIR, 'decode')
DUMP_FILES_CONVERT = os.path.join(DUMP_TMP_DIR, 'convert')
VECTOR_COMPARE_PATH = os.path.join(DUMP_TMP_DIR, 'vector_compare')

# FLAG
PRECISION_TOOL_OVERFLOW_FLAG = 'PRECISION_TOOL_OVERFLOW'
PRECISION_TOOL_DUMP_FLAG = 'PRECISION_TOOL_DUMP'

# DUMP CONFIG
OP_DEBUG_LEVEL = 1
DUMP_GE_GRAPH_VALUE = 2
DUMP_GRAPH_LEVEL_VALUE = 2

# TF_DEBUG
TF_DEBUG_TIMEOUT = 360

# MSACCUCMP
MS_ACCU_CMP = r'msaccucmp.py[c]?'
PYTHON = 'python3'
BUILD_JSON_GRAPH_NAME = 'PreRunAfterBuild'
