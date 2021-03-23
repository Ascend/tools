"""
cli

"""
import cmd
from lib.precision_tool import PrecisionTool
from lib.util import util


class BaseCli(cmd.Cmd):
    def default(self, line: str) -> bool:
        util.run_cmd(line)
        return False

    @staticmethod
    def do_exit(line='') -> bool:
        """Exit command line"""
        return True

    @staticmethod
    def do_q(line='') -> bool:
        """Exit command line"""
        return True

    @staticmethod
    def do_quit(line='') -> bool:
        """Exit command line"""
        return True


class CompareCli(BaseCli):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "PrecisionTool[Compare] > "


class Cli(BaseCli):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "PrecisionTool > "
        self.compare_cli = CompareCli()
        self.precision_tool = None
        self._prepare()

    def _prepare(self):
        self.precision_tool = PrecisionTool()
        self.precision_tool.prepare()

    def do_ac(self, line=''):
        """Auto check."""
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_auto_check(argv)

    def do_run(self, line=''):
        """Run any shell command"""
        util.run_cmd(line)

    def do_npu_run(self, line=''):
        """Run npu npu script with debug envs(overflow/dump) to generate dump data:\n usage: npu_run [start npu command]
        """
        util.auto_run_with_debug_envs(line)
        self._prepare()

    def do_tf_run(self, line=''):
        """Run tf cpu script with tfdbg to generate golden data:\n usage: tf_run [tf cpu start command]"""
        util.run_tf_dbg_dump(line)
        self._prepare()

    def do_ls(self, line=''):
        """List ops: \n usage: ls -n [op_name] -t [op_type]"""
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_list_nodes(argv)

    def do_ni(self, line=''):
        """Print node info:\n usage: ni (-n) [op_name]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) == 1:
            argv.insert(0, '-n')
        self.precision_tool.do_node_info(argv)

    def do_dc(self, line=''):
        """ convert npu dump by op names """
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_convert_npu_dump(argv)

    def do_vc(self, line=''):
        """Do vector compare: \n usage: vc """
        self.precision_tool.do_vector_compare()

    def do_pt(self, line=''):
        """Print data info:\n usage: pt (-n) [*.npy]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) == 1:
            argv.insert(0, '-n')
        self.precision_tool.do_print_data(argv)

    def do_fu(self, line=''):
        """Fusion summary"""
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_fusion(argv)

    def do_cp(self, line=''):
        """ Compare two data file """
        argv = line.split(' ') if line != '' else []
        argv.insert(0, '-n')
        self.precision_tool.do_compare_data(argv)

    '''
    def do_li(self, line=''):
        """ List input ops """

    def do_lo(self, line=''):
        """ List output ops """

    def do_compare(self, args):
        """ """
        LOG.info(args)
        self.compare_cli.cmdloop(intro="Bingo[Compare]!")
    '''


if __name__ == '__main__':
    cli = Cli()
    try:
        cli.cmdloop(intro="Bingo!")
    except KeyboardInterrupt:
        print("Bye!")
