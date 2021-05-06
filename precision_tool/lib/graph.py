# coding=utf-8
"""
Graph Manager
"""
import json
import os
import re
import shutil
import collections
import time

import config as cfg
from lib.tool_object import ToolObject
from lib.tf_graph import TensorflowGraph
from lib.op import Op
from lib.util import util
from lib.precision_tool_exception import catch_tool_exception
from lib.precision_tool_exception import PrecisionToolException

DANGEROUS_CAST = {
    'DT_FLOAT': ['DT_INT32']
}

NO_DIG_OPS = ['AtomicAddrClean', 'NetOutput']
CKPT_META_SHUFFIX='.meta'

OP_CAST = 'Cast'


class Graph(ToolObject):
    def __init__(self):
        super(Graph, self).__init__()
        self._init_dirs()
        self.build_file = None
        self.sub_graph = None
        self.ops_list = collections.OrderedDict()
        self.cpu_ops_list = collections.OrderedDict()
        self.tf_graph = TensorflowGraph()
        self.ops_type_list = {}
        self.log = util.get_log()

    @catch_tool_exception
    def prepare(self):
        """prepare"""
        self._prepare_npu_graphs()
        self._parse_ops()
        # parse tf ops
        # self.cpu_ops_list = self.tf_graph.get_op_list(cfg.GRAPH_CPU)

    def check_cast(self):
        """Check cast op type"""
        cast_list = {}
        danger_cast_list = {}
        if OP_CAST in self.ops_type_list:
            cast_ops = self.ops_type_list[OP_CAST]
            for op in cast_ops.values():
                input_type = ''
                output_type = ''
                for input_desc in op.inputs():
                    input_type = input_desc.dtype() if input_desc.dtype() != '' else input_type
                for output_desc in op.outputs():
                    output_type = output_desc.dtype() if output_desc.dtype() != '' else output_type
                cast_type = "%s -> %s" % (input_type, output_type)
                if cast_type not in cast_list:
                    cast_list[cast_type] = []
                cast_list[cast_type].append(op.name())
        for cast_type in cast_list:
            if self._is_dangerous_cast(cast_type):
                summary_txt = "[green][Cast][/green][red][%s][/red] %s" % (cast_type, cast_list[cast_type])
                util.print(summary_txt)

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

    @catch_tool_exception
    def print_op(self, op_name, is_dump=False, save_graph_level=0, dump_manager=None, compare_manager=None):
        """Print op detail info"""
        op = self.get_op(op_name)
        if op is None:
            raise PrecisionToolException("Can not find op [%s]" % op_name)
        title = '[green][%s][/green]%s' % (op.type(), op.name())
        summary = op.summary()
        # print dump info
        if is_dump:
            dump_summary = dump_manager.op_dump_summary(op)
            summary = '\n'.join([summary, dump_summary]) if dump_summary is not None else summary
        util.print_panel(summary, title=title, fit=True)
        # save subgraph
        if save_graph_level > 0:
            self.save_sub_graph(op, save_graph_level, dump_manager, compare_manager)
        return op

    def save_sub_graph(self, op, deep=0, dump_manager=None, compare_manager=None):
        """Save sub graph"""
        if op is None:
            raise PrecisionToolException("Save sub graph failed as root operator is None.")
        try:
            from graphviz import Digraph
            file_name = op.type() + '.' + op.name().replace('/', '_').replace('.', '_') + '.' + str(deep) + '.gv'
            path = os.path.join(cfg.OP_GRAPH_DIR, file_name)
            dot = Digraph(file_name, filename=path, node_attr={'shape': 'Mrecord'}, format='svg')
            dot_list = []
            edge_list = []
            self._gen_sub_graph(dot, op, deep, dot_list, edge_list, 'red', direction='all',
                                dump_manager=dump_manager, compare_manager=compare_manager)
            dot.format = 'svg'
            dot.save(path)
            self.log.info("Sub graph saved to %s" % os.path.abspath(cfg.OP_GRAPH_DIR))
            try:
                dot.view(path)
                time.sleep(1)
            except Exception as err:
                raise PrecisionToolException(
                    "graphviz not install, use [yum/apt-get] install graphviz xdg-utils. %s" % err)
        except ImportError as err:
            raise PrecisionToolException("Save sub graph failed as import graphviz module failed. %s" % err)

    def _gen_sub_graph(self, dot, op, deep, dot_list, edge_list, color='black', direction='all',
                       dump_manager=None, compare_manager=None):
        """Gen sub graph"""
        if deep == 0 or op.type() in NO_DIG_OPS:
            return
        if op.name() not in dot_list:
            dot.node(op.name(), self._gen_sub_graph_label(op), color=color, tooltip=op.summary(True))
            dot_list.append(op.name())
        # add input and output
        for desc in op.inputs():
            sub_op = self.get_op(desc.name())
            if sub_op is not None:
                if direction in ['all', 'input']:
                    self._gen_sub_graph(dot, sub_op, deep - 1, dot_list, edge_list, direction='input')
                if sub_op.name() in dot_list:
                    src_edge = '%s:o%d' % (sub_op.name(), desc.peer_idx())
                else:
                    dot.node(sub_op.name(), self._gen_sub_graph_label(sub_op), color=color, tooltip=op.summary(True))
                    src_edge = '%s:o%d' % (sub_op.name(), desc.peer_idx())
                dst_edge = '%s:i%d' % (op.name(), desc.idx())
                if src_edge + dst_edge not in edge_list:
                    dot.edge(src_edge, dst_edge)
                    edge_list.append(src_edge + dst_edge)
        # add output
        for desc in op.outputs():
            for out_node_name in desc.names():
                sub_op = self.get_op(out_node_name)
                if sub_op is not None and direction in ['all', 'output']:
                    self._gen_sub_graph(dot, sub_op, deep - 1, dot_list, edge_list, direction='output')

    def _gen_sub_graph_label(self, op):
        input_labels = []
        for desc in op.inputs():
            input_labels.append(self._gen_sub_graph_desc(desc, 'i'))
        output_labels = []
        for desc in op.outputs():
            output_labels.append(self._gen_sub_graph_desc(desc, 'o'))
        str_cell = '|'
        return '{{ %s } | [%s] %s | { %s }}' % (str_cell.join(input_labels), op.type(), op.name(),
                                                str_cell.join(output_labels))

    @staticmethod
    def _gen_sub_graph_desc(desc, id_prefix):
        desc_str = r'<%s%d> [%d]' % (id_prefix, desc.idx(), desc.idx())
        desc_str = r'%s [%s]' % (desc_str, desc.dtype()) if desc.dtype() != '' else desc_str
        desc_str = r'%s\n%s' % (desc_str, desc.shape()) if len(desc.shape()) != 0 else desc_str
        return desc_str

    def list_ops(self):
        """list ops in graph"""
        return self.ops_list

    def list_ops_type(self):
        return self.ops_type_list

    def get_op(self, name):
        """get op by name"""
        if name in self.ops_list:
            return self.ops_list[name]
        guess_op_list = []
        for op_detail in self.ops_list.values():
            if name in op_detail.name():
                guess_op_list.append(op_detail)
        if len(guess_op_list) == 0:
            self.log.warning("Can not find any Operator like %s", name)
            return None
        self.log.info("Can not find Operator named %s. You may mean the operator bellow.", name)
        guess_op_name_list = ['[green][%s][/green] %s' % (x.type(), x.name()) for x in guess_op_list]
        util.print_panel('\n'.join(guess_op_name_list), title='Possible Operators')
        return guess_op_list[0]

    def print_op_list(self, op_type='', op_name='', pass_name=''):
        """Print op list"""
        if op_type == '' and op_name == '' and pass_name == '':
            table = util.create_table("Operation Summary", ["OpType", "Count"])
            for op_type in self.ops_type_list.keys():
                table.add_row(op_type, str(len(self.ops_type_list[op_type])))
            util.print(table)
            return
        for op in self.ops_list.values():
            if op_type in op.type() and op_name in op.name() and pass_name in op.pass_name():
                self._print_single_op(op)

    @staticmethod
    def _print_single_op(op):
        """Print Single op"""
        op_pass_name = '' if op.pass_name() == '' else '[yellow][%s][/yellow]' % op.pass_name()
        util.print('[green][%s][/green]%s %s' % (op.type(), op_pass_name, op.name()))

    @staticmethod
    def _is_dangerous_cast(cast_type):
        """Check if cast """
        cast_info = cast_type.split(" -> ")
        input_dtype = cast_info[0]
        output_dtype = cast_info[1]
        if input_dtype in DANGEROUS_CAST:
            if output_dtype in DANGEROUS_CAST[input_dtype]:
                return True
        return False

    @staticmethod
    def _init_dirs():
        """Create graph dirs."""
        util.create_dir(cfg.GRAPH_DIR)
        util.create_dir(cfg.GRAPH_DIR_ALL)
        util.create_dir(cfg.GRAPH_DIR_BUILD)
        util.create_dir(cfg.GRAPH_CPU)

    def _prepare_npu_graphs(self):
        """Copy ge graphs to graph dir. """
        # move graphs to precision data dir
        graph_files = util.list_ge_graph_files(cfg.GRAPH_DIR_ALL)
        build_files = sorted(filter(lambda x: x['graph_name'] == cfg.BUILD_JSON_GRAPH_NAME, graph_files.values()),
                             key=lambda x: x['graph_id'])
        if len(build_files) == 0:
            self.log.warning("Can not find any build files in dir: %s", cfg.GRAPH_DIR_ALL)
            return
        self.log.info("Choose [%s] as default GE build file.", build_files[-1]['file_name'])
        self.build_file = util.convert_proto_to_json(build_files[-1]['file_name'])

    def _parse_ops(self):
        """Parse *_Build.txt.json to op objects."""
        # only parse the last build graph
        if self.build_file is None:
            raise PrecisionToolException("Cannot find any ge_proto_*_Build.json in %s." % cfg.GRAPH_DIR_BUILD)
        graph_name = self.build_file
        graph_path = os.path.join(cfg.GRAPH_DIR_BUILD, graph_name)
        with open(graph_path, 'r') as f:
            graph_json = json.load(f)
            if 'graph' not in graph_json:
                raise PrecisionToolException("No graph in file: %s" % graph_path)
            if len(graph_json['graph']) != 1:
                self.log.warning("There are more then one graph in ge build file, find %d" % len(graph_json['graph']))
            # cur_max_ops = 0
            # for graph in graph_json['graph']:
            #     self.log.debug("Graph %s operator count: %d" % len(graph['op']))
            item = graph_json['graph'][0]
            self.log.info("Find graph [%s] in %s", item['name'], graph_name)
            self.sub_graph = item['name']
            for op_json in item['op']:
                op_name = op_json['name']
                op_type = op_json['type']
                op = Op(op_json, self.ops_list)
                if op_type not in self.ops_type_list:
                    self.ops_type_list[op_type] = {}
                self.ops_list[op_name] = op
                self.ops_type_list[op_type][op_name] = op
        self.log.info("Finish parse npu ops from ge graph, find [%d] ops.", len(self.ops_list))
