# coding=utf-8
"""
cli
"""
import cmd
from lib.precision_tool import PrecisionTool
from lib.util import util


class Cli(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "PrecisionTool > "
        self.precision_tool = None
        self._prepare()

    def default(self, line: str) -> bool:
        util.execute_command(line)
        return False

    def _prepare(self):
        self.precision_tool = PrecisionTool()
        self.precision_tool.prepare()

    def do_ac(self, line=''):
        """Auto check."""
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_auto_check(argv)

    def do_run(self, line=''):
        """Run any shell command"""
        util.execute_command(line)

    def do_npu_run(self, line=''):
        """Run npu npu script with debug envs(overflow/dump) to generate dump data:\n usage: npu_run [start npu command]
        """
        self.precision_tool.auto_run_with_debug_envs(line)
        self._prepare()

    def do_tf_run(self, line=''):
        """Run tf cpu script with tfdbg to generate golden data:\n usage: tf_run [tf cpu start command]"""
        self.precision_tool.run_tf_dbg_dump(line)
        self._prepare()

    def do_ls(self, line=''):
        """List ops: \n usage: ls (op(default)/dump) -n [op_name] -t [op_type]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) > 0 and argv[0] == 'dump':
            return self.precision_tool.do_list_dump(argv[1:])
        self.precision_tool.do_list_nodes(argv)

    def do_ni(self, line=''):
        """Print node info:\n usage: ni (-n) [op_name]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) == 1:
            argv.insert(0, '-n')
        self.precision_tool.do_node_info(argv)

    def do_dc(self, line=''):
        """Convert npu dump by op names:\n usage: dc (-n) [npu dump file] -f [target format]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) == 0:
            return self.precision_tool.do_convert_all_npu_dump()
        if argv[0] != '-n':
            argv.insert(0, '-n')
        self.precision_tool.do_convert_npu_dump(argv)

    def do_vc(self, line=''):
        """Do vector compare: \n usage: vc """
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_vector_compare(argv)

    def do_pt(self, line=''):
        """Print data info:\n usage: pt (-n) [*.npy]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) == 1:
            argv.insert(0, '-n')
        self.precision_tool.do_print_data(argv)

    def do_fu(self, line=''):
        """Fusion summary"""
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_check_fusion(argv)

    def do_cp(self, line=''):
        """Compare two data file """
        argv = line.split(' ') if line != '' else []
        argv.insert(0, '-n')
        self.precision_tool.do_compare_data(argv)

    def do_cc(self, line=''):
        """Check cast"""
        self.precision_tool.do_check_cast()

    def do_cd(self, line=''):
        """Check dtype"""
        self.precision_tool.do_check_dtype()

    def do_help(self, arg: str):
        # print(arg)
        super(Cli, self).do_help(arg)


if __name__ == '__main__':
    cli = Cli()
    try:
        cli.cmdloop(intro="Bingo!")
    except KeyboardInterrupt:
        print("Bye!")
