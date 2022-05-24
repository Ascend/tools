# coding=utf-8


class Constant(object):
    VERSION = "0.1.1"
    NEW_LINE = "\n"
    TAB_LINE = "\t"
    DEFAULT_DEBUG_ID = "debug_0"
    NPU_DEBUG_ID_1 = "debug_1"
    GRAPH = "graph"
    DUMP = "dump"

    class Suffix(object):
        JSON = '.json'
        CSV = '.csv'
        H5 = '.h5'

    class Pattern(object):
        GE_PROTO_GRAPH_PATTERN = r'^ge_proto_([0-9]+)_([A-Za-z0-9_-]+)\.txt$'

