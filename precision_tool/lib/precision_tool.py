import argparse
import os

import pexpect
from lib.overflow import Overflow
from lib.dump import Dump
from lib.graph import Graph
from lib.compare import Compare
from lib.fusion import Fusion
from lib.util import util
from lib.util import LOG
import config as cfg

# env flags
FLAG_DUMP_GE_GRAPH = 'DUMP_GE_GRAPH'
FLAG_DUMP_GRAPH_LEVEL = 'DUMP_GRAPH_LEVEL'
FLAG_CHECK_OVERFLOW = 'CHECK_OVERFLOW'


class PrecisionTool(object):
    def __init__(self):
        """init"""
        self.graph = Graph()
        self.overflow = Overflow()
        self.dump = Dump()
        self.compare = Compare()
        self.fusion = Fusion()

    def prepare(self):
        """prepare"""
        util.create_dir(cfg.DATA_ROOT_DIR)
        self.dump.preapre()
        self.graph.prepare()
        self.overflow.prepare()
        self.fusion.prepare()

    def do_auto_check(self, argv):
        """auto check"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--name', dest='vector_compare', help='auto check', action='store_true')
        args = parser.parse_args(argv)
        # vector compare
        if args.vector_compare:
            self.do_vector_compare()
        self.do_check_fusion()
        self.do_check_overflow()
        self.do_check_cast()
        # self._check_graph_similarity()

    def do_check_overflow(self):
        """check overflow"""
        self.overflow.check()

    def do_check_cast(self):
        self.graph.check_cast()

    def do_check_dtype(self):
        """Check input/output dtype"""
        self.graph.check_dtype()

    def do_check_fusion(self, argv=None):
        """print fusion info summary"""
        self.fusion.check()

    def do_vector_compare(self, argv=None):
        """do vector compare"""
        self.compare.vector_compare()

    def do_print_data(self, argv):
        """print tensor data"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        args = parser.parse_args(argv)
        self.dump.print_data(args.name)

    def do_list_nodes(self, argv):
        """list op nodes in graph"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', dest='type', default='', help='list by op type')
        parser.add_argument('-n', '--name', dest='name', default='', help='list by op name')
        parser.add_argument('-f', '--fusion', dest='fusion', default='', help='list by op fusion pass')
        args = parser.parse_args(argv)
        self.graph.print_op_list(args.type, args.name, args.fusion)

    def do_list_dump(self, argv):
        """List dump files"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--dir', dest='dir')
        parser.add_argument('-n', '--name', dest='name')
        self.dump.list_dump(argv.dir, argv.name)

    def do_node_info(self, argv):
        """print op node info"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', default='', help='op name')
        args = parser.parse_args(argv)
        self.graph.print_op(args.name)

    def do_convert_npu_dump(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--name', dest='name', help='op name')
        parser.add_argument('-f', '--format', dest='format', help='target format')
        args = parser.parse_args(argv)
        self.dump.convert_npu_dump(args.name, args.format)

    def do_convert_all_npu_dump(self):
        self.dump.decode_all_npu_dump()

    def do_compare_data(self, argv):
        """compare two tensor"""
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

    @staticmethod
    def auto_run_with_debug_envs(cmd):
        """ auto run """
        if FLAG_DUMP_GE_GRAPH in os.environ:
            del os.environ[FLAG_DUMP_GE_GRAPH]
        if FLAG_DUMP_GRAPH_LEVEL in os.environ:
            del os.environ[FLAG_DUMP_GRAPH_LEVEL]

        # set check overflow flag
        os.environ[FLAG_CHECK_OVERFLOW] = "True"
        LOG.info("Run NPU script with overflow check....")
        util.execute_command(cmd)
        LOG.info("Finish run NPU script with overflow check.")

        # set dump ge flag
        os.environ[FLAG_DUMP_GE_GRAPH] = "2"
        os.environ[FLAG_DUMP_GRAPH_LEVEL] = "1"
        os.environ[FLAG_CHECK_OVERFLOW] = "False"
        LOG.info("Run NPU script with dump data....")
        util.execute_command(cmd)
        LOG.info("Finish run NPU script with dump data.")

    @staticmethod
    def run_tf_dbg_dump(line):
        """ run tf debug
        should set tf debug ui_type='readline'
        """
        tf_dbg = pexpect.spawn(line)
        tf_dbg.logfile = open(cfg.DUMP_FILES_CPU_LOG, 'wb')
        tf_dbg.expect('tfdbg>')
        tf_dbg.getecho()
        tf_dbg.sendline('run')
        tf_dbg.expect('tfdbg>')
        tf_dbg.sendline('lt > %s' % cfg.DUMP_FILES_CPU_NAMES)
        convert_cmd = "timestamp=$[$(date +%s%N)/1000]; cat " + cfg.DUMP_FILES_CPU_NAMES + \
                      " | awk '{print \"pt\",$4,$4}'| awk '{gsub(\"/\", \"_\", $3); gsub(\":\", \".\", $3);" \
                      "print($1,$2,\"-n 0 -w " + cfg.DUMP_FILES_CPU + \
                      "\"$3\".\"\"'$timestamp'\"\".npy\")}' > " + cfg.DUMP_FILES_CPU_CMDS
        util.execute_command(convert_cmd)
        if not os.path.exists(cfg.DUMP_FILES_CPU_CMDS):
            LOG.error("Save tf dump cmd failed")
            return
        for cmd in open(cfg.DUMP_FILES_CPU_CMDS):
            LOG.debug(cmd)
            tf_dbg.expect('tfdbg>')
            tf_dbg.sendline(cmd)
        tf_dbg.expect('tfdbg>')
        tf_dbg.sendline('exit')
        LOG.info('Finish save tf data')

    def check_graph_similarity(self):
        """ Check graph similarity """
