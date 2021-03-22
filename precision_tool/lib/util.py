import csv
import json
import re
import os
import shutil
import sys
import pexpect
import numpy as np
import logging
import subprocess

from rich.panel import Panel
from rich.layout import Layout
from rich.traceback import install

from rich import print

import config as cfg

install()
try:
    import readline
    readline.parse_and_bind('tab: complete')
except ImportError as import_error:
    print("[cli] Unable to import module: readline.")

# enable rich
ENABLE_RICH = False
try:
    from rich.logging import RichHandler

    ENABLE_RICH = True
except ImportError:
    ENABLE_RICH = False
    RichHandler = None

'''
ENABLE_RICH = False
if ENABLE_RICH:
    logging.basicConfig(level=cfg.LOG_LEVEL, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
    LOG = logging.getLogger("rich")
else:
'''
logging.basicConfig(level=cfg.LOG_LEVEL, format="%(asctime)s (%(process)d) -[%(levelname)s]%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
LOG = logging.getLogger()

GE_GRAPH_BUILD_PROTO_PATTERN = '^ge_proto.*_Build.*txt$'
OFFLINE_DUMP_PATTERN = r"^([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\.([0-9]+)(\.[0-9]+)?\.([0-9]{1,255})"
OFFLINE_DUMP_DECODE_PATTERN =\
    r"^([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\.([0-9]+)(\.[0-9]+)?\.([0-9]{1,255})\.([a-z]+)\.([0-9]{1,255})\.npy$"
OFFLINE_FILE_NAME = 'op_type.op_name.task_id(.stream_id).timestamp'
OP_DEBUG_NAME = 'OpDebug.Node_OpDebug.taskid.timestamp'
CPU_DUMP_DECODE_PATTERN = r"^([A-Za-z0-9_-]+)\.([0-9]+)(\.[0-9]+)?\.([0-9]{1,255})\.npy$"
CPU_FILE_DECODE_NAME = 'op_name.0(.0).timestamp.npy'
OP_DEBUG_PATTERN = r"Opdebug\.Node_OpDebug\.([0-9]+)(\.[0-9]+)?\.([0-9]{1,255})"
OP_DEBUG_DECODE_PATTERN = r"Opdebug\.Node_OpDebug\.([0-9]+)(\.[0-9]+)?\.([0-9]{1,255})\.([a-z]+)\.([0-9]{1,255})\.json"
VECTOR_COMPARE_RESULT_PATTERN = r"result_([0-9]{1,255})\.csv"
TIMESTAMP_DIR_PATTERN = '[0-9]{1,255}'
CSV_SHUFFIX = '.csv'
NUMPY_SHUFFIX = '.npy'


def detect_file(file_name, root_dir):
    """ find file in root dir"""
    result = []
    for dir_path, dir_names, file_names in os.walk(root_dir):
        for name in file_names:
            if name == file_name:
                result.append(dir_path)
    return result


def detect_file_if_not_exist(target_file):
    LOG.info("try to auto detect %s." % target_file)
    res = detect_file(target_file, cfg.CMD_ROOT_PATH)
    if len(res) == 0:
        LOG.error("Cannot find any %s in dir %s" % (target_file, cfg.CMD_ROOT_PATH))
        return cfg.CMD_ROOT_PATH
    LOG.info("Detect [%s] Success. %s" % (target_file, res))
    return res[0]


ATC_PATH = detect_file_if_not_exist('atc')
OPERATOR_CMP_PATH = detect_file_if_not_exist('msaccucmp.pyc')
os.environ['PATH'] = os.environ['PATH'] + ':' + ATC_PATH


class Util(object):
    @staticmethod
    def run_cmd(cmd):
        LOG.debug("[Run CMD]: %s" % cmd)
        subprocess.run(cmd, shell=True)

    @staticmethod
    def empty_dir(dir_path):
        if not os.path.exists(dir_path):
            return True
        if len(os.listdir(dir_path)) == 0:
            return True
        return False

    def auto_run_with_debug_envs(self, line):
        """ auto run """
        if 'DUMP_GE_GRAPH' in os.environ:
            del os.environ['DUMP_GE_GRAPH']
        if 'DUMP_GRAPH_LEVEL' in os.environ:
            del os.environ['DUMP_GRAPH_LEVEL']
        os.environ['CHECK_OVERFLOW'] = "True"
        LOG.info("Run with Overflow check....")
        self.run_cmd(line)
        os.environ['DUMP_GE_GRAPH'] = "2"
        os.environ['DUMP_GRAPH_LEVEL'] = "1"
        os.environ['CHECK_OVERFLOW'] = "False"
        LOG.info("Run with Dump Data....")
        self.run_cmd(line)

    def run_tf_dbg_dump(self, line):
        """ run tf dbg
        set tf debug ui_type='readline'
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
        self.run_cmd(convert_cmd)
        if not os.path.exists(cfg.DUMP_FILES_CPU_CMDS):
            LOG.error("Save tf dump cmd failed")
            return
        for cmd in open(cfg.DUMP_FILES_CPU_CMDS):
            LOG.debug(cmd)
            tf_dbg.expect('tfdbg>')
            tf_dbg.sendline(cmd)
        tf_dbg.expect('tfdbg>')
        tf_dbg.sendline('exit')

    def convert_proto_to_json(self, proto_file_list):
        """ Convert GE proto graphs to json format.
        atc --mode=5 --om=ge_proto_Build.txt --json=xxx.json
        """
        for file in proto_file_list:
            if not re.match(GE_GRAPH_BUILD_PROTO_PATTERN, file):
                continue
            if os.path.exists(cfg.GRAPH_DIR_BUILD + '/' + file + '.json'):
                continue
            cmd = 'atc --mode=5 --om=%s/%s --json=%s/%s.json' % (cfg.GRAPH_DIR_LAST, file, cfg.GRAPH_DIR_BUILD, file)
            self.run_cmd(cmd)
        LOG.info('Finish convert [%s] build graph from proto to json format.' % len(proto_file_list))

    def convert_dump_to_npy(self, src_file, dst_path):
        """ Convert npu dump files to npy format"""
        if not os.path.exists(dst_path):
            LOG.debug("Path[%s] not exist" % dst_path)
            self.create_dir(dst_path)
        cmd = 'python3 %s/msaccucmp.pyc convert -d %s -out %s' % (OPERATOR_CMP_PATH, src_file, dst_path)
        self.run_cmd(cmd)

    def compare_vector(self, dump_dir, cpu_dump_dir, graph_json, result_path):
        cmd = 'python3 %s/msaccucmp.pyc compare -m %s -g %s -f %s -out %s >> %s/log.txt' % (
            OPERATOR_CMP_PATH, dump_dir, cpu_dump_dir, graph_json, result_path, result_path)
        self.run_cmd(cmd)

    def compare(self, npu_file, gpu_file):
        """"""


    @staticmethod
    def _get_newest_dir(path):
        if not os.path.isdir(path):
            LOG.warning("Path[%s] not exists" % path)
            return ''
        paths = os.listdir(path)
        sub_paths = []
        for p in paths:
            if re.match(TIMESTAMP_DIR_PATTERN, p):
                sub_paths.append(p)
        if len(sub_paths) == 0:
            LOG.debug("Path[%s] has no timestamp dirs." % path)
            return ''
        newest_sub_path = sorted(sub_paths)[-1]
        LOG.info("[%d] Dump Dirs[%s], Choose[%s]" % (len(sub_paths), sub_paths, newest_sub_path))
        return newest_sub_path

    @staticmethod
    def _gen_dump_file_info(name, match, dir_path):
        return {
            "file_name": name,
            "op_name": match.group(2),
            "op_type": match.group(1),
            "task_id": int(match.group(3)),
            "dir_path": dir_path,
            "path": os.path.join(dir_path, name),
            "timestamp": int(match.groups()[-1])
        }

    @staticmethod
    def _gen_npu_dump_decode_file_info(name, match, dir_path):
        return {
            "file_name": name,
            "op_type": match.group(1),
            "op_name": match.group(2),
            "task_id": int(match.group(3)),
            "type": match.groups()[-2],
            "idx": int(match.groups()[-1]),
            "timestamp": int(match.groups()[-3]),
            "dir_path": dir_path,
            "path": os.path.join(dir_path, name)
        }

    @staticmethod
    def _gen_cpu_dump_decode_file_info(name, match, dir_path):
        return {
            "file_name": name,
            "op_name": match.group(1),
            "idx": int(match.group(2)),
            "path": os.path.join(dir_path, name),
            "dir_path": dir_path
        }

    @staticmethod
    def _gen_overflow_decode_file_info(name, match, dir_path):
        return {
            "file_name": name,
            "dir_path": dir_path,
            'task_id': int(match.group(1)),
            "path": os.path.join(dir_path, name),
            "type": match.groups()[-2],
            "idx": match.groups()[-1],
            "timestamp": int(match.groups()[-3])
        }

    @staticmethod
    def _gen_vector_compare_result_file_info(name, match, dir_path):
        return {
            "file_name": name,
            "dir_path": dir_path,
            "path": os.path.join(dir_path, name),
            "timestamp": int(match.group(1))
        }

    def list_dump_files(self, path):
        """ List all files in path """
        parent_dirs = {}
        dump_files = {}
        newest_sub_path = self._get_newest_dir(path)
        dump_pattern = re.compile(OFFLINE_DUMP_PATTERN)
        for dir_path, dir_names, file_names in os.walk(os.path.join(path, newest_sub_path)):
            for name in file_names:
                dump_match = dump_pattern.match(name)
                if dump_match is not None:
                    dump_files[name] = self._gen_dump_file_info(name, dump_match, dir_path)
                if dir_path not in parent_dirs:
                    parent_dirs[dir_path] = {}
                parent_dirs[dir_path][name] = dump_files[name]
        return dump_files, parent_dirs

    @staticmethod
    def _list_file_with_pattern(path, pattern, extern_pattern, gen_info_func):
        file_list = {}
        re_pattern = re.compile(pattern)
        for dir_path, dir_names, file_names in os.walk(path):
            for name in file_names:
                match = re_pattern.match(name)
                if match is None:
                    continue
                if extern_pattern != '' and not re.match(extern_pattern, name):
                    continue
                file_list[name] = gen_info_func(name, match, dir_path)
        return file_list

    def list_npu_dump_decode_files(self, path, extern_pattern=''):
        return self._list_file_with_pattern(path, OFFLINE_DUMP_DECODE_PATTERN, extern_pattern,
                                            self._gen_npu_dump_decode_file_info)

    def list_overflow_debug_files(self, path, extern_pattern=''):
        return self._list_file_with_pattern(path, OP_DEBUG_PATTERN, extern_pattern,
                                            self._gen_overflow_file_info)

    def list_debug_decode_files(self, path, extern_pattern=''):
        return self._list_file_with_pattern(path, OP_DEBUG_DECODE_PATTERN, extern_pattern,
                                            self._gen_overflow_decode_file_info)

    def list_cpu_dump_decode_files(self, path, extern_pattern=''):
        return self._list_file_with_pattern(path, CPU_DUMP_DECODE_PATTERN, extern_pattern,
                                            self._gen_cpu_dump_decode_file_info)

    def list_vector_compare_result_files(self, path, extern_pattern=''):
        return self._list_file_with_pattern(path, VECTOR_COMPARE_RESULT_PATTERN, extern_pattern,
                                            self._gen_vector_compare_result_file_info)

    @staticmethod
    def get_file_desc(file_name):
        """ Get File desc"""
        if not os.path.exists(file_name):
            LOG.warning("File[{}] not exist".format(file_name))

    @staticmethod
    def create_dir(path):
        """ create dir """
        if os.path.exists(path):
            return
        try:
            os.makedirs(path, mode=0o700)
        except OSError as err:
            LOG.error("Failed to create {}. {}".format(path, str(err)))

    @staticmethod
    def clear_dir(path, pattern=''):
        if not os.path.exists(path):
            return
        try:
            for f in os.listdir(path):
                if not re.match(pattern, f):
                    continue
                file_path = os.path.join(path, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        except OSError as err:
            LOG.error("Failed to remove {}. {}".format(path, str(err)))

    @staticmethod
    def npy_info(path):
        """
        :param path: npy path
        :return: (shape, dtype)
        """
        if not str(path).endswith(NUMPY_SHUFFIX):
            LOG.error("npy path [{}] invalid".format(path))
            return
        data = np.load(path, allow_pickle=True)
        return data.shape, data.dtype

    def npy_summary(self, path, file_name, extern_content=''):
        target_file = os.path.join(path, file_name)
        if not os.path.exists(target_file):
            LOG.warning("File[{}] not exist".format(target_file))
        self.save_npy_to_txt(target_file)
        data = np.load(target_file)
        content = 'Array: %s' % np.array2string(data)
        content += "\n========\nShape: %s\nDtype: %s\nMax: %s\nMin: %s\nMean: %s\nPath: %s\nTxtFile: %s.txt" % (
            data.shape, data.dtype, np.max(data), np.min(data), np.mean(data), target_file, target_file)
        if extern_content != '':
            content += '\n %s' % extern_content
        self.print_panel(content)

    @staticmethod
    def save_npy_to_txt(src_file, dst_file='', align=0):
        """ Convert npy to txt"""
        if dst_file == '':
            dst_file = src_file + '.txt'
        data = np.load(src_file)
        shape = data.shape
        data = data.flatten()
        if align == 0:
            if len(shape) == 0:
                align = 1
            else:
                align = shape[-1]
        elif data.size() % align != 0:
            pad_array = np.zeros((align - data.size() % align,))
            data = np.append(data, pad_array)
        np.savetxt(dst_file, data.reshape((-1, align)), delimiter=' ', fmt='%g')

    @staticmethod
    def read_csv(path):
        if not str(path).endswith(CSV_SHUFFIX):
            LOG.error("csv path [{}] invalid".format(path))
            return
        rows = []
        with open(path) as f:
            csv_handle = csv.reader(f)
            for row in csv_handle:
                rows.append(row)
        return rows

    @staticmethod
    def print_panel(content, title='', fit=True):
        if fit:
            print(Panel.fit(content, title=title))
        else:
            print(Panel(content, title=title))


util = Util()
