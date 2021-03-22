import argparse
import os
from lib.overflow import Overflow
from lib.dump import Dump
from lib.graph import Graph
from lib.compare import Compare
from lib.fusion import Fusion
from lib.util import util
from lib.util import LOG
import config as cfg


class PrecisionTool(object):
    def __init__(self):
        """"""
        self.graph = Graph()
        self.overflow = Overflow()
        self.dump = Dump()
        self.compare = Compare()
        self.fusion = Fusion()

    def prepare(self):
        util.create_dir(cfg.DATA_ROOT_DIR)
        self.dump.preapre()
        self.graph.prepare()
        self.overflow.prepare()
        self.fusion.prepare()

    def do_auto_check(self, argv):
        """"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--name', dest='vector_compare', help='auto check', action='store_true')
        args = parser.parse_args(argv)

        self.fusion.summary()
        self.overflow.check()
        # vector compare
        if args.vector_compare:
            self.compare.vector_compare()
        #self._check_graph_similarity()
        #self._check_vector()
        #self._check_cast_op()

    def do_check_overflow(self):
        self.overflow.check()

    def do_fusion(self, argv):
        self.fusion.summary()

    def do_vector_compare(self):
        self.compare.vector_compare()

    def do_print_data(self, argv):
        """ print data """
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        args = parser.parse_args(argv)
        self.dump.print_data(args.name)

    def do_list_nodes(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', dest='type', default='', help='list by op type')
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        args = parser.parse_args(argv)
        self.graph.print_op_list(args.type, args.name)

    def do_node_info(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='op name')
        # parser.add_argument('-d', '--data', dest='data', help='show data detail', action='store_true')
        args = parser.parse_args(argv)
        self.graph.print_op(args.name)

    def do_convert_npu_dump(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', help='op name')
        # parser.add_argument('-n', '--name', dest='name', type=list, default=[], help='op name', nargs='+')
        args = parser.parse_args(argv)
        self.graph.print_op(args.name)

    def do_compare_data(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='names', type=str, default=[], help='op name', nargs='+')
        parser.add_argument('-p', '--print', dest='print', default=20, type=int, help='print err data num')
        parser.add_argument('-al', '--atol', dest='atol', default=0.001, type=float, help='set rtol')
        parser.add_argument('-rl', '--rtol', dest='rtol', default=0.001, type=float, help='set atol')
        args = parser.parse_args(argv)
        if len(args.names) < 2:
            LOG.error("compare files less then 2")
            return
        self.compare.compare_data(args.names[0], args.names[1], print_n=args.print)

    def _check_graph_similarity(self):
        """ Check graph similarity """

    def _check_cast_op(self):
        """ Check if there is low precision cast """
