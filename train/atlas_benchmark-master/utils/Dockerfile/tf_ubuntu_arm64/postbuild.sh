#!/bin/bash

#--------------------------------------------------------------------------------
# VERSION: 20.0.0.RC1
# 请在此处使用使用bash语法编写脚本代码，清除不需要保留在容器中的安装包、脚本、代理配置等
# 本脚本将会在正式构建过程结束后被执行
#
# 注：本脚本运行结束后会被自动清除，不会残留在镜像中；脚本所在位置和Working Dir位置为/tmp
#--------------------------------------------------------------------------------
rm -f ascend_install.info
rm -f prebuild.sh
rm -f install_ascend_pkgs.sh
rm -f Dockerfile*
rm -f cmake*
rm -f openmpi*
rm -f Ascend-cann-nnae_20.1.0.B030_linux-aarch64.run
rm -f Ascend-fwk-tfplugin_20.1.0.B030_linux-aarch64.run
rm -f tensorflow-1.15.0-cp37-cp37m-linux_aarch64.whl
# rm -f /etc/apt/apt.conf.d/80proxy
tee /etc/resolv.conf <<- EOF
# This file is managed by man:systemd-resolved(8). Do not edit.
#
# This is a dynamic resolv.conf file for connecting local clients to the
# internal DNS stub resolver of systemd-resolved. This file lists all
# configured search domains.
#
# Run "systemd-resolve --status" to see details about the uplink DNS servers
# currently in use.
#
# Third party programs must not access this file directly, but only through the
# symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a different way,
# replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.
options edns0
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF