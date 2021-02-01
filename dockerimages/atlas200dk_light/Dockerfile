FROM ubuntu:16.04
COPY sources.list /etc/apt/
RUN set -ex && apt update -y 2> /dev/null && apt install net-tools -y 2> /dev/null  && apt install iputils-ping -y 2> /dev/null \
    && apt install vim -y 2> /dev/null && apt install sudo 2> /dev/null 
RUN echo "root:root" | chpasswd \
WORKDIR /root/
RUN set -ex && apt install xterm python python3 python-pip python3-pip -y 2> /dev/null \
    && apt install libcanberra-gtk-module -y 2> /dev/null \
    && apt install wget -y 2> /dev/null \
    && apt install fonts-droid-fallback ttf-wqy-zenhei ttf-wqy-microhei fonts-arphic-ukai fonts-arphic-uming -y 2> /dev/null \
    && pip2 install numpy==1.14 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com 2> /dev/null \
    && pip2 install decorator --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com 2> /dev/null \
    && pip3 install numpy --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com 2> /dev/null \
    && pip3 install decorator --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com 2> /dev/null \
    && apt install openjdk-8-jdk -y 2> /dev/null \
    && apt install qemu-user-static binfmt-support python3-yaml gcc-aarch64-linux-gnu g++-aarch64-linux-gnu -y 2> /dev/null \
    && apt install ssh -y 2> /dev/null \
    && echo "export DISPLAY=:0" >> ${HOME}/.bashrc \
    && echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ${HOME}/.bashrc \
    && echo "export PATH=$JAVA_HOME/bin:$PATH" >> ${HOME}/.bashrc \
    && /bin/bash -c "source ${HOME}/.bashrc" 
COPY make_sd_card.py make_ubuntu_sd.sh /root/mksd/
