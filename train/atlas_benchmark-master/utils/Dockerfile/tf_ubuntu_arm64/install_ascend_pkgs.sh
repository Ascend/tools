#!/bin/bash

#--------------------------------------------------------------------------------
# VERSION: 20.0.0.RC1
# 请在此处使用使用bash语法编写脚本代码，安装昇腾软件包
#
# 注：本脚本运行结束后不会被自动清除，若无需保留在镜像中请在postbuild.sh脚本中清除
#--------------------------------------------------------------------------------

ASCEND_NNAE=Ascend-cann-nnae_20.1.0.B030_linux-aarch64.run
ASCEND_TFPLUGIN=Ascend-fwk-tfplugin_20.1.0.B030_linux-aarch64.run

# 构建之前把host上的/etc/ascend_install.info拷贝一份到当前目录
cp ascend_install.info /etc/
# 构建之前把host的/usr/local/Ascend/driver/version.info拷贝一份到当前目录
mkdir -p /usr/local/Ascend/driver/
cp version.info /usr/local/Ascend/driver/
# Ascend-NNAE-20.0.0.B001-arm64-linux_gcc7.3.0.run
chmod +x ${ASCEND_NNAE}
./${ASCEND_NNAE} --install-path=/usr/local/Ascend/ --install --quiet
# Ascend-TFPlugin-20.0.0.B001-arm64-linux_gcc7.3.0.run
chmod +x ${ASCEND_TFPLUGIN}
./${ASCEND_TFPLUGIN} --install-path=/usr/local/Ascend/ --install --quiet

# 只为了安装nnae包，所以需要清理，容器启动时通过ascend docker挂载进来
rm -f version.info
rm -rf /usr/local/Ascend/driver/