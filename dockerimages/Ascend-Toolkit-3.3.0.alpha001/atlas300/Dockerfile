FROM ubuntu:18.04
COPY sources.list /etc/apt/
RUN set -ex && apt update -y 2> /dev/null && apt install vim -y 2> /dev/null && apt install sudo -y 2> /dev/null \
    && apt install python -y 2> /dev/null \
    && apt install python3 -y 2> /dev/null \
    && apt install python-pip -y 2> /dev/null \
    && apt install python3-pip -y 2> /dev/null \ 
    && apt install git -y 2> /dev/null \
    && python3.6 -m pip install --upgrade pip -i https://mirrors.huaweicloud.com/repository/pypi/simple \
    && echo "root:root" | chpasswd \
    && useradd -d /home/HwHiAiUser -m HwHiAiUser \
    && echo "HwHiAiUser:Mind@123" | chpasswd \
    && chmod 750 /home/HwHiAiUser \
    && chmod u+w /etc/sudoers \
    && sed -i '/# User privilege specification/a\HwHiAiUser ALL=(ALL:ALL)   ALL' /etc/sudoers \
    && chmod u-w /etc/sudoers
USER HwHiAiUser
WORKDIR /home/HwHiAiUser/
COPY --chown=HwHiAiUser:HwHiAiUser Ascend-cann-toolkit_3.3.0.alpha001_linux-x86_64.run ./
COPY --chown=HwHiAiUser:HwHiAiUser Python-3.7.5.tgz ./
COPY --chown=HwHiAiUser:HwHiAiUser Ascend-cann-nnrt_3.3.0.alpha001_linux-x86_64.run ./
WORKDIR /home/HwHiAiUser/
RUN set -ex  && echo 'Mind@123' | sudo -S apt install  gcc make cmake unzip zlib1g zlib1g-dev libsqlite3-dev openssl libssl-dev libffi-dev pciutils net-tools g++-5-aarch64-linux-gnu -y \
    && sudo apt install qemu-user-static binfmt-support python3-yaml gcc-aarch64-linux-gnu g++-aarch64-linux-gnu -y \
    && sudo apt install ssh -y
WORKDIR /home/HwHiAiUser/
RUN set -ex && tar -zxvf Python-3.7.5.tgz \
    && cd Python-3.7.5 \
    && ./configure --prefix=/usr/local/python3.7.5 --enable-loadable-sqlite-extensions --enable-shared \
    && make \
    && echo 'Mind@123' | sudo -S make install
WORKDIR /home/HwHiAiUser/
RUN set -ex && echo 'Mind@123' | sudo -S  sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/local/python3.7.5/bin/python3.7.5 \
    && sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/local/python3.7.5/bin/pip3.7.5 \
    && sudo cp /usr/local/python3.7.5/lib/libpython3.7m.so.1.0 /usr/lib \
    && echo "export DISPLAY=:0" >> ${HOME}/.bashrc \
    && echo "export USER=HwHiAiUser" >> ${HOME}/.bashrc \
    && echo "export install_path=/home/HwHiAiUser/Ascend/ascend-toolkit/latest" >> ${HOME}/.bashrc \
    && echo "export PATH=/usr/local/python3.7.5/bin:/home/HwHiAiUser/Ascend/ascend-toolkit/latest/atc/ccec_compiler/bin:/home/HwHiAiUser/Ascend/ascend-toolkit/latest/atc/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> ${HOME}/.bashrc \    
    && echo "export ASCEND_OPP_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/opp" >> ${HOME}/.bashrc \   
    && echo "export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest" >> ${HOME}/.bashrc \   
    && echo "export PYTHONPATH=/home/HwHiAiUser/Ascend/nnrt/latest/pyACL/python/site-packages/acl" >> ${HOME}/.bashrc \   
    && echo "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:/home/HwHiAiUser/Ascend/nnrt/latest/acllib/lib64:/home/HwHiAiUser/Ascend/ascend-toolkit/latest/atc/lib64:/home/HwHiAiUser/ascend_ddk/x86/lib:/usr/local/Ascend/driver/lib64" >> ${HOME}/.bashrc \    
    && /bin/bash -c "source ${HOME}/.bashrc" \
    && /usr/local/python3.7.5/bin/pip3.7.5 install attrs psutil decorator numpy protobuf==3.11.3 scipy sympy cffi grpcio grpcio-tools requests --user -i https://mirrors.huaweicloud.com/repository/pypi/simple
WORKDIR /home/HwHiAiUser/
ENV LD_LIBRARY_PATH /usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
ENV PATH /usr/local/python3.7.5/bin:$PATH
ENV USER=HwHiAiUser
ENV DISPLAY=:0
RUN echo $PATH
RUN chmod +x Ascend-cann-toolkit_3.3.0.alpha001_linux-x86_64.run \
    && ./Ascend-cann-toolkit_3.3.0.alpha001_linux-x86_64.run --install
RUN chmod +x Ascend-cann-nnrt_3.3.0.alpha001_linux-x86_64.run \
    && ./Ascend-cann-nnrt_3.3.0.alpha001_linux-x86_64.run --install \
    && rm -rf Ascend-cann-toolkit_3.3.0.alpha001_linux-x86_64.run \
    && rm -rf Ascend-cann-nnrt_3.3.0.alpha001_linux-x86_64.run \
    && rm -rf Python-3.7.5.tgz 

