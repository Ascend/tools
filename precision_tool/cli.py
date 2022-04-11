# coding=utf-8
"""
cli
"""
import os
import sys

from lib.precision_tool import PrecisionTool
from lib.train.train_analysis import TrainAnalysis
from lib.interactive_cli import InteractiveCli
from lib.util.precision_tool_exception import PrecisionToolException
from lib.util.util import util
from lib.dump.tf_dump import TfDump
from lib.adapter.msquickcmp_adapter import MsQuickCmpAdapter
from lib.config import config as cfg

INTRODUCE_DOC = \
    "==============<Precision Tool>=================\n" \
    "Usage:\n" \
    "  Single mode:\n" \
    "    Exp:\n" \
    "      Dump TF data:\n" \
    "       > python3.7.5 precision_tool/cli.py tf_dump \n" \
    "      Adapt msquickcmp data:\n" \
    "       > python3.7.5 precision_tool/cli.py infer [data path of msquickcmp output] \n" \
    "  Interactive mode:\n" \
    "    Exp:\n" \
    "      Start command line:\n" \
    "       > python3.7.5 precision_tool/cli.py\n"


def _run_tf_dbg_dump(cmdline):
    """ Generate tf dump files with tf debug files."""
    tf_dump = TfDump()
    tf_dump.run_tf_dbg_dump(cmdline)


def _unset_flags():
    if cfg.PRECISION_TOOL_OVERFLOW_FLAG in os.environ:
        del os.environ[cfg.PRECISION_TOOL_OVERFLOW_FLAG]
    if cfg.PRECISION_TOOL_DUMP_FLAG in os.environ:
        del os.environ[cfg.PRECISION_TOOL_DUMP_FLAG]


def _run_npu_dump(cmd):
    """Deprecate function."""
    _unset_flags()
    log = util.get_log()
    os.environ[cfg.PRECISION_TOOL_DUMP_FLAG] = 'True'
    log.info("Start run NPU script with dump data.")
    ret = util.execute_command(cmd)
    log.info("Finish run NPU script with dump data. ret [%s]", ret)
    _unset_flags()


def _run_npu_overflow(cmd):
    """Deprecate function."""
    _unset_flags()
    log = util.get_log()
    os.environ[cfg.PRECISION_TOOL_OVERFLOW_FLAG] = 'True'
    log.info("Start run NPU script with overflow check process....")
    ret = util.execute_command(cmd)
    log.info("Finish run NPU script with overflow check process. ret [%s]", ret)
    precision_tool = PrecisionTool()
    precision_tool.prepare()
    precision_tool.do_check_overflow()
    _unset_flags()


def _run_infer_adapter(output_path):
    """ Run precision_tool with msquickcmp output data
    :param output_path: msquickcmp output path
    :return: None
    """
    adapter = MsQuickCmpAdapter(output_path)
    adapter.run()
    _run_interactive_cli()


def _run_interactive_cli(cli=None):
    """ Run precision_tool in interactive mode
    :param cli:
    :return:
    """
    util.get_log().info("Interactive command mode.")
    if cli is None:
        cli = InteractiveCli()
    try:
        cli.cmdloop(intro="Enjoy!")
    except KeyboardInterrupt:
        util.get_log().info("Bye.......")


def _run_cli_with_data(data_path):
    """ Run precision with specific data path, default is precision_data."""
    cfg.DATA_ROOT_DIR = data_path
    _run_interactive_cli()


function_list = {
    'tf_dump': _run_tf_dbg_dump,
    'npu_dump': _run_npu_dump,
    'npu_overflow': _run_npu_overflow,
    'infer': _run_infer_adapter,
    'data': _run_cli_with_data
}


def main():
    while len(sys.argv) > 1:
        util.get_log().info("Single command mode.")
        function_key = sys.argv[1]
        cmd_line = sys.argv[2] if len(sys.argv) > 2 else None
        if function_key in function_list:
            return function_list[function_key](cmd_line)
        precision_tool = PrecisionTool()
        return precision_tool.single_cmd(sys.argv)
    _run_interactive_cli()


if __name__ == '__main__':
    try:
        main()
    except PrecisionToolException as pte:
        util.get_log().error(pte.error_info)
