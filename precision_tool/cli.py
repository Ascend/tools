# coding=utf-8
"""
cli
"""
import os
import sys
import argparse
import time

from termcolor import colored
from lib.precision_tool import PrecisionTool
from lib.interactive_cli import InteractiveCli
from lib.precision_tool_exception import PrecisionToolException
from lib.util import util
import config as cfg


INTRODUCE_DOC = \
    "==============<Precision Tool>=================\n" \
    "Usage:\n" \
    "  Single mode:\n" \
    "    Exp:\n" \
    "      Dump TF data:\n" \
    "       > python3.7.5 precision_tool/cli.py tf_dump \"sh cpu_train.sh param1 param2\" \n" \
    "      Dump NPU data:\n" \
    "       > python3.7.5 precision_tool/cli.py npu_dump \"sh npu_train.sh param1 param2\" \n" \
    "      Check NPU overflow:\n" \
    "       > python3.7.5 precision_tool/cli.py npu_overflow \"sh npu_train.sh param1 param2\" \n" \
    "  Interactive mode:\n" \
    "    Exp:\n" \
    "      Start command line:\n" \
    "       > python3.7.5 precision_tool/cli.py\n"


def _run_tf_dbg_dump(argv):
    """Run tf train script to get dump data."""
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, default=None, help="tf train command")
    args = parser.parse_args(argv)
    log = util.get_log()
    if os.path.exists(cfg.DUMP_FILES_CPU_DEBUG) and len(os.listdir(cfg.DUMP_FILES_CPU_DEBUG)) != 0:
        log.info("TF offline debug path [%s] is not empty, will analyze it directly." % cfg.DUMP_FILES_CPU_DEBUG)
    elif args.command is not None:
        log.info("Run command: %s" % args.command)
        util.execute_command(args.command)
        log.info("Run finish, start analyze TF dump.")
    if not os.path.exists(cfg.DUMP_FILES_CPU_DEBUG) or len(os.listdir(cfg.DUMP_FILES_CPU_DEBUG)) == 0:
        raise PrecisionToolException("Empty tf debug dir. %s" % cfg.DUMP_FILES_CPU_DEBUG)
    run_dirs = os.listdir(cfg.DUMP_FILES_CPU_DEBUG)
    run_dirs.sort()
    # extra the last run dir
    # run_dir = run_dirs[-1]
    # log.info("Find %s run dirs, will choose the last one: %s" % (run_dirs, run_dir))
    for run_dir in run_dirs:
        time.sleep(1)
        command = "%s -m tensorflow.python.debug.cli.offline_analyzer --ui_type readline --dump_dir %s" % (
            cfg.PYTHON, os.path.join(cfg.DUMP_FILES_CPU_DEBUG, run_dir))
        _do_run_tf_dbg_dump(command, 0)


def _do_run_tf_dbg_dump(cmd_line, run_times=2):
    """Run tf debug with pexpect, should set tf debug ui_type='readline'"""
    log = util.get_log()
    try:
        import pexpect
        import readline
    except ImportError as import_err:
        log.error("Import failed with err:%s. You can run 'pip3 install pexpect gnureadline pyreadline' to fix it.",
                  import_err)
        raise PrecisionToolException("Import module error.")
    log.info("======< Auto run tf train process to dump data >======")
    log.info("Send run times: %d", run_times)
    tf_dbg = pexpect.spawn(cmd_line)
    # tf_dbg.logfile = open(cfg.DUMP_FILES_CPU_LOG, 'wb')
    tf_dbg.logfile = sys.stdout.buffer
    for i in range(run_times):
        tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
        log.info("Process %d tf_debug.run", i + 1)
        tf_dbg.sendline('run')
    log.info("Generate tensor name file.")
    tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
    tf_dbg.sendline('lt > %s' % cfg.DUMP_FILES_CPU_NAMES)
    tf_dbg.expect('tfdbg>')
    if not os.path.exists(cfg.DUMP_FILES_CPU_NAMES):
        log.error("Failed to get tensor name in tf_debug.")
        raise PrecisionToolException("Get tensor name in tf_debug failed.")
    log.info("Save tensor name success. Generate tf dump commands from file: %s", cfg.DUMP_FILES_CPU_NAMES)
    convert_cmd = "timestamp=" + str(int(time.time())) + "; cat " + cfg.DUMP_FILES_CPU_NAMES + \
                  " | awk '{print \"pt\",$4,$4}'| awk '{gsub(\"/\", \"_\", $3); gsub(\":\", \".\", $3);" \
                  "print($1,$2,\"-n 0 -w " + cfg.DUMP_FILES_CPU + "/" + \
                  "\"$3\".\"\"'$timestamp'\"\".npy\")}' > " + cfg.DUMP_FILES_CPU_CMDS
    util.execute_command(convert_cmd)
    if not os.path.exists(cfg.DUMP_FILES_CPU_CMDS):
        log.error("Save tf dump cmd failed")
        raise PrecisionToolException("Failed to generate tf dump command.")
    log.info("Generate tf dump commands. Start run commands in file: %s", cfg.DUMP_FILES_CPU_CMDS)
    for cmd in open(cfg.DUMP_FILES_CPU_CMDS):
        log.debug(cmd.strip())
        tf_dbg.sendline(cmd.strip())
        tf_dbg.expect('tfdbg>')
    tf_dbg.sendline('exit')
    log.info('Finish dump tf data')


def _unset_flags():
    if cfg.PRECISION_TOOL_OVERFLOW_FLAG in os.environ:
        del os.environ[cfg.PRECISION_TOOL_OVERFLOW_FLAG]
    if cfg.PRECISION_TOOL_DUMP_FLAG in os.environ:
        del os.environ[cfg.PRECISION_TOOL_DUMP_FLAG]


def _run_npu_dump(cmd):
    _unset_flags()
    log = util.get_log()
    os.environ[cfg.PRECISION_TOOL_DUMP_FLAG] = 'True'
    log.info("Start run NPU script with dump data.")
    ret = util.execute_command(cmd)
    log.info("Finish run NPU script with dump data. ret [%s]", ret)
    _unset_flags()


def _run_npu_overflow(cmd):
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


def main():
    log = util.get_log()
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            print(INTRODUCE_DOC)
            sys.exit(0)
        log.info("Single command mode.")
        cmd_line = sys.argv[2]
        if sys.argv[1] == 'tf_dump':
            _run_tf_dbg_dump(sys.argv[2:])
        elif sys.argv[1] == 'npu_dump':
            _run_npu_dump(cmd_line)
        elif sys.argv[1] == 'npu_overflow':
            _run_npu_overflow(cmd_line)
        else:
            precision_tool = PrecisionTool()
            precision_tool.single_cmd(sys.argv)
        exit(0)
    log.info("Interactive command mode.")
    cli = InteractiveCli()
    try:
        cli.cmdloop(intro="Enjoy!")
    except KeyboardInterrupt:
        log.info("Bye.......")
    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except PrecisionToolException as pte:
        util.get_log().error(pte.error_info)
