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

import argparse
import atexit
import json
import fcntl
import os
import stat
import sys
from typing import Optional

from modify_pod_config_item import (
    UseSecuritySettingItem,
    CheckImageSha256,
    UseCapability,
    SetImageSha256WhiteList,
    UseHostNetwork,
    UseSeccomp,
    UseStartCommand,
    UseProbe,
    UseRunAsRoot,
    UsePrivilegeEscalation,
    UsePrivileged,
    UseDefaultContainerCap,
    SetRootFsReadOnly,
    EmptyDirVolume,
    ContainerCpuLimit,
    ContainerNpuLimit,
    ContainerMemoryLimit,
    AddHostPath,
    DeleteHostPath,
    MaxContainerNumber,
    MaxTotalModelFileNumber,
    MaxContainerModelFileNumber,
    SystemReservedCPUQuota,
    SystemReservedMemoryQuota
)
from modify_pod_config_logger import ModifyPodConfigLogger
from modify_pod_config_logger import record_operate_log_info
from modify_pod_config_logger import run_log
from modify_pod_config_logger import record_operate_log_error

FILE_MAX_SIZE = 512 * 1024


def _load_config_file(path: str) -> Optional[dict]:
    try:
        if os.path.getsize(path) > FILE_MAX_SIZE:
            run_log.error(f"check json file [{path}] size failed: size too large")
            return {}

        with open(path, "r", encoding="UTF-8") as cfg_file:
            return json.load(cfg_file)
    except Exception as e:
        run_log.error(f"load json file exception {path} {e}")
        return {}


def _save_config_file(path: str, data: dict) -> int:
    try:
        json_data = json.dumps(data, indent=4)
        if len(json_data) > FILE_MAX_SIZE:
            run_log.error("check json data failed: size too large")
            return 1

        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        modes = stat.S_IWUSR | stat.S_IRUSR
        with os.fdopen(os.open(path, flags, modes), "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(json_data)
            return 0

    except Exception as e:
        run_log.error(f"load json file exception {path} {e}")
        return 1


def _init_argument_parser(items: list) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    for item in items:
        parser.add_argument(item.get_argument(), help=item.get_help(), type=item.get_type())
    return parser


def _parse_argument(parser: argparse):
    return parser.parse_args()


def _set_all_item_value(args, items):
    for item in items:
        item.set_value(args)


def _set_all_value(config_data: dict, items: list):
    for item in items:
        item.modify_json_data(config_data)


def _get_config_file_fill_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/podconfig.json")


exit_code = 1


def _exit_func():
    global exit_code
    if exit_code == 2:
        return
    record_operate_log_info(f"modify pod config", "success") if exit_code == 0 else record_operate_log_error(
        f"modify pod config", "fail"
    )


def _log_init() -> int:
    if not ModifyPodConfigLogger().init_logger(log_type="run") or not ModifyPodConfigLogger().init_logger(
            log_type="operate"
    ):
        print(f"logger init fail")
        return 1
    return 0


def _reg_exit_func():
    atexit.register(_exit_func)


def _get_args_items() -> list:
    return [
        UseSecuritySettingItem(),
        CheckImageSha256(),
        UseCapability(),
        UsePrivileged(),
        UsePrivilegeEscalation(),
        UseRunAsRoot(),
        UseProbe(),
        UseStartCommand(),
        UseHostNetwork(),
        UseSeccomp(),
        SetImageSha256WhiteList(),
        UseDefaultContainerCap(),
        SetRootFsReadOnly(),
        EmptyDirVolume(),
        ContainerCpuLimit(),
        ContainerNpuLimit(),
        ContainerMemoryLimit(),
        AddHostPath(),
        DeleteHostPath(),
        MaxContainerNumber(),
        MaxTotalModelFileNumber(),
        MaxContainerModelFileNumber(),
        SystemReservedCPUQuota(),
        SystemReservedMemoryQuota()
    ]


def _parse_args(items):
    parser = _init_argument_parser(items)
    return _parse_argument(parser)


def _modify_pod_config(items) -> int:
    config_file_path = _get_config_file_fill_path()

    data = _load_config_file(config_file_path)
    if not data:
        return 1
    _set_all_value(data, items)
    run_log.info(f"new config is {data}")

    return _save_config_file(config_file_path, data)


def main():
    global exit_code

    if _log_init() != 0:
        exit_code = 1
        return

    _reg_exit_func()

    try:

        items = _get_args_items()

        args = _parse_args(items)

        run_log.info(f"begin to set item value")

        _set_all_item_value(args, items)

        exit_code = _modify_pod_config(items)
    except Exception as e:
        run_log.error(f"modify pod config exception: {e}")
        print(f"modify pod config exception: {e}")
        exit_code = 1


def _is_help(argv):
    global exit_code

    if len(argv) == 2 and (argv[1] == "-h" or argv[1] == "--help"):
        # 退出码标记为2，表示是查询操作，不记录操作日志
        exit_code = 2
        return
    exit_code = 1


if __name__ == "__main__":
    _is_help(sys.argv)
    main()
    exit(exit_code)
