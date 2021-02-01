FROM ubuntu:18.04
COPY sources.list /etc/apt/
RUN set -ex && apt update -y 2> /dev/null && apt install net-tools -y 2> /dev/null  && apt install iputils-ping -y 2> /dev/null \
    && apt install vim -y 2> /dev/null && apt install sudo 2> /dev/null \
    && echo "root:root" | chpasswd \
    && useradd -d /home/ascend -m ascend \
    && echo "ascend:ascend" | chpasswd \
    && chmod 750 /home/ascend \
    && chmod u+w /etc/sudoers \
    && sed -i '/# User privilege specification/a\ascend ALL=(ALL:ALL)   ALL' /etc/sudoers \
    && chmod u-w /etc/sudoers 
USER ascend
WORKDIR /home/ascend/
COPY --chown=ascend:ascend mindstudio.tar.gz ./ 
COPY --chown=ascend:ascend Python-3.7.5.tgz ./ 
COPY --chown=ascend:ascend Ascend-Toolkit-20.0.0.RC1-x86_64-linux_gcc7.3.0.run ./

RUN set -ex && echo 'ascend' | sudo -S apt install  gcc make cmake unzip zlib1g zlib1g-dev libsqlite3-dev openssl libssl-dev libffi-dev pciutils net-tools g++-5-aarch64-linux-gnu -y 2> /dev/null \
    && sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu -y 2> /dev/null \
    && sudo apt install xterm firefox xdg-utils openjdk-8-jdk fonts-droid-fallback fonts-wqy-zenhei fonts-wqy-microhei fonts-arphic-ukai fonts-arphic-uming -y 2> /dev/null\
    && sudo apt install ssh -y 2> /dev/null \
    && sudo apt clean 2> /dev/null \
    && echo "export DISPLAY=:0" >> ${HOME}/.bashrc \
    && /bin/bash -c "source ${HOME}/.bashrc" \
    && /bin/bash -c "rm -rf ${HOME}/.cache/pip " 
