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

import abc
import re
import os
from abc import ABC

from typing import Optional


class ValueConverters:
    @staticmethod
    def convert_str_to_bool(value: str) -> Optional[bool]:
        if value is None:
            return None
        if not isinstance(value, str) or (value.strip().lower() != "false" and value.strip().lower() != "true"):
            raise Exception(f"bool value type error.")
        return True if value.strip().lower() == "true" else False

    @staticmethod
    def convert_str_to_int(value: str, min_value: int, max_value: int) -> Optional[int]:
        if value is None:
            return None
        if not isinstance(value, str) or not value.isdigit():
            raise Exception(f"input is not str or digital.")
        int_value = int(value)
        if int_value < min_value or int_value > max_value:
            raise Exception(f"input value {int_value} is not in range [{min_value}, {max_value}].")
        return int_value

    @staticmethod
    def convert_str_to_float(value: str, min_value: float, max_value: float) -> Optional[float]:
        if value is None:
            return None
        try:
            float_value = float(value)
        except Exception:
            raise Exception(f"input is not float type.")
        if float_value < min_value or float_value > max_value:
            raise Exception(f"input value {float_value} is not in range [{min_value}, {max_value}].")
        return float_value


class PodConfigItemBase(ABC):
    def __init__(self):
        self.value = None

    @abc.abstractmethod
    def modify_json_data(self, config_data):
        pass

    @abc.abstractmethod
    def get_argument(self):
        pass

    @abc.abstractmethod
    def get_help(self):
        pass

    def get_type(self):
        return str

    @abc.abstractmethod
    def set_value(self, args):
        pass


class UseSecuritySettingItem(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["useSecuritySetting"] = self.value

    def get_argument(self):
        return "--useSecuritySetting"

    def get_help(self):
        return "Whether to enable the container security check, True is enabled, False is not enabled."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useSecuritySetting)


class CheckImageSha256(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["checkImageSha256"] = self.value

    def get_argument(self):
        return "--checkImageSha256"

    def get_help(self):
        return (
            "Whether to verify the container image sha256 value, True means verification, False means no verification."
        )

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.checkImageSha256)


class UseCapability(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["capability"] = self.value

    def get_argument(self):
        return "--useCapability"

    def get_help(self):
        return "Whether to allow configuration of container capability, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useCapability)


class UsePrivileged(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["privileged"] = self.value

    def get_argument(self):
        return "--usePrivileged"

    def get_help(self):
        return "Whether to allow the configuration of privileged containers, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.usePrivileged)


class UsePrivilegeEscalation(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["allowPrivilegeEscalation"] = self.value

    def get_argument(self):
        return "--usePrivilegeEscalation"

    def get_help(self):
        return "Whether to allow privilege escalation, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.usePrivilegeEscalation)


class UseRunAsRoot(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["runAsRoot"] = self.value

    def get_argument(self):
        return "--useRunAsRoot"

    def get_help(self):
        return "Whether to allow running containers as root account, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useRunAsRoot)


class UseProbe(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["probe"] = self.value

    def get_argument(self):
        return "--useProbe"

    def get_help(self):
        return "Whether to allow the use of container probes, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useProbe)


class UseStartCommand(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["startCommand"] = self.value

    def get_argument(self):
        return "--useStartCommand"

    def get_help(self):
        return "Whether to allow the specified container startup command, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useStartCommand)


class UseHostNetwork(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["useHostNetwork"] = self.value

    def get_argument(self):
        return "--useHostNetwork"

    def get_help(self):
        return "Whether to allow the container to use the host network, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useHostNetwork)


class UseSeccomp(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["useSeccomp"] = self.value

    def get_argument(self):
        return "--useSeccomp"

    def get_help(self):
        return "Whether to allow the container to use seccomp, True is allowed, False is not allowed."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useSeccomp)


class SetImageSha256WhiteList(PodConfigItemBase):
    MAX_WHITE_LIST_CNT_PER_TIME = 8
    MAX_WHITE_LIST_COUNT = 128

    def _splite_white_list(self, value: str) -> list:
        if not isinstance(value, str):
            raise Exception(f"The container image sha256 whitelist type is wrong.")
        sha256s = value.split(",")
        white_list = []
        for sha256 in sha256s:
            if not sha256:
                continue
            white_list.append(sha256)
        return white_list

    def _check_white_list(self, white_list: list):
        if len(white_list) > SetImageSha256WhiteList.MAX_WHITE_LIST_CNT_PER_TIME:
            raise Exception(
                f"Wrong number of sha256 whitelists configured, "
                f"and a maximum of 8 whitelists can be configured at a time."
            )

        pattern = r"^sha256:[0-9a-fA-F]{64}$"
        for item in white_list:
            if not re.match(pattern, item):
                raise Exception("Sha256 whitelist format error")

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        if len(self.value) == 0:
            config_data["imageSha256"] = {}
            return
        if len(config_data["imageSha256"]) + len(self.value) > SetImageSha256WhiteList.MAX_WHITE_LIST_COUNT:
            raise Exception("Too many mirror whitelists are configured, a total of 16 can be configured.")
        for item in self.value:
            config_data["imageSha256"][item] = ""

    def get_argument(self):
        return "--imageSha256WhiteList"

    def get_help(self):
        return (
            f'Configure the container image sha256 value whitelist. Multiple whitelists are divided by ",",'
            f" and a maximum of 8 can be configured at a time."
        )

    def set_value(self, args):
        if not args.imageSha256WhiteList:
            return
        if args.imageSha256WhiteList == "clean":
            self.value = {}
        else:
            white_list = self._splite_white_list(args.imageSha256WhiteList)
            self._check_white_list(white_list=white_list)
            self.value = white_list


class UseDefaultContainerCap(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["useDefaultContainerCap"] = self.value

    def get_argument(self):
        return "--useDefaultContainerCap"

    def get_help(self):
        return "Whether to use the default container capabilities."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.useDefaultContainerCap)


class SetRootFsReadOnly(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["setRootFsReadOnly"] = self.value

    def get_argument(self):
        return "--setRootFsReadOnly"

    def get_help(self):
        return "Indicates whether to set the container root file system to read-only. The default value is true."

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.setRootFsReadOnly)


class EmptyDirVolume(PodConfigItemBase):
    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["emptyDirVolume"] = self.value

    def get_argument(self):
        return "--emptyDirVolume"

    def get_help(self):
        return (
            "Indicates whether to allow container config empty dir volume."
        )

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_bool(args.emptyDirVolume)


class ContainerCpuLimit(PodConfigItemBase):
    CPU_CORE_MIN_VALUE = 0.01
    CPU_CORE_MAX_VALUE = 100.0

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["containerCpuLimit"] = self.value

    def get_argument(self):
        return "--containerCpuLimit"

    def get_help(self):
        return (
            "Configure cpu core limit for container, the format of the parameter is float, and the unit of the"
            " parameter is number of cpu cores. The default value is 1 cpu core."
        )

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_float(
            args.containerCpuLimit, self.CPU_CORE_MIN_VALUE, self.CPU_CORE_MAX_VALUE
        )


class ContainerNpuLimit(PodConfigItemBase):
    NPU_CORE_MIN_VALUE = 0
    NPU_CORE_MAX_VALUE = 100.0

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["containerNpuLimit"] = self.value

    def get_argument(self):
        return "--containerNpuLimit"

    def get_help(self):
        return (
            "Configure npu core limit for container, the format of the parameter is float, and the unit of the"
            " parameter is number of npu cores. The default value is 1 npu core."
        )

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_float(
            args.containerNpuLimit, self.NPU_CORE_MIN_VALUE, self.NPU_CORE_MAX_VALUE
        )


class ContainerMemoryLimit(PodConfigItemBase):
    MEMORY_MIN_VALUE = 4
    MEMORY_MAX_VALUE = 65536

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["containerMemoryLimit"] = self.value

    def get_argument(self):
        return "--containerMemoryLimit"

    def get_help(self):
        return (
            "Configure memory limit for container, the format of the parameter is int, and the unit of the"
            " parameter is MB. The default value is 2048MB."
        )

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_int(
            args.containerMemoryLimit, self.MEMORY_MIN_VALUE, self.MEMORY_MAX_VALUE
        )


class HostPathItem(PodConfigItemBase):
    def _splite_hostpath_list(self, value: str) -> list:
        if not isinstance(value, str):
            raise Exception(f"The hostpath type is wrong.")
        hostpaths_list = value.split(",")
        hostpath_list = []
        for hostpath in hostpaths_list:
            if not hostpath:
                continue
            hostpath_list.append(hostpath)
        return hostpath_list


class AddHostPath(HostPathItem):
    MAX_LENGTH = 1024
    MAX_WHITE_LIST_COUNT = 256
    ETC_LOCALTIME = "/etc/localtime"
    ETC_LOCALTIME_PREFIX = "/usr/share/zoneinfo/"

    def _check_path_etc_localtime(self, path: str):
        if not os.path.exists(path):
            return
        real_path = os.path.realpath(path)
        if real_path == self.ETC_LOCALTIME:
            return
        if not real_path.startswith(self.ETC_LOCALTIME_PREFIX):
            raise Exception(
                f"the real path pointed by {self.ETC_LOCALTIME} is not start with {self.ETC_LOCALTIME_PREFIX}.")
        if len(real_path) > self.MAX_LENGTH:
            raise Exception(
                f"the length of the real path pointed by {self.ETC_LOCALTIME} is more than {self.MAX_LENGTH}.")

    def _check_path_symbolic(self, path: str):
        if not os.path.exists(path):
            return
        real_path = os.path.realpath(path)
        if real_path != os.path.normpath(path):
            raise Exception(f"{path} is not a real path.")

    def _check_path_valid(self, path: str):
        if len(path) > self.MAX_LENGTH:
            raise Exception(f"input path length > {self.MAX_LENGTH}")
        pattern_name = re.compile(r"[^0-9a-zA-Z_./-]")
        match_name = pattern_name.findall(path)
        if match_name or ".." in path:
            raise Exception(f"illegal path,{path} has illegal character.")
        if not os.path.isabs(path):
            raise Exception(f"illegal path,{path} is not an absolute path.")

    def _check_hostpath_list(self, hostpath_list: list):
        for path in hostpath_list:
            if path == self.ETC_LOCALTIME:
                self._check_path_etc_localtime(path)
            else:
                self._check_path_valid(path)
                self._check_path_symbolic(path)

    def modify_json_data(self, config_data):
        if not self.value:
            return
        if len(config_data["hostpath"]) + len(self.value) > AddHostPath.MAX_WHITE_LIST_COUNT:
            raise Exception(
                f"Too many hsotpaths are configured, a total of {self.MAX_WHITE_LIST_COUNT}" f" can be configured."
            )
        config_data["hostpath"] = list((set(config_data["hostpath"])).union(set(self.value)))

    def get_argument(self):
        return "--addHostPath"

    def get_help(self):
        return (
            f"List of directories or files on the host where the container mounted volume is located."
            f'multiple lists are divided by ",",'
            f"and a maximum of {self.MAX_WHITE_LIST_COUNT} can be configured"
            f"but it cannot be executed at the same time with deleteHostPath."
        )

    def set_value(self, args):
        if args.deleteHostPath and args.addHostPath:
            raise Exception(
                f"add hostpath and delete hostpath cannot be executed at the same time in a single command entry."
            )
        if not args.addHostPath:
            return
        else:
            hostpath_list = self._splite_hostpath_list(args.addHostPath)
            self._check_hostpath_list(hostpath_list)
            self.value = hostpath_list


class DeleteHostPath(HostPathItem):
    def modify_json_data(self, config_data):
        if not self.value:
            return
        for item in self.value:
            if item not in config_data["hostpath"]:
                raise Exception(
                    f"The entered path or file {item} cannot be deleted because " f"it does not exist in the list."
                )
        config_data["hostpath"] = list((set(config_data["hostpath"])).difference(set(self.value)))

    def get_argument(self):
        return "--deleteHostPath"

    def get_help(self):
        return (
            f"The list contains the paths or files on the host that the container "
            f"mounted volume depends on, the input paths or files will be removed from the list,"
            f'multiple inputs should be divided by ",",'
            f"but it cannot be executed at the same time with addHostPath."
        )

    def set_value(self, args):
        if args.deleteHostPath and args.addHostPath:
            raise Exception(
                f"add hostpath and delete hostpath cannot be executed at the same time in a single command entry."
            )
        if not args.deleteHostPath:
            return
        else:
            self.value = self._splite_hostpath_list(args.deleteHostPath)


class MaxContainerNumber(PodConfigItemBase):
    MIN_CONTAINER_NUMBER_MIN_VALUE = 1
    MAX_CONTAINER_NUMBER_MIN_VALUE = 128

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["maxContainerNumber"] = self.value

    def get_argument(self):
        return "--maxContainerNumber"

    def get_help(self):
        return "Maximum number of containers that can be created on a device. The default value is 16. The value " \
               "ranges from 1 to 128. "

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_int(
            args.maxContainerNumber, self.MIN_CONTAINER_NUMBER_MIN_VALUE, self.MAX_CONTAINER_NUMBER_MIN_VALUE
        )


class MaxContainerModelFileNumber(PodConfigItemBase):
    MIN_CONTAINER_MODEL_FILE_NUMBER_VALUE = 0
    MAX_CONTAINER_MODEL_FILE_NUMBER_VALUE = 2048

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        if self.value > config_data["totalModelFileNumber"]:
            raise Exception(
                f"containerModelFileNumber must less than totalModelFileNumber: {config_data['totalModelFileNumber']}"
            )
        config_data["containerModelFileNumber"] = self.value

    def get_argument(self):
        return "--containerModelFileNumber"

    def get_help(self):
        return "Maximum number of model file in one container. The default value is 48. The value " \
               "ranges from 0 to totalModelFileNumber. "

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_int(
            args.containerModelFileNumber, self.MIN_CONTAINER_MODEL_FILE_NUMBER_VALUE,
            self.MAX_CONTAINER_MODEL_FILE_NUMBER_VALUE
        )


class MaxTotalModelFileNumber(PodConfigItemBase):
    MIN_TOTAL_MODEL_FILE_NUMBER_VALUE = 0
    MAX_TOTAL_MODEL_FILE_NUMBER_VALUE = 2048

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["totalModelFileNumber"] = self.value

    def get_argument(self):
        return "--totalModelFileNumber"

    def get_help(self):
        return "Maximum number of model file that can be created on a device. The default value is 512. The value " \
               "ranges from 0 to 2048. "

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_int(
            args.totalModelFileNumber, self.MIN_TOTAL_MODEL_FILE_NUMBER_VALUE, self.MAX_TOTAL_MODEL_FILE_NUMBER_VALUE
        )


class SystemReservedCPUQuota(PodConfigItemBase):
    CPU_CORE_MIN_VALUE = 0.5
    CPU_CORE_MAX_VALUE = 4.0

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["systemReservedCPUQuota"] = self.value

    def get_argument(self):
        return "--systemReservedCPUQuota"

    def get_help(self):
        return (
            "Configure cpu core limit for system reserved use, the format of the parameter is float, "
            "and the unit of the parameter is number of cpu cores. The default value is 1 cpu core."
        )

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_float(
            args.systemReservedCPUQuota, self.CPU_CORE_MIN_VALUE, self.CPU_CORE_MAX_VALUE
        )


class SystemReservedMemoryQuota(PodConfigItemBase):
    MEMORY_MIN_VALUE = 512
    MEMORY_MAX_VALUE = 4096

    def modify_json_data(self, config_data):
        if self.value is None:
            return
        config_data["systemReservedMemoryQuota"] = self.value

    def get_argument(self):
        return "--systemReservedMemoryQuota"

    def get_help(self):
        return ("Configure memory limit for system reserved use. the format of the parameter is int, "
                "and the unit of the parameter is MB. The default value is 1024MB. The value ranges from 512 to 2048.")

    def set_value(self, args):
        self.value = ValueConverters.convert_str_to_int(
            args.systemReservedMemoryQuota, self.MEMORY_MIN_VALUE, self.MEMORY_MAX_VALUE
        )
