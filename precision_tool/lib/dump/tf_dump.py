# coding=utf-8
import os
import re
import time
import sys
from ..util.util import util
from ..util.constant import Constant
from ..util.precision_tool_exception import catch_tool_exception
from ..util.precision_tool_exception import PrecisionToolException
from ..config import config as cfg


class TfDump(object):
    def __init__(self, dump_root=cfg.TF_DUMP_DIR):
        self.log = util.get_log()
        self.dump_root = dump_root
        self.dump_files = None

    def prepare(self):
        if not os.path.exists(self.dump_root):
            util.create_dir(self.dump_root)
        self._parse_dump_files()

    def get_dump_files_by_op(self, op):
        """Get cpu dump files by op"""
        tf_files = {}
        for output in op.outputs():
            if output.data_dump_origin_name() != '':
                tf_files.update(self.get_dump_files_by_name(output.data_dump_origin_name()))
        if len(tf_files) == 0:
            tf_files.update(self.get_dump_files_by_name(op.name()))
        return tf_files

    def get_dump_files_by_name(self, name, likely=False):
        match_name = name.replace('/', '_')
        if not likely:
            match_name = match_name.replace('.', '_') + '\\.'
        tf_files = {}
        for f in self.dump_files:
            if re.match(match_name, f):
                tf_files[f] = self.dump_files[f]
        return tf_files

    @catch_tool_exception
    def op_dump_summary(self, op):
        # cpu dump info
        if op is None:
            return ''
        cpu_dump_txt = ['TfDumpOutput:']
        cpu_dump_files = self.get_dump_files_by_op(op)
        cpu_dump_file_list = sorted(cpu_dump_files.values(), key=lambda x: x.timestamp)
        for cpu_dump_file in cpu_dump_file_list:
            cpu_dump_txt.append(' -[green][%s][/green] %s' % (cpu_dump_file.idx, cpu_dump_file.file_name))
            cpu_dump_txt.append('   └─ [yellow]%s[/yellow]' % util.gen_npy_info_txt(cpu_dump_file.path))
        return Constant.NEW_LINE.join(cpu_dump_txt)

    def _parse_dump_files(self):
        self.dump_files = util.list_cpu_dump_decode_files(self.dump_root)

    def run_tf_dbg_dump(self, cmd_line=None):
        """Run tf train script to get dump data."""
        if os.path.exists(cfg.TF_DEBUG_DUMP_DIR) and len(os.listdir(cfg.TF_DEBUG_DUMP_DIR)) != 0:
            self.log.info("TF offline debug path [%s] is not empty, will analyze it directly." % cfg.TF_DEBUG_DUMP_DIR)
        elif cmd_line is not None:
            self.log.info("Run command: %s" % cmd_line)
            util.execute_command(cmd_line)
            self.log.info("Run finish, start analyze TF dump.")
        if not os.path.exists(cfg.TF_DEBUG_DUMP_DIR) or len(os.listdir(cfg.TF_DEBUG_DUMP_DIR)) == 0:
            raise PrecisionToolException("Empty tf debug dir. %s" % cfg.TF_DEBUG_DUMP_DIR)
        run_dirs = os.listdir(cfg.TF_DEBUG_DUMP_DIR)
        run_dirs.sort()
        # create dirs
        util.create_dir(cfg.TF_DUMP_DIR)
        util.create_dir(cfg.TMP_DIR)
        # extra the last run dir
        for run_dir in run_dirs:
            time.sleep(1)
            command = "%s -m tensorflow.python.debug.cli.offline_analyzer --ui_type readline --dump_dir %s" % (
                util.python, os.path.join(cfg.TF_DEBUG_DUMP_DIR, run_dir))
            self._do_run_tf_dbg_dump(command, 0)

    @staticmethod
    def _make_pt_commands(tensor_name_path):
        pt_command_list = []
        tensor_count = {}
        with open(tensor_name_path) as tensor_name_file:
            # skip 3 line
            next(tensor_name_file)
            next(tensor_name_file)
            next(tensor_name_file)
            # start to convert tensor to pt command
            for line in tensor_name_file:
                new_line = line.strip()
                tensor_name = new_line[new_line.rfind(' ') + 1:]
                if tensor_name not in tensor_count:
                    tensor_count[tensor_name] = 0
                else:
                    tensor_count[tensor_name] += 1

                npy_file_name = "%s.%s.npy" % (tensor_name.replace("/", "_").replace(":", "."),
                                               str(round(time.time() * 1000000)))
                pt_command_list.append("pt %s -n %d -w %s" %
                                       (tensor_name, tensor_count[tensor_name],
                                        os.path.join(cfg.TF_DUMP_DIR, npy_file_name)))
        return pt_command_list

    def _do_run_tf_dbg_dump(self, cmd_line, run_times=2):
        """Run tf debug with pexpect, should set tf debug ui_type='readline'"""
        try:
            import pexpect
            import readline
        except ImportError as import_err:
            self.log.error("Import failed with err:%s. You can run "
                           "'pip3 install pexpect gnureadline pyreadline' to fix it.",
                           import_err)
            raise PrecisionToolException("Import module error.")
        self.log.info("======< Auto run tf train process to dump data >======")
        self.log.info("Send run times: %d", run_times)
        tf_dbg = pexpect.spawn(cmd_line)
        # tf_dbg.logfile = open(cfg.DUMP_FILES_CPU_LOG, 'wb')
        tf_dbg.logfile = sys.stdout.buffer
        for i in range(run_times):
            tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
            self.log.info("Process %d tf_debug.run", i + 1)
            tf_dbg.sendline('run')
        self.log.info("Generate tensor name file.")
        tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
        tf_dbg.sendline('lt > %s' % cfg.TF_TENSOR_NAMES)
        tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
        if not os.path.exists(cfg.TF_TENSOR_NAMES):
            self.log.error("Failed to get tensor name in tf_debug.")
            raise PrecisionToolException("Get tensor name in tf_debug failed.")
        self.log.info("Save tensor name success. Generate tf dump commands from file: %s", cfg.TF_TENSOR_NAMES)
        pt_commands = self._make_pt_commands(cfg.TF_TENSOR_NAMES)
        self.log.info("Pt %d tensors." % len(pt_commands))
        for cmd in pt_commands:
            self.log.debug(cmd.strip())
            tf_dbg.sendline(cmd.strip())
            tf_dbg.expect('tfdbg>', timeout=cfg.TF_DEBUG_TIMEOUT)
        tf_dbg.sendline('exit')
        self.log.info('Finish dump tf data')
