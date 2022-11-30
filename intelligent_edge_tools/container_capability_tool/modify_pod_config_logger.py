# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################

import logging
import os
import pwd
import socket
from pathlib import Path
from logging.handlers import WatchedFileHandler

from modify_pod_config_cmd_executor import CmdExecutor


class _WatchedFileSoftLinkHandler(WatchedFileHandler):
    def _is_file_soft_link(self) -> bool:
        return os.path.islink(self.baseFilename)

    def emit(self, record):
        try:
            if self._is_file_soft_link():
                logging.FileHandler.emit(self, record)
            super().emit(record)
        except Exception:
            self.handleError(record)


class ModifyPodConfigLogger:
    _DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    _MODULE_NAME = "edge_core"

    def _get_module_dir(self) -> str:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")

    def _get_log_dir(self) -> str:
        module_dir = self._get_module_dir()
        return os.path.join(module_dir, "var/log/")

    def _get_log_file_name(self, log_type: str) -> str:
        if log_type == "operate":
            return f"{self._MODULE_NAME}_script_operate.log"
        return f"{self._MODULE_NAME}_{log_type}.log"

    def _get_run_log_format(self) -> str:
        return f"[%(asctime)s] [%(levelname)s] [EdgeCore] " f"[%(funcName)s] [%(filename)s:%(lineno)d] [%(message)s]"

    def _get_operate_log_format(self) -> str:
        return f"[%(asctime)s] [%(levelname)s] [{self._MODULE_NAME}] [%(message)s]"

    def _get_log_format(self, log_type: str) -> str:
        return self._get_run_log_format() if log_type == "run" else self._get_operate_log_format()

    def _create_file_if_not_exists(self, log_path):
        if len(log_path) > 1024:
            return

        if not os.path.exists(log_path):
            with os.fdopen(os.open(log_path, os.O_CREAT, 0o600), "w"):
                pass

    def _is_log_dir_exists(self, log_path):
        return os.path.exists(log_path)

    def _get_log_info(self):
        return {
            "AtlasEdge_log": 0o755,
            "edge_core": 0o700,
        }

    def _check_and_make_dir_recursive(self, log_path):
        paths = log_path.split("/")
        tmp_path = "/"
        log_info_item = self._get_log_info()
        for i in range(1, len(paths)):
            tmp_path = os.path.join(tmp_path, paths[i])
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path, exist_ok=True)
                os.chmod(tmp_path, log_info_item.get(paths[i], 0o755))

    def init_logger(self, log_type="run", log_level=logging.INFO) -> bool:
        log_dir_path = self._get_log_dir()
        log_full_path = os.path.join(log_dir_path, self._get_log_file_name(log_type=log_type))
        try:
            # log_dir_path not exists means: 1.soft link not exist or 2.the dir that soft link point to not exist
            if not self._is_log_dir_exists(log_path=log_dir_path):
                # soft link point to not exist
                if Path(log_dir_path).is_symlink():
                    realpath = os.path.realpath(log_dir_path)
                    self._check_and_make_dir_recursive(log_path=realpath)
                else:
                    return False
            self._create_file_if_not_exists(log_path=log_full_path)
            watch_handler = _WatchedFileSoftLinkHandler(log_full_path)
            formatter = logging.Formatter(self._get_log_format(log_type=log_type), self._DATE_FORMAT)
            watch_handler.setFormatter(formatter)

            logger_instance = logging.getLogger(log_type)
            logger_instance.setLevel(log_level)
            logger_instance.addHandler(watch_handler)
            return True
        except Exception as e:
            print(f"logger init exception: {e}")
            return False


run_log = logging.getLogger("run")

_DEFAULT_OPERATE_IP = "127.0.0.1"
_DEFAULT_OPERATE_USER = "root"
_OPERATE_LOG_USER_LEN = 15
_OPERATE_LOG_IP_LEN = 150
_OPERATE_LOG_MSG_LEN = 100
_OPERATE_LOG_RESULT_LEN = 15

def _get_cur_user() -> str:
    try:
        return pwd.getpwuid(os.geteuid())[0]
    except Exception as e:
        print(f"get current user exception: {e}")
        return _DEFAULT_OPERATE_USER


def _check_ipv4(ip_str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET, ip_str)
        return True
    except socket.error:
        return False


def _check_ipv6(ip_str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET6, ip_str)
        return True
    except socket.error:
        return False


def _ip_format_check(ip_str) -> bool:
    if not _check_ipv4(ip_str) and not _check_ipv6(ip_str):
        return False
    return True


def _exec_who_cmd():
    cmd = "/usr/bin/who am i | awk -F'(' '{print $2}' | awk -F')' '{print $1}'"
    return CmdExecutor.exec_cmd_get_out_put(cmd, 5)


def _parse_who_cmd_result(result):
    if result[0] != 0:
        print(f"exec who fail")
        return _DEFAULT_OPERATE_IP
    lines = result[1].split("\n")
    if not lines:
        print(f"result of who is empty")
        return _DEFAULT_OPERATE_IP
    # 在ipv6的场景下，who命令查出的地址使用"%"分隔IP地址和网卡名称
    ip = lines[0].split("%")[0]
    if not _ip_format_check(ip):
        print(f"result is not ip")
        return _DEFAULT_OPERATE_IP
    return ip


def _get_peer_ip() -> str:
    try:
        result = _exec_who_cmd()
        return _parse_who_cmd_result(result)
    except Exception as e:
        print(f"get current ip exception: {e}")
        return _DEFAULT_OPERATE_IP


def _decorate_log_item(item: str, limit: int) -> str:
    if len(item) > limit:
        return item[0:limit] + "+"
    else:
        return item


def _create_log(msg: str, result: str) -> str:
    deco_user = _decorate_log_item(_get_cur_user(), _OPERATE_LOG_USER_LEN)
    deco_ip = _decorate_log_item(_get_peer_ip(), _OPERATE_LOG_IP_LEN)
    deco_msg = _decorate_log_item(msg, _OPERATE_LOG_MSG_LEN)
    deco_result = _decorate_log_item(result, _OPERATE_LOG_RESULT_LEN)
    return f"{deco_user}@{deco_ip}] [{deco_msg}] [{deco_result}"


def record_operate_log_info(msg: str, result: str):
    print(f"{msg} {result}")
    logging.getLogger("operate").info(_create_log(msg, result))


def record_operate_log_error(msg: str, result: str):
    print(f"{msg} {result}")
    logging.getLogger("operate").error(_create_log(msg, result))
