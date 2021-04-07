FROM ubuntu:18.04
COPY sources.list /etc/apt/
RUN set -ex && apt update -y 2> /dev/null && apt install net-tools -y 2> /dev/null  && apt install iputils-ping -y 2> /dev/null \
    && apt install vim -y 2> /dev/null && apt install sudo 2> /dev/null \
    && echo "root:root" | chpasswd \
    && useradd -d /home/HwHiAiUser -m HwHiAiUser \
    && echo "HwHiAiUser:HwHiAiUser" | chpasswd \
    && chmod 750 /home/HwHiAiUser \
    && chmod u+w /etc/sudoers \
    && sed -i '/# User privilege specification/a\HwHiAiUser ALL=(ALL:ALL)   ALL' /etc/sudoers \
    && chmod u-w /etc/sudoers 
USER HwHiAiUser
WORKDIR /home/HwHiAiUser/
COPY --chown=HwHiAiUser:HwHiAiUser Python-3.7.5.tgz ./ 
COPY --chown=HwHiAiUser:HwHiAiUser A200dk-npu-driver-20.2.0-ubuntu18.04-aarch64-minirc.tar.gz ./ 
COPY --chown=HwHiAiUser:HwHiAiUser Ascend-cann-toolkit_20.2.alpha001_linux-aarch64.run ./
COPY --chown=HwHiAiUser:HwHiAiUser Ascend-cann-toolkit_20.2.alpha001_linux-x86_64.run ./

RUN set -ex && echo 'HwHiAiUser' | sudo -S apt install  gcc make cmake unzip zlib1g zlib1g-dev libsqlite3-dev openssl libssl-dev libffi-dev pciutils net-tools g++-5-aarch64-linux-gnu -y 2> /dev/null \
    && sudo apt install qemu-user-static binfmt-support python3-yaml gcc-aarch64-linux-gnu g++-aarch64-linux-gnu -y 2> /dev/null \
    && sudo apt install xterm firefox xdg-utils openjdk-8-jdk fonts-droid-fallback fonts-wqy-zenhei fonts-wqy-microhei fonts-arphic-ukai fonts-arphic-uming -y 2> /dev/null\
    && sudo apt install ssh -y 2> /dev/null \
    && sudo apt clean 2> /dev/null \
    && echo "export DISPLAY=:0" >> ${HOME}/.bashrc \
    && /bin/bash -c "source ${HOME}/.bashrc" \
    && /bin/bash -c "rm -rf ${HOME}/.cache/pip " 