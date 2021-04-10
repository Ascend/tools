# coding=utf-8
"""
cli
"""
import os
import sys
from termcolor import colored
from lib.interactive_cli import InteractiveCli
from lib.util import util
import config as cfg

INTRODUCE_DOC = \
    "==============<Precision Tool>=================\n" \
    "Usage:\n" \
    "  Single mode:\n" \
    "    Exp:\n" \
    "      python3.7.5 precision_tool/cli.py tf_dump \"sh cpu_train.sh param1 param2\"" \
    "  Single mode:\n" \
    "    Exp:\n"

def _run_tf_dbg_dump(cmd_line):
    """ run tf debug
    should set tf debug ui_type='readline'
    """
    log = util.get_log()
    try:
        import pexpect
    except ImportError as import_err:
        log.error("Import pexpect failed with err:%s. You can run 'pip3 install pexpect' to fix it.", import_err)
        return
    tf_dbg = pexpect.spawn(cmd_line)
    tf_dbg.logfile = open(cfg.DUMP_FILES_CPU_LOG, 'wb')
    tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
    tf_dbg.getecho()
    tf_dbg.sendline('run')
    tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
    tf_dbg.sendline('lt > %s' % cfg.DUMP_FILES_CPU_NAMES)
    convert_cmd = "timestamp=$[$(date +%s%N)/1000]; cat " + cfg.DUMP_FILES_CPU_NAMES + \
                  " | awk '{print \"pt\",$4,$4}'| awk '{gsub(\"/\", \"_\", $3); gsub(\":\", \".\", $3);" \
                  "print($1,$2,\"-n 0 -w " + cfg.DUMP_FILES_CPU + "/" + \
                  "\"$3\".\"\"'$timestamp'\"\".npy\")}' > " + cfg.DUMP_FILES_CPU_CMDS
    util.execute_command(convert_cmd)
    if not os.path.exists(cfg.DUMP_FILES_CPU_CMDS):
        log.error("Save tf dump cmd failed")
        return
    for cmd in open(cfg.DUMP_FILES_CPU_CMDS):
        log.debug(cmd)
        # tf_dbg.expect('tfdbg>')
        tf_dbg.sendline(cmd)
    tf_dbg.expect('tfdbg>')
    tf_dbg.sendline('exit')
    log.info('Finish save tf data')


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
    print(cmd)
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
            _run_tf_dbg_dump(cmd_line)
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
    main()
