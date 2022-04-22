# CI package
import enum
import re
import datetime
import logging
import platform
import time
from hdfs import InsecureClient
from typing import List
import os
import socket
from . import shell_printer

NAME_RES = [
    re.compile(r'CANN-compiler-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'CANN-runtime-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'CANN-opp-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'CANN-fwkplugin-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'CANN-toolkit-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),

    re.compile(r'Ascend-acllib-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'Ascend-fwkacllib-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'Ascend-atc-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'Ascend-toolkit-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'Ascend-opp-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
    re.compile(r'Ascend-tfplugin-(?P<version>[\w\.]+)-(?P<os>[\w\.]+)\.(?P<arch>(\w+))\.run'),
]


class PackageType(enum.Enum):
    COMPILER_CANN = 0
    RUNTIME_CANN = 1
    OPP_CANN = 2
    FWKPLUGIN_CANN = 3
    TOOLKIT_CANN = 4

    ACLLIB_ONETRACK = 5
    FWKACLLIB_ONETRACK = 6
    ATC_ONETRACK = 7
    TOOLKIT_ONETRACK = 8
    OPP_ONETRACK = 9
    TFPLUGIN_ONETRACK = 10

    @staticmethod
    def guess_type_by_name(name):
        for pt in PackageType:
            if pt.get_name_re().match(name):
                return pt
        return None

    def get_name_re(self):
        global NAME_RES
        return NAME_RES[self.value]

    def get_build_scene(self):
        if self.value < PackageType.ACLLIB_ONETRACK.value:
            return 'cann'
        else:
            return 'onetrack'


class OsType(enum.Enum):
    UBUNTU = 0
    CENTOS = 1
    EULEROS = 2
    MINIOS = 3
    LINUX = 4

    @staticmethod
    def analyse_os(os_str: str):
        if os_str.startswith('ubuntu'):
            return OsType.UBUNTU
        elif os_str.startswith('centos'):
            return OsType.CENTOS
        elif os_str.startswith('euleros'):
            return OsType.EULEROS
        elif os_str.startswith('minios'):
            return OsType.MINIOS
        elif os_str.startswith('linux'):
            return OsType.LINUX
        else:
            raise Exception("Unexpected os_str {}".format(os_str))


class HisiHdfs:
    def __init__(self):
        self._c = InsecureClient(url="http://{}:14000".format(HisiHdfs.get_host()), user='hdfs', root="/")
        # self._c = InsecureClient(url="http://10.154.67.254:14000", user='hdfs', root="/")

    @staticmethod
    def get_host():
        domain = 'hdfs-ngx1.turing-ci.hisilicon.com'
        try:
            socket.gethostbyname(domain)
            return domain
        except Exception as e:
            return '10.154.67.254'

    @staticmethod
    def build_month_path(build_scene):
        '''daily build path'''
        return '/compilepackage/CI_Version/{}/br_hisi_trunk_ai/{}'.\
            format(build_scene, datetime.datetime.today().strftime('%Y%m'))

    @staticmethod
    def prebuild_month_path(build_scene):
        '''compile path'''
        return '/compilepackage/CI_Version/{}/br_hisi_trunk_ai_PRE_COMPILE/{}'.\
            format(build_scene, datetime.datetime.today().strftime('%Y%m'))

    def find_newest_build(self, build_scene):
        builds = self._c.list(HisiHdfs.build_month_path(build_scene), True)
        newest_build_name = None
        for build in builds:
            if type(build) != tuple:
                logging.warning("Unexpected build format {}".format(build))
                continue
            if len(build) < 2:
                logging.warning("Unexpected build format {}".format(build))
                continue
            if type(build[1]) != dict:
                logging.warning("Unexpected build format[1] {}".format(build))
                continue
            if build[1].get('type', None) != "DIRECTORY":
                logging.warning("Found unexpected build type(not DIRECTORY) {}".format(build))
                continue
            if type(build[0]) != str:
                logging.warning("Unexpected build format[0] {}".format(build))
                continue
            elements = build[0].split('_')
            if len(elements) != 3:
                logging.warning("Unexpected build name {}".format(build))
                continue
            if elements[2] != "newest":
                continue
            # build_date = datetime.datetime.strptime('_'.join(elements[:2]), "%Y%m%d_%H%M%S%f")
            if newest_build_name is None:
                newest_build_name = build[0]
                continue
            if newest_build_name < build[0]:
                newest_build_name = build[0]
        return newest_build_name

    def path_exists(self, base_path: str, build_name: str):
        path = "{}/{}".format(base_path, build_name)
        return self._c.status(path, strict=False) is not None

    def find_package(self, base_path: str, build_name: str, package_type: PackageType, os_type=None, arch=None):
        if os_type is None:
            os_type, arch = get_env()
        path = "{}/{}".format(base_path, build_name)
        packages = self._c.list(path, True)
        pr = package_type.get_name_re()
        for package_name, package_info in packages:
            pm = pr.match(package_name)
            if pm is not None:
                if OsType.analyse_os(pm.group('os')) == os_type and pm.group('arch') == arch:
                    return package_name
        return None

    def download_package(self, base_path: str, build_name: str, package_name: str, local_path: str):
        return self._c.download(hdfs_path="{}/{}/{}".format(base_path, build_name, package_name),
                                local_path=local_path, overwrite=True)

    def download_compile_package(self, build_scene: str, build_name: str, package_name: str, local_path: str):
        return self.download_package(HisiHdfs.prebuild_month_path(build_scene), build_name, package_name, local_path)

    def download_daily_package(self, build_scene: str, build_name: str, package_name: str, local_path: str):
        return self.download_package(HisiHdfs.build_month_path(build_scene), build_name, package_name, local_path)

    def download_newest(self, local_path: str, packages: List[PackageType], os_type=None, arch=None):
        if not os.path.isdir(local_path):
            raise FileNotFoundError("The path {} does not exists".format(local_path))
        if os_type is None:
            os_type, arch = get_env()

        build_scenes_to_build_name = {}
        package_names = []
        print("Begin to download newest run packages from the newest")
        for package in packages:
            build_scene = package.get_build_scene()
            newest_build_name = build_scenes_to_build_name.get(build_scene, self.find_newest_build(build_scene))
            if newest_build_name is None:
                logging.error("Can not find the newest build")
                raise Exception("Can not find the newest build")
            package_name = self.find_package(HisiHdfs.build_month_path(build_scene),
                                             newest_build_name, package, os_type, arch)
            if package_name is None:
                logging.error("Can not find the package {}, os {}, arch {}".format(package, os_type, arch))
                raise Exception("Can not find package")
            with shell_printer.DotPrinter(
                    "Begin to download {} from {} to {}".format(package_name, newest_build_name, local_path)):
                self.download_daily_package(build_scene, newest_build_name, package_name, local_path)
            logging.info("Download {} to {} successfully".format(package_name, local_path))
            package_names.append(package_name)
        return package_names

    def download_compile_packages(self, build_name: str, local_path: str, package_types: List[PackageType]):
        self.wait_compile_paths_ready(package_types, build_name)
        package_names = []
        for package_type in package_types:
            package_name = self.find_package(HisiHdfs.prebuild_month_path(package_type.get_build_scene()),
                                             build_name, package_type)
            if package_name is None:
                with shell_printer.DotPrinter("Wait package {} from {}".format(package_type.name, build_name)):
                    while package_name is None:
                        logging.debug("Can not find package {} from {}, sleep".format(package_type.name, build_name))
                        time.sleep(10)
                        package_name = self.find_package(HisiHdfs.prebuild_month_path(package_type.get_build_scene()),
                                                         build_name, package_type)
                    # 实测来看，刚创建好的文件直接下载可能有问题（下载失败，或者下载文件不完整），这里等5秒钟再下载
                    time.sleep(5)

            with shell_printer.DotPrinter("Begin to download {} to {}".format(package_name, local_path)):
                self.download_compile_package(package_type.get_build_scene(), build_name, package_name, local_path)
            logging.info("Download {} to {} successfully".format(package_name, local_path))
            package_names.append(package_name)
        return package_names

    def wait_compile_paths_ready(self, package_types: List[PackageType], build_name: str):
        scenes = set([pt.get_build_scene() for pt in package_types])
        for build_scene in scenes:
            build_path = HisiHdfs.prebuild_month_path(build_scene)
            if not self.path_exists(build_path, build_name):
                with shell_printer.DotPrinter(
                        "The build({}) path({}) has not been created, wait".format(build_name, build_path)):
                    while not self.path_exists(build_path, build_name):
                        time.sleep(1)


def get_release_from_etc():
    release_re = re.compile(r'NAME="(?P<release>\w+)"')
    release_file = "/etc/os-release"
    if not os.path.exists(release_file):
        return None
    with open(release_file, 'r') as f:
        for line in f:
            ma = release_re.match(line)
            if ma is not None:
                return ma.group('release')
    return None


def get_env():
    if platform.system() != "Linux":
        logging.error("Do not support the os")
        raise Exception("Do not support the {} os".format(platform.system()))

    arch = platform.machine()
    if arch not in {"x86_64", "aarch64"}:
        raise Exception("Unsupport arch {}".format(arch))

    release = platform.release().lower()
    for os_type in OsType:
        if release.find(os_type.name.lower()) >= 0:
            break
    else:
        release = get_release_from_etc().lower()
        for os_type in OsType:
            if release.find(os_type.name.lower()) >= 0:
                break
        else:
            raise Exception("unsupport release {}".format(platform.release()))

    special_packages = {(OsType.EULEROS, "aarch64"), (OsType.UBUNTU, "x86_64")}
    if (os_type, arch) in special_packages:
        return os_type, arch
    else:
        return OsType.LINUX, arch

