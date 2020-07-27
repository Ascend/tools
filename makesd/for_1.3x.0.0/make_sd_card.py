#
#   =======================================================================
#
# Copyright (C) 2018, Hisilicon Technologies Co., Ltd. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1 Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   2 Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   3 Neither the names of the copyright holders nor the names of the
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#   =======================================================================
#
'''common installation'''
import os
import platform
import signal
import subprocess
import time
import yaml
import sys

NETWORK_CARD_DEFAULT_IP="192.168.0.2"
USB_CARD_DEFAULT_IP="192.168.1.2"

VERSION_INFO_URL = "https://raw.githubusercontent.com/Ascend/tools/master/versioninfo.yaml"

CURRENT_PATH = os.path.dirname(
    os.path.realpath(__file__))

SD_CARD_MAKING_PATH = os.path.join(CURRENT_PATH, "sd_card_making")

MIN_DISK_SIZE = 7 * 1024 * 1024 * 1024

MAKING_SD_CARD_COMMAND = "bash {path}/make_ubuntu_sd.sh " + " {dev_name}" + \
    " {pkg_path} {ubuntu_file_name} {ascend_developerkit_file_name}" + \
    " " + NETWORK_CARD_DEFAULT_IP + " " + USB_CARD_DEFAULT_IP + \
    " > {log_path}/make_ubuntu_sd.log "


def execute(cmd, timeout=3600, cwd=None):
    '''execute os command'''
    # print(cmd)
    is_linux = platform.system() == 'Linux'

    if not cwd:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, cwd=cwd, bufsize=32768, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               preexec_fn=os.setsid if is_linux else None)

    t_beginning = time.time()

    # cycle times
    time_gap = 0.01

    str_std_output = ""
    while True:

        str_out = str(process.stdout.read().decode())

        str_std_output = str_std_output + str_out

        if process.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning

        if timeout and seconds_passed > timeout:

            if is_linux:
                os.kill(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            return False, process.stdout.readlines()
        time.sleep(time_gap)
    str_std_output = str_std_output.strip()
    # print(str_std_output)
    std_output_lines_last = []
    std_output_lines = str_std_output.split("\n")
    for i in std_output_lines:
        std_output_lines_last.append(i)

    if process.returncode != 0 or "Traceback" in str_std_output:
        return False, std_output_lines_last

    return True, std_output_lines_last

def print_process(string, is_finished=False):
    if string == "" or string is None or is_finished:
        print(".......... .......... .......... .......... 100%", end='\r')
        print("")
    else:
        string = string.split(".......... ", 1)[1]
        string = string.split("%")[0] + "%"
        print(string, end='\r')

def execute_wget(cmd, timeout=86400, cwd=None):
    '''execute os command'''
    # print(cmd)
    is_linux = platform.system() == 'Linux'

    if not cwd:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, cwd=cwd, bufsize=1, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               preexec_fn=os.setsid if is_linux else None)

    t_beginning = time.time()

    # cycle times
    time_gap = 0.01

    str_std_output = ""
    process_str = ""
    while True:

        str_out = str(process.stdout.readline())
        if "......" in str_out:
            process_str = str_out
            print_process(process_str)

        str_std_output = str_std_output + str_out

        if process.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning

        if timeout and seconds_passed > timeout:

            if is_linux:
                os.kill(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            print("")
            return False
        time.sleep(time_gap)
        
    if process.returncode != 0 or "Traceback" in str_std_output:
        print("")
        return False
    print_process(process_str, True)
    return True

def check_sd(dev_name):
    ret, disk = execute(
        "fdisk -l 2>/dev/null | grep \"Disk {dev_name}:\"".format(dev_name=dev_name))

    if not ret or len(disk) > 1:
        print(
            "[ERROR] Can not get disk, please use fdisk -l to check available disk name!")
        return False

    ret, mounted_list = execute("df -h")

    if not ret:
        print("[ERROR] Can not get mounted disk list!")
        return False

    unchanged_disk_list = []
    for each_mounted_disk in mounted_list:
        disk_name = each_mounted_disk.split()[0]
        disk_type = each_mounted_disk.split()[5]
        if disk_type == "/boot" or disk_type == "/":
            unchanged_disk_list.append(disk_name)
    unchanged_disk = " ".join(unchanged_disk_list)

    disk_size_str = disk[0].split(", ")[1]
    disk_size_str = disk_size_str.split()[0]
    disk_size = int(disk_size_str)

    if dev_name not in unchanged_disk and disk_size >= MIN_DISK_SIZE:
        return True

    print("[ERROR] Invalid SD card or size is less then 8G, please check SD Card.")
    return False


def parse_download_info(ascend_version):
    version_info_file_name = os.path.basename(VERSION_INFO_URL)
    version_info_path = os.path.join(
        CURRENT_PATH, version_info_file_name)
    ret = execute_wget("wget -O {name} {url} --no-check-certificate".format(
        name=version_info_path, url=VERSION_INFO_URL))

    if not ret or not os.path.exists(version_info_path):
        print(
            "[ERROR] Can not download versioninfo.yaml, please check your network connection.")
        execute("rm -rf {path}".format(path=version_info_path))
        return False, "", "", ""

    version_info_file = open(
        version_info_path, 'r', encoding='utf-8')
    version_info_dict = yaml.load(
        version_info_file)

    ascend_version_dict = version_info_dict.get("mini_developerkit")
    if ascend_version == "" or ascend_version == ascend_version_dict.get("latest_version"):
        ascend_developerkit_url = ascend_version_dict.get("url")
        ascend_sd_making_url = ascend_version_dict.get("sd_making_url")
        ubuntu_version = ascend_version_dict.get(
            "compatibility").get("ubuntu")[0]
    else:
        version_list = ascend_version_dict.get("archived_versions")
        for each_version in version_list:
            if ascend_version == each_version.get("version"):
                ascend_developerkit_url = each_version.get("url")
                ascend_sd_making_url = each_version.get("sd_making_url")
                ubuntu_version = each_version.get(
                    "compatibility").get("ubuntu")[0]
                break
    ubuntu_version_dict = version_info_dict.get("ubuntu")
    for each_version in ubuntu_version_dict:
        if ubuntu_version == each_version.get("version"):
            ubuntu_url = each_version.get("url")
            break

    version_info_file.close()

    if ascend_developerkit_url == "" or ascend_sd_making_url == "" or ubuntu_url == "":
        return False, "", "", ""

    return True, ascend_developerkit_url, ascend_sd_making_url, ubuntu_url


def process_local_installation(dev_name):
    confirm_tips = "Please make sure you have installed dependency packages:" + \
        "\n\t apt-get install -y qemu-user-static binfmt-support gcc-aarch64-linux-gnu g++-aarch64-linux-gnu\n" + \
        "Please input Y: continue, other to install them:"
    confirm = input(confirm_tips)
    confirm = confirm.strip()

    if confirm != "Y" and confirm != "y":
        return False

    execute("rm -rf {path}_log/*".format(path=SD_CARD_MAKING_PATH))
    execute("mkdir -p {path}_log".format(path=SD_CARD_MAKING_PATH))
    log_path = "{path}_log".format(path=SD_CARD_MAKING_PATH)
    ret, paths = execute(
        "find {path} -name \"mini_developerkit*.rar\"".format(path=CURRENT_PATH))
    if not ret:
        print("[ERROR] Can not fine mini eveloperkit package in current path")
        return False

    if len(paths) > 1:
        print(
            "[ERROR] Too many mini developerkit packages, please delete redundant packages.")
        return False
    ascend_developerkit_path = paths[0]
    ascend_developerkit_file_name = os.path.basename(ascend_developerkit_path)

    ret, paths = execute(
        "find {path} -name \"make-ubuntu-sd.sh\"".format(path=CURRENT_PATH))
    if not ret:
        print("[ERROR] Can not fine make_ubuntu_sd.sh in current path")
        return False

    ret, paths = execute(
        "find {path} -name \"ubuntu*server*arm*.iso\"".format(path=CURRENT_PATH))
    if not ret:
        print("[ERROR] Can not fine ubuntu\ package in current path")
        return False
    if len(paths) > 1:
        print("[ERROR] Too many ubuntu packages, please delete redundant packages.")
        return False
    ubuntu_path = paths[0]
    ubuntu_file_name = os.path.basename(ubuntu_path)

    print("Step: Start to make SD Card. It need some time, please wait...")
    execute(MAKING_SD_CARD_COMMAND.format(path=CURRENT_PATH, dev_name=dev_name, pkg_path=CURRENT_PATH,
                                                ubuntu_file_name=ubuntu_file_name,
                                                ascend_developerkit_file_name=ascend_developerkit_file_name, log_path=log_path))
    ret = execute("grep Success {log_path}/make_ubuntu_sd.result".format(log_path=log_path))
    if not ret[0]:
        print("[ERROR] Making SD Card failed, please check %s/make_ubuntu_sd.log for details!" % log_path)
        return False

    return True


def process_internet_installation(dev_name, ascend_version):
    print("Step: Downloading version information...")
    ret = parse_download_info(ascend_version)

    if not ret[0]:
        print("Can not find valid versions, please try to get valid version: python3 sd_card_making.py list")
        return False

    ascend_developerkit_url = ret[1]
    ascend_sd_making_url = ret[2]
    ubuntu_url = ret[3]

    execute("rm -rf {path}_log/*".format(path=SD_CARD_MAKING_PATH))
    execute("mkdir -p {path}_log".format(path=SD_CARD_MAKING_PATH))
    log_path = "{path}_log".format(path=SD_CARD_MAKING_PATH)

    print("Step: Downloading developerkit package...")
    ascend_developerkit_file_name = os.path.basename(ascend_developerkit_url)
    ascend_developerkit_path = os.path.join(
        CURRENT_PATH, ascend_developerkit_file_name)
    if os.path.exists(ascend_developerkit_path):
        print("%s is already downloaded, skip to download it." %
              ascend_developerkit_path)
    else:
        ret = execute_wget("wget -O {name} {url} --no-check-certificate".format(
            name=ascend_developerkit_path, url=ascend_developerkit_url))
        if not ret or not os.path.exists(ascend_developerkit_path):
            print("[ERROR] Download develperkit package failed, Please check %s connection." %
                  ascend_developerkit_url)
            execute("rm -rf {path}".format(path=ascend_developerkit_path))
            return False

    print("Step: Downloading SD Card making scripts...")
    ascend_sd_making_file_name = os.path.basename(ascend_sd_making_url)
    ascend_sd_making_path = os.path.join(
        CURRENT_PATH, ascend_sd_making_file_name)
    ret = execute_wget("wget -O {name} {url} --no-check-certificate".format(
        name=ascend_sd_making_path, url=ascend_sd_making_url))
    if not ret or not os.path.exists(ascend_developerkit_path):
        print("[ERROR] Download SD Card making scripts failed, Please check %s connection." %
              ascend_sd_making_url)
        execute("rm -rf {path}".format(path=ascend_sd_making_path))
        return False

    print("Step: Downloading Ubuntu iso...")
    ubuntu_file_name = os.path.basename(ubuntu_url)
    ubuntu_path = os.path.join(CURRENT_PATH, ubuntu_file_name)
    if os.path.exists(ubuntu_path):
        print("%s is already downloaded, skip to download it." % ubuntu_path)
    else:
        ret = execute_wget(
            "wget -O {name} {url} --no-check-certificate".format(name=ubuntu_path, url=ubuntu_url))
        if not ret or not os.path.exists(ascend_developerkit_path):
            print(
                "[ERROR] Download Ubuntu iso failed, Please check %s connection." % ubuntu_url)
            execute("rm -rf {path}".format(path=ubuntu_path))
            return False

    print("Step: Installing system dependency...")
    ret = execute(
        "apt-get install -y qemu-user-static binfmt-support gcc-aarch64-linux-gnu g++-aarch64-linux-gnu")
    if not ret[0]:
        print("[ERROR] Install system dependency failed, please check:" +
              "\n\tapt-get install -y qemu-user-static binfmt-support gcc-aarch64-linux-gnu g++-aarch64-linux-gnu\n\tapt-get install -y qemu-user-static binfmt-support gcc-aarch64-linux-gnu g++-aarch64-linux-gnu")

    print("Step: Start to make SD Card. It need some time, please wait...")
    execute(MAKING_SD_CARD_COMMAND.format(path=CURRENT_PATH, dev_name=dev_name,
                                                pkg_path=CURRENT_PATH, ubuntu_file_name=ubuntu_file_name,
                                                ascend_developerkit_file_name=ascend_developerkit_file_name,
                                                log_path=log_path))
    ret = execute("grep Success {log_path}/make_ubuntu_sd.result".format(log_path=log_path))
    if not ret[0]:
        print("[ERROR] Making SD Card failed, please check %s/make_ubuntu_sd.log for details!" % log_path)
        return False
    return True


def print_usage():
    print("Usage: ")
    print("\t[internet]: python3 make_sd_card.py internet [SD Name]")
    print("\t                 Use latest version to make SD card.")
    print("\t[internet]: python3 make_sd_card.py internet [SD Name] [Version]")
    print("\t                 Use given version to make SD card.")
    print("\t[local   ]: python3 make_sd_card.py local [SD Name]")
    print("\t                 Use local given packages to make SD card.")


def main():
    '''sd card making'''
    command = ""
    dev_name = ""
    version = ""
    if (len(sys.argv) >= 3):
        command = sys.argv[1]
        dev_name = sys.argv[2]

    if (len(sys.argv) >= 4):
        version = sys.argv[3]

    if command == "internet" and (len(sys.argv) == 3 or len(sys.argv) == 4):
        print("Begin to make SD Card...")
    elif command == "local" and len(sys.argv) == 3:
        print("Begin to make SD Card...")
    else:
        print("Invalid Command!")
        print_usage()
        exit(-1)

    ret = check_sd(dev_name)

    if not ret:
        exit(-1)

    if command == "internet":
        result = process_internet_installation(dev_name, version)
    else:
        result = process_local_installation(dev_name)

    if result:
        print("Make SD Card successfully!")
        exit(0)
    else:
        exit(-1)


if __name__ == '__main__':
    main()
