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
GRAPH_DIR = os.path.join(DATA_ROOT_DIR, 'graph')
GRAPH_DIR_ALL = os.path.join(DATA_ROOT_DIR, 'graph/all')
GRAPH_DIR_LAST = os.path.join(DATA_ROOT_DIR, 'graph/last')
GRAPH_DIR_BUILD = os.path.join(DATA_ROOT_DIR, 'graph/json')

FUSION_DIR = os.path.join(DATA_ROOT_DIR, 'fusion')

DUMP_FILES_NPU = os.path.join(DATA_ROOT_DIR, 'dump/npu')
DUMP_FILES_OVERFLOW = os.path.join(DATA_ROOT_DIR, 'dump/overflow')
DUMP_FILES_OVERFLOW_DECODE = os.path.join(DATA_ROOT_DIR, 'dump/overflow_decode')
DUMP_FILES_CPU = os.path.join(DATA_ROOT_DIR, 'dump/cpu')
DUMP_FILES_CPU_LOG = os.path.join(DATA_ROOT_DIR, 'dump/cpu_tf_dump_log.txt')
DUMP_FILES_CPU_NAMES = os.path.join(DATA_ROOT_DIR, 'dump/cpu_tf_tensor_names.txt')
DUMP_FILES_CPU_CMDS = os.path.join(DATA_ROOT_DIR, 'dump/cpu_tf_tensor_cmd.txt')
DUMP_FILES_DECODE = os.path.join(DATA_ROOT_DIR, 'dump/decode/')

VECTOR_COMPARE_PATH = os.path.join(DATA_ROOT_DIR, 'dump/vector/compare')
