# coding=utf-8
"""
cli
"""
import os
import sys
import argparse
from termcolor import colored
from lib.interactive_cli import InteractiveCli
from lib.precision_tool_exception import PrecisionToolException
from lib.util import util
import config as cfg

INTRODUCE_DOC = \
    "==============<Precision Tool>=================\n" \
    "Usage:\n" \
    "  Single mode:\n" \
    "    Exp:\n" \
    "      python3.7.5 precision_tool/cli.py tf_dump \"sh cpu_train.sh param1 param2\"" \
    "  Interactive mode:\n" \
    "    Exp:\n"


def _run_tf_dbg_dump(argv):
    """Run tf train script to get dump data."""
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, help="tf train command")
    parser.add_argument('-r', '--run_times', dest='run_times', help="Dump data after run command after start tf_debug",
                        type=int, default=2)
    args = parser.parse_args(argv)
    _do_run_tf_dbg_dump(args.command, args.run_times)


def _do_run_tf_dbg_dump(cmd_line, run_times=2):
    """Run tf debug with pexpect, should set tf debug ui_type='readline'"""
    log = util.get_log()
    try:
        import pexpect
        import readline
    except ImportError as import_err:
        log.error("Import failed with err:%s. You can run 'pip3 install pexpect gnureadline' to fix it.", import_err)
        raise PrecisionToolException("Import module error.")
    log.info("======< Auto run tf train process to dump data >======")
    tf_dbg = pexpect.spawn(cmd_line)
    tf_dbg.logfile = open(cfg.DUMP_FILES_CPU_LOG, 'wb')
    for i in range(run_times):
        tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
        log.info("Process %d tf_debug.run", i + 1)
        tf_dbg.sendline('run')
    log.info("Generate tensor name file.")
    tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
    tf_dbg.sendline('lt > %s' % cfg.DUMP_FILES_CPU_NAMES)
    if not os.path.exists(cfg.DUMP_FILES_CPU_NAMES):
        log.error("Failed to get tensor name in tf_debug.")
        raise PrecisionToolException("Get tensor name in tf_debug failed.")
    log.info("Save tensor name success. Generate tf dump commands from file: %s", cfg.DUMP_FILES_CPU_NAMES)
    convert_cmd = "timestamp=$[$(date +%s%N)/1000]; cat " + cfg.DUMP_FILES_CPU_NAMES + \
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
        tf_dbg.expect('tfdbg>')
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
    log.info("Start run NPU script with dump data....")
    ret = util.execute_command(cmd)
    log.info("Finish run NPU script with dump data. ret [%s]", ret)
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
            log.warning("Unknown command:", sys.argv[1])
            print(INTRODUCE_DOC)
        exit(0)
    log.info("Interactive command mode.")
    cli = InteractiveCli()
    try:
        cli.cmdloop(intro=cli.__doc__)
    except KeyboardInterrupt:
        log.info("Bye.......")
    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except PrecisionToolException as pte:
        util.get_log().error(pte.error_info)
