# coding=utf-8
"""
Graph Manager
"""
import json
import os
import collections
import time
from .op import Op
from ..util.util import util
from ..util.constant import Constant
from ..util.precision_tool_exception import catch_tool_exception
from ..util.precision_tool_exception import PrecisionToolException
from ..config import config as cfg

DANGEROUS_CAST = {
    'DT_FLOAT': ['DT_INT32']
}

NO_DIG_OPS = ['AtomicAddrClean', 'NetOutput']
CKPT_META_SHUFFIX='.meta'

OP_CAST = 'Cast'


class NpuSubGraph(object):
    def __init__(self, graph_json, build_file, npu_graph):
        self.log = util.get_log()
        self.graph_name = graph_json['name']
        self.npu_graph = npu_graph
        self.graph = graph_json
        self.build_file = build_file
        self.ops_list = collections.OrderedDict()
        self.ops_type_list = {}
        self._prepare()
        self.graph_id = self._get_graph_id()

    def _prepare(self):
        self.log.debug("Graph %s operator count: %d" % (self.graph_name, len(self.graph['op'])))
        for op_json in self.graph['op']:
            op_name = op_json['name']
            op_type = op_json['type']
            if op_name not in self.ops_list:
                self.ops_list[op_name] = []
            op = Op(op_json, self.ops_list, self.graph['name'], self.npu_graph, self)
            if op_type not in self.ops_type_list:
                self.ops_type_list[op_type] = {}
            self.ops_list[op_name] = op
            self.ops_type_list[op_type][op_name] = op

    def _get_graph_id(self):
        if 'attr' in self.graph:
            for item in self.graph['attr']:
                if item['key'] == '_session_graph_id':
                    return item['value']['s']
        self.log.warning("Unknown sub graph id.")
        return "UNKNOWN"

    def compare(self, sub_graph):
        """compare with another sub graph"""
        if not isinstance(sub_graph, NpuSubGraph):
            raise PrecisionToolException("Should compare with another subgraph.")
        right_ops_list = sub_graph.ops_list
        ignore_ops = ["TransData", "Cast", "Recv", "Send", "Variable", "NetOutput", "NoOp", "Assign", "Constant",
                      "StreamActive"]
        similar_count = 0
        for op_name in self.ops_list:
            if self.ops_list[op_name].type() in ignore_ops:
                continue
            if op_name not in right_ops_list:
                self.log.warning("Can not Find [%s] %s in right subgraph.", self.ops_list[op_name].type(), op_name)
                continue
            result, similar = self.ops_list[op_name].compare(right_ops_list[op_name])
            if not similar:
                util.print_panel(result, title=op_name)
            else:
                similar_count += 1
        for op_name in right_ops_list:
            if right_ops_list[op_name].type() in ignore_ops:
                continue
            if op_name not in self.ops_list:
                self.log.warning("Can not Find [%s] %s in left subgraph.", right_ops_list[op_name].type(), op_name)
        self.log.info("Compare [%s] [%s], similarity is [%s / %s]",
                      self.graph_name, sub_graph.graph_name, similar_count, len(self.ops_list))

    def get_op(self, name):
        if name in self.ops_list:
            return [self.ops_list[name]]
        guess_op_list = []
        for op_detail in self.ops_list.values():
            if name in op_detail.name():
                guess_op_list.append(op_detail)
        return guess_op_list

    def get_parent_node_by_subgraph_name(self, graph_name):
        ops = []
        for op_detail in self.ops_list.values():
            if graph_name in op_detail.subgraph_names():
                ops.append(op_detail)
        return ops

    def get_op_by_type(self, op_type):
        ops = []
        for op_detail in self.ops_list.values():
            if op_type == op_detail.type():
                ops.append(op_detail)
        return ops

    def check_cast(self):
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


class NpuGraph(object):
    def __init__(self, debug_id=Constant.DEFAULT_DEBUG_ID):
        self.log = util.get_log()
        self.build_files = None
        self.build_json_files = []
        self.debug_id = debug_id
        self.npu_root = os.path.join(cfg.NPU_DIR, debug_id)
        self.graph_root = os.path.join(self.npu_root, Constant.GRAPH)
        self.sub_graphs = collections.OrderedDict()
        self.ops_list = []
        util.create_dir(self.graph_root)

    @catch_tool_exception
    def prepare(self):
        """prepare"""
        self._prepare_npu_graphs()
        if self.build_files is not None:
            for build_file in self.build_files:
                self._parse_ops(build_file)

    def check_cast(self):
        """Check cast op type"""
        for sub_graph in self.sub_graphs.values():
            sub_graph.check_cast()

    def check_dtype(self):
        """Check op input/output dtype"""
        for op in self.ops_list:
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
    def save_sub_graph(self, op, deep=0, dump_manager=None, compare_manager=None):
        """Save sub graph"""
        if op is None:
            raise PrecisionToolException("Save sub graph failed as root operator is None.")
        try:
            from graphviz import Digraph
            file_name_list = [self.debug_id, op.graph_name, op.type(), op.name().replace('/', '_').replace('.', '_'),
                              str(deep), 'gv']
            file_name = '.'.join(file_name_list)
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
            sub_op = self.get_op(desc.name(), op.graph_name)
            if len(sub_op) != 0:
                sub_op = sub_op[0]
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
                sub_op = self.get_op(out_node_name, op.graph_name)
                if len(sub_op) != 0 and direction in ['all', 'output']:
                    sub_op = sub_op[0]
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

    def list_ops(self, op_type='', op_name='', pass_name='', kernel_name=''):
        """list ops in graph"""
        return filter(lambda op: op_type in op.type() and op_name in op.name() and pass_name in op.pass_name()
                                 and kernel_name in op.kernel_name(), self.ops_list)

    def get_op(self, name, graph_name=None):
        """get op by name"""
        # get op in specific sub graph
        if graph_name is not None and graph_name in self.sub_graphs:
            return self.sub_graphs[graph_name].get_op(name)
        ops = []
        for sub_graph in self.sub_graphs.values():
            ops.extend(sub_graph.get_op(name))
        # check if there is an exact match operation
        match_ops = list(filter(lambda x: x.name() == name, ops))
        if len(match_ops) != 0:
            return match_ops
        # return guess operations by name
        self.log.info("Can not find Operator named %s. You may mean the operator bellow.", name)
        guess_op_name_list = ['[green][%s][/green] %s' % (x.type(), x.name()) for x in ops]
        util.print_panel(Constant.NEW_LINE.join(guess_op_name_list), title='Possible Operators')
        return ops

    def get_parent_node_by_subgraph_name(self, graph_name):
        ops = []
        for sub_graph in self.sub_graphs.values():
            ops.extend(sub_graph.get_parent_node_by_subgraph_name(graph_name))
        return ops

    def _prepare_npu_graphs(self):
        """prepare ge graphs  """
        # move graphs to precision data dir
        graph_files = util.list_ge_graph_files(self.graph_root)
        self.build_files = sorted(filter(lambda x: x.graph_name == cfg.BUILD_JSON_GRAPH_NAME, graph_files.values()),
                                  key=lambda x: x.graph_id)
        if len(self.build_files) == 0:
            self.log.warning("Can not find any build files in dir: %s", self.graph_root)
        self.log.info("Find [%d] GE build files.", len(self.build_files))

    @catch_tool_exception
    def _parse_ops(self, build_file):
        """Parse *_Build.txt.json to op objects."""
        build_file_json = build_file.path + '.json'
        build_file_json = util.convert_proto_to_json(build_file.path, build_file_json)
        if build_file_json is not None:
            self.build_json_files.append(build_file_json)
        with open(build_file_json, 'r') as f:
            graph_json = json.load(f)
            if 'graph' not in graph_json:
                raise PrecisionToolException("No graph in file: %s" % build_file.file_name)
            if len(graph_json['graph']) != 1:
                self.log.warning("There are more then one graph in ge build file, find %d" % len(graph_json['graph']))
            # sub_graphs = []
            for graph in graph_json['graph']:
                npu_sub_graph = NpuSubGraph(graph, build_file, self)
                self.sub_graphs[graph['name']] = npu_sub_graph
                self.ops_list.extend(npu_sub_graph.ops_list.values())
