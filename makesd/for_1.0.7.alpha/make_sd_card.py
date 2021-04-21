"""
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
"""

import os
import platform
import signal
import subprocess
import time
import yaml
import sys
import re


NETWORK_CARD_DEFAULT_IP="192.168.0.2"
USB_CARD_DEFAULT_IP="192.168.1.2"


CURRENT_PATH = os.path.dirname(
    os.path.realpath(__file__))

SD_CARD_MAKING_PATH = os.path.join(CURRENT_PATH, "sd_card_making")
LOG_PATH = "{path}_log".format(path=SD_CARD_MAKING_PATH)
MAKE_SD_LOG_PATH = os.path.join(LOG_PATH, "make_ubuntu_sd.log")
MIN_DISK_SIZE = 7 * 1024 * 1024 * 1024

MAKING_SD_CARD_COMMAND = "bash {path}/make_ubuntu_sd.sh " + " {dev_name}" + \
    " {pkg_path} {ubuntu_file_name}" + \
    " " + NETWORK_CARD_DEFAULT_IP + " " + USB_CARD_DEFAULT_IP + " {sector_num}" + " {sector_size}" \
    " >> {log_path}/make_ubuntu_sd.log "


def execute(cmd, timeout=3600, cwd=None):
    """execute os command"""

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


def C_trans_to_E(string):
    E_PUN = u',.!?:[]()<>"\''
    C_PUN = u'，。！？：【】（）《》“‘'

    table= {ord(f): ord(t) for f, t in zip(C_PUN, E_PUN)}

    return string.translate(table)


def remove_chn_and_charactor(str1):
    """remove Special charactors""" 
    C_PUN = u'，。！？：【】（）《》“‘'
    stren = ''

    if not isinstance(str1, str):
        print("The input is not string")
        execute("echo 'The input is not string' >> %s" % (MAKE_SD_LOG_PATH))
        return stren

    for i in range(len(str1)):
        if str1[i] >= u'\u4e00' and str1[i] <= u'\u9fa5' \
                or str1[i] >= u'\u3300' and str1[i] <= u'\u33FF' \
                or str1[i] >= u'\u3200' and str1[i] <= u'\u32FF' \
                or str1[i] >= u'\u2700' and str1[i] <= u'\u27BF' \
                or str1[i] >= u'\u2600' and str1[i] <= u'\u26FF' \
                or str1[i] >= u'\uFE10' and str1[i] <= u'\uFE1F' \
                or str1[i] >= u'\u2E80' and str1[i] <= u'\u2EFF' \
                or str1[i] >= u'\u3000' and str1[i] <= u'\u303F' \
                or str1[i] >= u'\u31C0' and str1[i] <= u'\u31EF' \
                or str1[i] >= u'\u2FF0' and str1[i] <= u'\u2FFF' \
                or str1[i] >= u'\u3100' and str1[i] <= u'\u312F' \
                or str1[i] >= u'\u21A0' and str1[i] <= u'\u31BF' \
                :
            pass
        else:
            if str1[i] in C_PUN:
                st = C_trans_to_E(str1[i])
            else:
                st = str1[i]
            stren += st

    return stren


def get_disk_size_and_sectors(disk_info):
    """get disk infomation""" 
    disk_size_info = disk_info.split(":")[1]
    disk_size_info = disk_size_info.replace(",", ".")
    disk_size_list = re.findall(r"\b\d+\.?\d+\b", disk_size_info)
    if (len(disk_size_list) != 3):
        print("[ERROR] Get disk size failed ", disk_info)
        execute("echo '[ERROR] Get disk size failed %s' >> %s" % (disk_info, MAKE_SD_LOG_PATH))
        return 0, 0
    return int(disk_size_list[1]), int(disk_size_list[2])


def check_sd(dev_name):
    """check sd card""" 
    ret, disk = execute("fdisk -l 2>/dev/null | grep -P 'Disk %s[\\x{FF1A}:]'" % (dev_name))
    disk[0] = remove_chn_and_charactor(disk[0])    
    if not ret or len(disk) > 1:
        print("[ERROR] Can not get disk, please use fdisk -l to check available disk name!")
        execute("echo '[ERROR] Can not get disk, please use fdisk -l to check available disk name!'\
        >> %s" % (MAKE_SD_LOG_PATH))
        return False, None, None

    ret, mounted_list = execute("df -h")

    if not ret:
        print("[ERROR] Can not get mounted disk list!")
        execute("echo '[ERROR] Can not get mounted disk list!' >> %s" % (MAKE_SD_LOG_PATH))
        return False, None, None

    unchanged_disk_list = []
    for each_mounted_disk in mounted_list:
        disk_name = each_mounted_disk.split()[0]
        disk_type = each_mounted_disk.split()[5]
        if disk_type == "/boot" or disk_type == "/":
            unchanged_disk_list.append(disk_name)
    unchanged_disk = " ".join(unchanged_disk_list)

    disk_size, sector_num = get_disk_size_and_sectors(disk[0])
    print("disk %s size %d, sector num %d" % (dev_name, disk_size, sector_num))
    execute("echo 'disk %s size %d, sector num %d' >> %s" % (dev_name, disk_size, sector_num, MAKE_SD_LOG_PATH))
    if dev_name  in unchanged_disk or disk_size < MIN_DISK_SIZE:
        print("[ERROR] Invalid SD card or size is less then 8G, please check SD Card.")
        execute("echo '[ERROR] Invalid SD card or size is less then 8G, please check SD Card.' >> %s"\
            % (MAKE_SD_LOG_PATH))
        return False, None, None

    ret, sector = execute("fdisk -l 2>/dev/null | grep -PA 2 'Disk %s[\\x{FF1A}:]' | grep -P \
    '[\\x{5355}\\x{5143}]|Units'" % (dev_name))
    if not ret or len(sector) > 1:
        print("[ERROR] Can not get sector size , please use fdisk -l to check available disk name!")
        execute("echo '[ERROR] Can not get sector size , please use fdisk -l to check available disk name!' \
            >> %s" % (MAKE_SD_LOG_PATH))
        return False, None, None

    sector[0] = remove_chn_and_charactor(sector[0])    
    sector_size_str=sector[0].split('*')[1].split('=')[0].strip()
    sector_size=int(sector_size_str)

    print("sector size %d" % (sector_size))
    execute("echo 'sector size %d' >> %s" % (sector_size, MAKE_SD_LOG_PATH))
    return True, sector_num, sector_size


def process_local_installation(dev_name, sector_num, sector_size):
    """Installation process""" 
    confirm_tips = "Please make sure you have installed dependency packages:" + \
        "\n\t apt-get install -y qemu-user-static binfmt-support gcc-aarch64-linux-gnu g++-aarch64-linux-gnu\n" + \
        "Please input Y: continue, other to install them:"
    confirm = input(confirm_tips)
    confirm = confirm.strip()

    if confirm != "Y" and confirm != "y":
        return False

    ret, paths = execute(
        "find {path} -name \"make_ubuntu_sd.sh\"".format(path=CURRENT_PATH))
    if not ret or len(paths[0]) == 0:
        print("[ERROR] Can not find make_ubuntu_sd.sh in current path")
        execute("echo '[ERROR] Can not find make_ubuntu_sd.sh in current path' >> %s" % (MAKE_SD_LOG_PATH))
        return False

    ret, paths = execute(
        "find {path} -name \"ubuntu*server*arm*.iso\"".format(path=CURRENT_PATH))
    if not ret or len(paths[0])==0:
        print("[ERROR] Can not find ubuntu*server*arm*.iso package in current path")
        execute("echo '[ERROR] Can not find ubuntu*server*arm*.iso package in current path' >> %s" % (MAKE_SD_LOG_PATH))
        return False

    if len(paths) > 1:
        print("[ERROR] Too many ubuntu packages, please delete redundant packages.")
        execute("echo '[ERROR] Too many ubuntu packages, please delete redundant packages.' >> %s" % (MAKE_SD_LOG_PATH))
        return False
    ubuntu_path = paths[0]
    ubuntu_file_name = os.path.basename(ubuntu_path)

    print("Step: Start to make SD Card. It need some time, please wait...")
    execute("echo 'Step: Start to make SD Card. It need some time, please wait...' >> %s" % (MAKE_SD_LOG_PATH))
    print("Command:")
    execute("echo 'Command:' >> %s" % (MAKE_SD_LOG_PATH))

    making_sd_card_command_str = MAKING_SD_CARD_COMMAND.format(path=CURRENT_PATH, dev_name=dev_name, \
    pkg_path=CURRENT_PATH, ubuntu_file_name=ubuntu_file_name, log_path=LOG_PATH, sector_num=sector_num,\
    sector_size=sector_size)

    print(making_sd_card_command_str)
    execute("echo '%s' >> %s" % (making_sd_card_command_str, MAKE_SD_LOG_PATH))

    execute(MAKING_SD_CARD_COMMAND.format(path=CURRENT_PATH, dev_name=dev_name, pkg_path=CURRENT_PATH,\
        ubuntu_file_name=ubuntu_file_name, log_path=LOG_PATH, sector_num=sector_num, \
        sector_size=sector_size))

    ret = execute("grep Success {log_path}/make_ubuntu_sd.result".format(log_path=LOG_PATH))
    if not ret[0]:
        print("[ERROR] Making SD Card failed, please check %s/make_ubuntu_sd.log for details!" % LOG_PATH)
        execute("echo '[ERROR] Making SD Card failed, please check %s/make_ubuntu_sd.log for details!' >> %s" \
        % (LOG_PATH, MAKE_SD_LOG_PATH))
        return False
    return True


def print_usage():
    """print usage"""
    print("Usage: ")
    print("\t[local   ]: python3 make_sd_card.py local [SD Name]")
    print("\t                 Use local given packages to make SD card.")
    execute("echo 'Usage: ' >> %s" % (MAKE_SD_LOG_PATH))
    execute("echo '\t[local   ]: python3 make_sd_card.py local [SD Name]' >> %s" % (MAKE_SD_LOG_PATH))
    execute("echo '\t                 Use local given packages to make SD card.' >> %s" % (MAKE_SD_LOG_PATH))


def main():
    """sd card making"""
    command = ""
    dev_name = ""
    sector_num=None
    sector_size=None
    execute("rm -rf {path}_log/*".format(path=SD_CARD_MAKING_PATH))
    execute("mkdir -p {path}_log".format(path=SD_CARD_MAKING_PATH))
    if (len(sys.argv) >= 3):
        command = sys.argv[1]
        dev_name = sys.argv[2]

    if command == "local" and len(sys.argv) == 3:
        print("Begin to make SD Card...")
        execute("echo 'Begin to make SD Card...' >> %s" % (MAKE_SD_LOG_PATH))
    else:
        print("Invalid Command!")
        execute("echo 'Invalid Command!' >> %s" % (MAKE_SD_LOG_PATH))
        print_usage()
        exit(-1)

    ret, sector_num, sector_size = check_sd(dev_name)
    if not ret:
        exit(-1)

    result = process_local_installation(dev_name, sector_num, sector_size)

    if result:
        print("Make SD Card successfully!")
        execute("echo 'Make SD Card successfully!' >> %s" % (MAKE_SD_LOG_PATH))
        exit(0)
    else:
        exit(-1)


if __name__ == '__main__':
    main()

