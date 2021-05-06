import argparse
import os

from lib.overflow import Overflow
from lib.dump import Dump
from lib.graph import Graph
from lib.compare import Compare
from lib.fusion import Fusion
from lib.util import util
import config as cfg
from lib.precision_tool_exception import PrecisionToolException
from lib.precision_tool_exception import catch_tool_exception

# env flags
FLAG_DUMP_GE_GRAPH = 'DUMP_GE_GRAPH'
FLAG_DUMP_GRAPH_LEVEL = 'DUMP_GRAPH_LEVEL'
FLAG_DUMP_GRAPH_PATH = 'DUMP_GRAPH_PATH'
FLAG_CHECK_OVERFLOW = 'CHECK_OVERFLOW'


class PrecisionTool(object):
    def __init__(self):
        """init"""
        self.graph = Graph()
        self.overflow = Overflow()
        self.dump = Dump()
        self.compare = Compare()
        self.fusion = Fusion()
        self.log = util.get_log()

    @catch_tool_exception
    def prepare(self):
        """prepare"""
        util.create_dir(cfg.DATA_ROOT_DIR)
        self.graph.prepare()
        self.dump.prepare(self.graph.sub_graph)
        self.overflow.prepare()
        self.fusion.prepare()
        self.compare.prepare()

    @catch_tool_exception
    def do_auto_check(self, argv):
        """auto check"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--vector_compare', dest='vector_compare', help='auto check', action='store_true')
        args = parser.parse_args(argv)
        # vector compare
        if args.vector_compare:
            self.do_vector_compare()
        self.do_vector_compare_summary()
        self.do_check_fusion()
        self.do_check_overflow()
        self.do_check_cast()
        self.do_check_graph_similarity()

    @catch_tool_exception
    def do_check_overflow(self):
        """check overflow"""
        self.overflow.check()

    @catch_tool_exception
    def do_check_cast(self):
        self.graph.check_cast()

    @catch_tool_exception
    def do_check_dtype(self):
        """Check input/output dtype"""
        self.graph.check_dtype()

    @catch_tool_exception
    def do_check_fusion(self):
        """print fusion info summary"""
        self.fusion.check()

    @catch_tool_exception
    def do_check_graph_similarity(self):
        self.graph.check_similarity()

    @catch_tool_exception
    def do_vector_compare(self, argv=None):
        """do vector compare"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-lt', '--left', dest='lt', default=None, help='left path(npu dump path)')
        parser.add_argument('-rt', '--right', dest='rt', default=None, help='right path(cpu/npu dump path)')
        parser.add_argument('-g', '--graph', dest='graph', required=False, default=None, help='graph json file')
        args = parser.parse_args() if argv is None else parser.parse_args(argv)
        if args.lt is None:
            lh_path = self.dump.sub_graph_path
            rh_path = cfg.DUMP_FILES_CPU
            graph_json = os.path.join(cfg.GRAPH_DIR_BUILD, self.graph.build_file)
        else:
            lh_path = args.lt
            rh_path = args.rt
            graph_json = args.graph
        self.compare.vector_compare(lh_path, rh_path, graph_json)

    @catch_tool_exception
    def do_vector_compare_summary(self, argv=None):
        parser = argparse.ArgumentParser(description="show vector compare result summary.")
        parser.add_argument('-f', '--file', dest='file', default=None, required=False, help='compare_result file')
        parser.add_argument('-c', '--cos_sim', dest='cos_sim', type=float, help='cos_sim_threshold', default=0.98)
        args = parser.parse_args() if argv is None else parser.parse_args(argv)
        error_ops = self.compare.vector_summary(args.file, args.cos_sim)

    @catch_tool_exception
    def do_print_data(self, argv=None):
        """print tensor data"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        parser.add_argument('-c', '--convert', dest='convert', help='convert txt', action='store_true')
        args = parser.parse_args() if argv is None else parser.parse_args(argv)
        self.dump.print_data(args.name, args.convert)

    @catch_tool_exception
    def do_list_nodes(self, argv):
        """list op nodes in graph"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', dest='type', default='', help='list by op type')
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        parser.add_argument('-f', '--fusion', dest='fusion', default='', help='list by op fusion pass')
        args = parser.parse_args(argv)
        self.graph.print_op_list(args.type, args.name, args.fusion)

    @catch_tool_exception
    def do_list_dump(self, argv):
        """List dump files"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--dir', dest='dir')
        parser.add_argument('-n', '--name', dest='name')
        self.dump.list_dump(argv.dir, argv.name)

    @catch_tool_exception
    def do_node_info(self, argv):
        """Print op node info"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='op name')
        parser.add_argument('-d', '--dump', dest='dump', help='show dump files info', action='store_true')
        parser.add_argument('-s', '--save', dest='save', type=int, default=0,
                            help='save subgraph, param gives the deep of subgraph')
        args = parser.parse_args(argv)
        # print graph op info
        self.graph.print_op(args.name, args.dump, args.save, dump_manager=self.dump, compare_manager=self.compare)

    @catch_tool_exception
    def do_convert_npu_dump(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', help='op name')
        parser.add_argument('-f', '--format', dest='format', help='target format')
        parser.add_argument('-o', '--output', dest='output', required=False, default=None, help='output path')
        args = parser.parse_args(argv)
        self.dump.convert_npu_dump(args.name, args.format, args.output)

    @catch_tool_exception
    def do_convert_all_npu_dump(self):
        self.dump.decode_all_npu_dump()

    @catch_tool_exception
    def do_compare_data(self, argv):
        """compare two tensor"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='names', type=str, default=[], help='op name', nargs='+')
        parser.add_argument('-p', '--print', dest='count', default=20, type=int, help='print err data num')
        parser.add_argument('-s', '--save', dest='save', action='store_true', help='print err data num')
        parser.add_argument('-al', '--atol', dest='atol', default=0.001, type=float, help='set rtol')
        parser.add_argument('-rl', '--rtol', dest='rtol', default=0.001, type=float, help='set atol')
        args = parser.parse_args(argv)
        if len(args.names) != 2:
            self.log.error("compare files should be 2.")
        else:
            self.compare.compare_data(args.names[0], args.names[1], args.save, args.rtol, args.atol, args.count)

    @catch_tool_exception
    def check_graph_similarity(self):
        """ Check graph similarity """

    def single_cmd(self, argv):
        cmd_func_map = {'compare': self.do_compare_data,
                        'vector_compare': self.do_vector_compare}
        if argv[1] in cmd_func_map:
            func = cmd_func_map[argv[1]]
            return func(argv[2:])
        raise PrecisionToolException("cmd %s is not supported or cmd should be run in interactive mode.", argv[1])
