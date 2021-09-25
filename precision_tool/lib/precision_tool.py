import argparse
import os
import time

from lib.overflow import Overflow
from lib.dump_manager import DumpManager
from lib.graph_manager import GraphManager
from lib.compare import Compare
from lib.fusion import Fusion
from lib.util import util
from lib.constant import Constant
import config as cfg
from lib.precision_tool_exception import PrecisionToolException
from lib.precision_tool_exception import catch_tool_exception


class PrecisionTool(object):
    def __init__(self):
        """init"""
        self.graph_manager = GraphManager()
        self.overflow = Overflow()
        self.dump_manager = DumpManager()
        self.compare = Compare()
        self.fusion = Fusion()
        self.log = util.get_log()

    @catch_tool_exception
    def prepare(self):
        """prepare"""
        util.create_dir(cfg.DATA_ROOT_DIR)
        self.graph_manager.prepare()
        self.dump_manager.prepare()
        self.overflow.prepare()
        self.fusion.prepare()
        self.compare.prepare()

    @catch_tool_exception
    def do_auto_check(self, argv):
        """Auto check"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--vector_compare', dest='vector_compare', help='Run vector compare process',
                            action='store_true')
        parser.add_argument('-l', '--limit', dest='limit', type=int, help='limit', default=3)
        args = parser.parse_args(argv)
        # vector compare
        if args.vector_compare:
            self.do_vector_compare()
        self.do_vector_compare_summary()
        self.do_check_fusion()
        self.do_check_overflow(args.limit)
        self.do_check_cast()
        self.do_check_graph_similarity()

    @catch_tool_exception
    def do_check_overflow(self, limit=3):
        """check overflow"""
        self.overflow.check(limit)

    @catch_tool_exception
    def do_check_cast(self):
        self.graph_manager.check_cast()

    @catch_tool_exception
    def do_check_dtype(self):
        """Check input/output dtype"""
        self.graph_manager.check_dtype()

    @catch_tool_exception
    def do_check_fusion(self):
        """print fusion info summary"""
        self.fusion.check()

    @catch_tool_exception
    def do_check_graph_similarity(self):
        self.graph_manager.check_similarity()

    @catch_tool_exception
    def do_vector_compare(self, argv=None):
        """do vector compare"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-lt', '--left', dest='lt', default=None, help='left path(npu dump path)')
        parser.add_argument('-rt', '--right', dest='rt', default=None, help='right path(cpu/npu dump path)')
        parser.add_argument('-g', '--graph', dest='graph', required=False, default=None, help='graph json file')
        args = parser.parse_args() if argv is None else parser.parse_args(argv)
        # 1. compare npu_debug0 - tf  dump data (auto)
        # 2. compare npu_debug0 - npu_debug1 dump data
        # 3. compare dir - dir dump data
        result_dir = os.path.join(cfg.VECTOR_COMPARE_PATH, time.strftime("%Y%m%d%H%M%S", time.localtime()))
        if args.lt is None:
            debug_0_dump_root = self.dump_manager.get_dump_root_dir(Constant.DEFAULT_DEBUG_ID)
            if util.empty_dir(debug_0_dump_root):
                raise PrecisionToolException("NPU debug_0 dump dir is empty, no files to compare.")
            if not util.empty_dir(cfg.TF_DUMP_DIR):
                self.log.info("Tf dump dir is not empty, will compare npu dump data with tf dump data.")
                self.compare.npu_tf_vector_compare(self.graph_manager.get_graphs(Constant.DEFAULT_DEBUG_ID),
                                                   debug_0_dump_root, cfg.TF_DUMP_DIR, result_dir)
            else:
                self.log.warning("Tf dump dir is empty, maybe run [python3 precision_tool/cli.py tf_dump] to decode"
                                 " tf debug data.")
            debug_1_dump_root = self.dump_manager.get_dump_root_dir(Constant.NPU_DEBUG_ID_1)
            if debug_1_dump_root is not None and not util.empty_dir(debug_1_dump_root):
                self.log.info("NPU debug_1 dump dir is not empty, will compare two npu dump data.")
                self.compare.npu_vector_compare(debug_0_dump_root, debug_1_dump_root)
        else:
            lh_path = args.lt
            rh_path = args.rt
            graph_json = args.graph
            self.compare.vector_compare(lh_path, rh_path, result_dir, graph_json)
        self.compare.vector_summary(result_dir)

    @catch_tool_exception
    def do_vector_compare_summary(self, argv=None):
        parser = argparse.ArgumentParser(description="show vector compare result summary.")
        parser.add_argument('-f', '--file', dest='file', default=None, required=False, help='compare_result file/path')
        parser.add_argument('-c', '--cos_sim', dest='cos_sim', type=float, help='cos_sim_threshold', default=0.98)
        parser.add_argument('-l', '--limit', dest='limit', type=int, help='limit', default=3)
        args = parser.parse_args() if argv is None else parser.parse_args(argv)
        error_ops = self.compare.vector_summary(args.file, args.cos_sim, args.limit)
        # parse error_ops

    @catch_tool_exception
    def do_print_data(self, argv=None):
        """print tensor data"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        args = parser.parse_args() if argv is None else parser.parse_args(argv)
        self.dump_manager.print_tensor(args.name, True)

    @catch_tool_exception
    def do_list_nodes(self, argv):
        """list op nodes in graph"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', dest='type', default='', help='list by op type')
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        parser.add_argument('-f', '--fusion', dest='fusion', default='', help='list by op fusion pass')
        parser.add_argument('-k', '--kernel_name', dest='kernel_name', default='', help='list by op kernel_name')
        args = parser.parse_args(argv)
        self.graph_manager.print_op_list(args.type, args.name, args.fusion, args.kernel_name)

    @catch_tool_exception
    def do_node_info(self, argv):
        """Print op node info"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='op name')
        parser.add_argument('-g', '--graph', dest='graph', help='graph name')
        parser.add_argument('-s', '--save', dest='save', type=int, default=0,
                            help='save subgraph, param gives the deep of subgraph')
        args = parser.parse_args(argv)
        # print graph op info
        npu_ops, _ = self.graph_manager.get_ops(args.name, args.graph)
        npu_op_summary, tf_op_summary = self.graph_manager.op_graph_summary(npu_ops)
        npu_dump_summary, tf_dump_summary = self.dump_manager.op_dump_summary(npu_ops)
        # merge graph/dump/compare info
        for debug_id, graph_summary in npu_op_summary.items():
            for graph_name, summary_detail in graph_summary.items():
                summary_txt = [summary_detail]
                if debug_id in npu_dump_summary and graph_name in npu_dump_summary[debug_id]:
                    summary_txt.append(npu_dump_summary[debug_id][graph_name])
                if tf_dump_summary is not None:
                    summary_txt.append(tf_dump_summary)
                title = "[green](%s)[/green] %s" % (debug_id, graph_name)
                util.print_panel(Constant.NEW_LINE.join(summary_txt), title)
        if args.save != 0:
            self.graph_manager.save_sub_graph(npu_ops, args.save)

    @catch_tool_exception
    def do_compare_data(self, argv):
        """compare two tensor"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='names', type=str, default=[], help='op name', nargs='+')
        parser.add_argument('-p', '--print', dest='count', default=20, type=int, help='print err data num')
        parser.add_argument('-s', '--save', dest='save', action='store_true', help='save data in txt format')
        parser.add_argument('-al', '--atol', dest='atol', default=0.001, type=float, help='set rtol')
        parser.add_argument('-rl', '--rtol', dest='rtol', default=0.001, type=float, help='set atol')
        args = parser.parse_args(argv)
        if len(args.names) != 2:
            self.log.error("compare files should be 2.")
        else:
            self.compare.compare_data(args.names[0], args.names[1], args.save, args.rtol, args.atol, args.count)

    @catch_tool_exception
    def do_list_dump(self, argv):
        """List dump files"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', dest='type', help='')
        parser.add_argument('-n', '--name', dest='name')
        self.dump_manager.list_dump(argv.dir, argv.name)

    @catch_tool_exception
    def do_convert_npu_dump(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', help='op name')
        parser.add_argument('-f', '--format', dest='format', default=None, required=False, help='target format')
        parser.add_argument('-o', '--output', dest='output', required=False, default=None, help='output path')
        args = parser.parse_args(argv)
        self.dump_manager.convert_npu_dump(args.name, args.format, args.output)

    @catch_tool_exception
    def do_convert_all_npu_dump(self):
        self.dump_manager.decode_all_npu_dump()

    @catch_tool_exception
    def check_graph_similarity(self):
        """ Check graph similarity """

    def single_cmd(self, argv):
        cmd_func_map = {'compare': self.do_compare_data,
                        'vector_compare': self.do_vector_compare}
        if argv[1] in cmd_func_map:
            func = cmd_func_map[argv[1]]
            return func(argv[2:])
        raise PrecisionToolException("cmd %s is not supported or cmd should be run in interactive mode." % argv[1])
