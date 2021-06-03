# coding=utf-8
"""
Graph Manager
"""
import json
import os
import collections
import time
import config as cfg
from lib.tf_graph import TfGraph
from lib.op import Op
from lib.constant import Constant
from lib.npu_graph import NpuGraph
from lib.tf_graph import TfGraph
from lib.util import util
from lib.precision_tool_exception import catch_tool_exception
from lib.precision_tool_exception import PrecisionToolException


class GraphManager(object):
    def __init__(self):
        self.log = util.get_log()
        self.npu_graphs = collections.OrderedDict()
        self.tf_graph = None

    def prepare(self):
        # prepare npu graphs
        if not os.path.exists(cfg.NPU_DIR):
            util.create_dir(cfg.NPU_DIR)
        sub_dirs = os.listdir(cfg.NPU_DIR)
        if len(sub_dirs) == 0:
            # create default dir
            sub_dirs = [Constant.DEFAULT_DEBUG_ID]
        for sub_dir in sub_dirs:
            npu_graph = NpuGraph(sub_dir)
            npu_graph.prepare()
            self.npu_graphs[sub_dir] = npu_graph
        # prepare cpu graph
        self.tf_graph = TfGraph(cfg.TF_GRAPH_DIR)

    def check_cast(self):
        for graph in self.npu_graphs.values():
            graph.check_cast()

    def check_dtype(self):
        for graph in self.npu_graphs.values():
            graph.check_dtype()

    def check_similarity(self):
        return

    def get_graphs(self, debug_id):
        if debug_id not in self.npu_graphs:
            raise PrecisionToolException("Get graphs failed with no debug_id:%s" % debug_id)
        return self.npu_graphs[debug_id].build_json_files

    def get_ops(self, op_name):
        """ Get npu/tf ops by op_name
        :param op_name:
        :return: npu op dict: debug_id->Op, tf op
        """
        npu_ops = collections.OrderedDict()
        for debug_id, npu_graph in self.npu_graphs.items():
            npu_ops[debug_id] = npu_graph.get_op(op_name)
        # tf graph op
        return npu_ops, None

    def print_op_list(self, op_type='', op_name='', pass_name='', kernel_name=''):
        if op_type == '' and op_name == '' and pass_name == '' and kernel_name == '':
            table_list = []
            for debug_id, graph in self.npu_graphs.items():
                table = util.create_table(debug_id, ["OpType", "Count"])
                for op_types, op_list in graph.ops_type_list.items():
                    table.add_row(op_types, str(len(op_list)))
                table_list.append(table)
            util.print(util.create_columns(table_list))

        else:
            for debug_id, graph in self.npu_graphs.items():
                ops = graph.list_ops(op_type, op_name, pass_name, kernel_name)
                ops_txt = ['[green][%s][/green][yellow][%s][/yellow] %s' % (
                    op.type(), op.pass_name(), op.name()) for op in ops]
                util.print_panel(Constant.NEW_LINE.join(ops_txt), debug_id)

    def op_graph_summary(self, ops):
        npu_summary = collections.OrderedDict()
        for debug_id, op in ops.items():
            if op is None:
                self.log.debug("Find no target node in [%s]", debug_id)
                continue
            npu_summary[debug_id] = op.summary()
        return npu_summary, None

    def save_sub_graph(self, ops, deep):
        for debug_id, op in ops.items():
            if debug_id in self.npu_graphs:
                self.npu_graphs[debug_id].save_sub_graph(op, deep)
