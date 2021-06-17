# coding=utf-8
import cmd
from .util import util
from .precision_tool import PrecisionTool

HEADER = r"""    ____                 _      _           ______            __
   / __ \________  _____(_)____(_)___  ____/_  __/___  ____  / /
  / /_/ / ___/ _ \/ ___/ / ___/ / __ \/ __ \/ / / __ \/ __ \/ /
 / ____/ /  /  __/ /__/ (__  ) / /_/ / / / / / / /_/ / /_/ / /
/_/   /_/   \___/\___/_/____/_/\____/_/ /_/_/  \____/\____/_/"""

HELP_AC = "Run auto check function, use [-c] to start vector compare process.\n" \
          "  usage: ac (-c) \n"
HELP_RUN = "Run any shell command.\n" \
           "  usage: (run) vim tensor_name.txt \n"
HELP_PT = "Print npy tensor, use [-c] to convert and save to txt file.\n" \
          "  usage: pt (-c) [tensor_name.npy] \n"


class InteractiveCli(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "PrecisionTool > "
        self.precision_tool = None
        util.print_panel(HEADER)
        self._prepare()

    def default(self, line=''):
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

    def do_ls(self, line=''):
        """List ops: \n usage: ls (op(default)/dump) -n [op_name] -t [op_type]"""
        argv = line.split(' ') if line != '' else []
        if len(argv) > 0 and argv[0] == 'dump':
            return self.precision_tool.do_list_dump(argv[1:])
        self.precision_tool.do_list_nodes(argv)

    def do_ni(self, line=''):
        """Print node info:\n usage: ni (-n) [op_name]"""
        argv = line.split(' ') if line != '' else []
        if '-n' not in argv and '-h' not in argv:
            argv.insert(0, '-n')
        self.precision_tool.do_node_info(argv)

    def do_dc(self, line=''):
        """Convert npu dump by op names:\n usage: dc (-n) [npu dump file] -f [target format]"""
        argv = line.split(' ') if line != '' else []
        # if len(argv) == 0:
        #    return self.precision_tool.do_convert_all_npu_dump()
        if '-n' not in argv:
            argv.insert(0, '-n')
        self.precision_tool.do_convert_npu_dump(argv)

    def do_vc(self, line=''):
        """Do vector compare: \n usage: vc """
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_vector_compare(argv)

    def do_vcs(self, line=''):
        """Do vector compare summary"""
        argv = line.split(' ') if line != '' else []
        self.precision_tool.do_vector_compare_summary(argv)

    def do_pt(self, line=''):
        """Print data info:\n usage: pt (-n) [*.npy] (-c)\n   -c: convert and save to txt file"""
        argv = line.split(' ') if line != '' else []
        if len(argv) > 0 and argv[0] != '-n' and argv[0] != '-c':
            argv.insert(0, '-n')
        self.precision_tool.do_print_data(argv)

    def do_cp(self, line=''):
        """Compare two data file """
        argv = line.split(' ') if line != '' else []
        argv.insert(0, '-n')
        self.precision_tool.do_compare_data(argv)
