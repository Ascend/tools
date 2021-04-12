# coding=utf-8
"""
Graph Manager
"""
import json
import os
import re
import shutil
import collections

import config as cfg
from lib.tool_object import ToolObject
from lib.op import Op
from lib.util import util

DANGEROUS_CAST = {
    'DT_FLOAT': ['DT_INT32']
}
GE_GRAPH_PREFIX = '^ge_.*txt$'
GE_GRAPH_BUILD = '^ge_.*_Build.*txt$'
GE_GRAPH_BUILD_PROTO = '^ge_proto.*_Build.*txt$'
GE_GRAPH_BUILD_JSON = '^ge_proto.*_Build.*json$'
CKPT_META_SHUFFIX='.meta'

OP_CAST = 'Cast'


class Graph(ToolObject):
    """ """
    def __init__(self):
        """
        """
        super(Graph, self).__init__()
        self._init_dirs()
        self.build_list = []
        self.sub_graph_json_map = {}
        # ops = []
        self.ops_list = collections.OrderedDict()
        self.cpu_ops_list = collections.OrderedDict()
        self.ops_type_list = {}
        self.log = util.get_log()

    def prepare(self):
        """ prepare """
        self._prepare_npu_graphs()
        self._parse_ops()
        self._parse_cpu_ops()

    def sub_graph(self):
        """Get sub graph map."""
        return self.sub_graph_json_map

    def check_cast(self):
        """Check cast op type"""
        if OP_CAST in self.ops_type_list:
            cast_ops = self.ops_type_list[OP_CAST]
            for op in cast_ops.values():
                input_type = ''
                output_type = ''
                for input_desc in op.inputs():
                    input_type = input_desc.dtype() if input_desc.dtype() != '' else input_type
                for output_desc in op.outputs():
                    output_type = output_desc.dtype() if output_desc.dtype() != '' else output_type
                color = 'red' if self._is_dangerous_cast(input_type, output_type) else 'yellow'
                util.print('[green][%s][/green][%s][%s -> %s][/%s] %s' % (
                    op.type(), color, input_type, output_type, color, op.name()))

    def check_dtype(self):
        """Check op input/output dtype"""
        for op in self.ops_list.values():
            input_dtype = ''
            for input_desc in op.inputs():
                input_dtype += ' ' + input_desc.dtype()
            output_dtype = ''
            for output_desc in op.outputs():
                output_dtype += ' ' + output_desc.dtype()
            util.print('[green][%s][/green] %s\n - Input:  %s\n - Output: %s' % (
                op.type(), op.name(), input_dtype, output_dtype))

    def check_similarity(self):
        """Check graph similarity."""

    def print_op(self, op_name):
        """ print op detail info"""
        if op_name not in self.ops_list:
            self.log.warning("can not find op [%s]" % op_name)
            return
        op = self.ops_list[op_name]
        title = '[green][%s][/green]%s' % (op.type(), op.name())
        util.print_panel(op.summary(), title=title, fit=True)

    def list_ops(self):
        """list ops in graph"""
        return self.ops_list

    def list_ops_type(self):
        return self.ops_type_list

    def get_op(self, name):
        """get op by name"""
        return self.ops_list[name] if name in self.ops_list else None

    def print_op_list(self, op_type='', op_name='', pass_name=''):
        """"""
        if op_type == '' and op_name == '' and pass_name == '':
            for op in self.ops_list.values():
                util.print('[green][%s][/green] %s' % (op.type(), op.name()))
            table = util.create_table("Operation Summary", ["OpType", "Count"])
            for op_type in self.ops_type_list.keys():
                table.add_row(op_type, str(len(self.ops_type_list[op_type])))
            return
        for op in self.ops_list.values():
            if op_type in op.type() and op_name in op.name() and pass_name in op.pass_name():
                op_pass_name = '' if op.pass_name() == '' else '[yellow][%s][/yellow]' % op.pass_name()
                util.print('[green][%s][/green]%s %s' % (op.type(), op_pass_name, op.name()))

    def _parse_cpu_ops(self):
        self._convert_ckpt_to_graph(cfg.GRAPH_CPU)

    def _convert_ckpt_to_graph(self, ckpt_path):
        import tensorflow as tf
        if not str(ckpt_path).endswith(CKPT_META_SHUFFIX):
            if os.path.isfile(ckpt_path + CKPT_META_SHUFFIX):
                ckpt_path = ckpt_path + CKPT_META_SHUFFIX
            elif os.path.isdir(ckpt_path):
                # find .meta
                sub_files = os.listdir(ckpt_path)
                for file_name in sub_files:
                    if file_name.endswith(CKPT_META_SHUFFIX):
                        ckpt_path = file_name
        if not str(ckpt_path).endswith(CKPT_META_SHUFFIX):
            self.log.error("Path [%s] is not valid.", ckpt_path)
            return
        saver = tf.train.import_meta_graph(ckpt_path, clear_devices=True)
        graph = tf.get_default_graph()
        for op in graph.get_operations():
            self.cpu_op_list[op.name] = op

    @staticmethod
    def _is_dangerous_cast(input_dtype, output_dtype):
        """Check if cast """
        if input_dtype in DANGEROUS_CAST:
            if output_dtype in DANGEROUS_CAST[input_dtype]:
                return True
        return False

    @staticmethod
    def _init_dirs():
        """Create graph dirs."""
        util.create_dir(cfg.GRAPH_DIR)
        util.create_dir(cfg.GRAPH_DIR_ALL)
        util.create_dir(cfg.GRAPH_DIR_LAST)
        util.create_dir(cfg.GRAPH_DIR_BUILD)

    def _prepare_npu_graphs(self):
        """Copy ge graphs to graph dir. """
        # move graphs to precision data dir
        files = os.listdir('./')
        num = 0
        for file in files:
            if re.match(GE_GRAPH_PREFIX, file):
                if re.match(GE_GRAPH_BUILD, file):
                    shutil.copy(file, cfg.GRAPH_DIR_LAST)
                shutil.move(file, os.path.join(cfg.GRAPH_DIR_ALL, file))
                num += 1
        self.log.info("Prepare GE graphs success. Move [%d] graphs", num)
        # convert build proto files to json files
        util.convert_proto_to_json(os.listdir(cfg.GRAPH_DIR_LAST))
        # list graphs
        self.build_list = list(filter(lambda x: re.match(GE_GRAPH_BUILD_JSON, x) is not None,
                                      os.listdir(cfg.GRAPH_DIR_BUILD)))

    def _parse_ops(self):
        """Parse *_Build.txt.json to op objects."""
        # only parse the last build graph
        if len(self.build_list) == 0:
            self.log.warning("Cannot find any ge_proto_*_Build.txt in %s.", cfg.GRAPH_DIR_LAST)
            return
        sorted_graphs = sorted(self.build_list)
        self.log.info("Find [%d] graphs. %s", len(sorted_graphs), sorted_graphs)
        last_graph = sorted_graphs[-1]
        self.log.info("Choose the last graph [%s].", last_graph)
        graph_path = os.path.join(cfg.GRAPH_DIR_BUILD, last_graph)
        with open(graph_path, 'r') as f:
            graph_json = json.load(f)
            for item in graph_json['graph']:
                self.log.info("Find graph [%s] in %s", item['name'], last_graph)
                self.sub_graph_json_map[item['name']] = graph_path
                for op_json in item['op']:
                    op_name = op_json['name']
                    op_type = op_json['type']
                    op = Op(op_json, self.ops_list)
                    if op_type not in self.ops_type_list:
                        self.ops_type_list[op_type] = {}
                    self.ops_list[op_name] = op
                    self.ops_type_list[op_type][op_name] = op

