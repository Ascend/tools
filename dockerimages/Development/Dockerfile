FROM ubuntu:18.04
# 配置ubuntu基础环境
ENV DEBIAN_FRONTEND=noninteractive
RUN set -ex && apt update -y 2> /dev/null && apt install vim -y 2> /dev/null && apt install sudo -y 2> /dev/null \
    && apt install python -y 2> /dev/null \
    && apt install python3 -y \
    && apt install python-pip -y 2> /dev/null \
    && apt install python3-pip -y \
    && apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk -y 2> /dev/null \
    && python3.6 -m pip install --upgrade pip  -i https://mirrors.huaweicloud.com/repository/pypi/simple 2> /dev/null \
    && python3.6 -m pip install Cython numpy pillow tornado==5.1.0 protobuf  -i https://mirrors.huaweicloud.com/repository/pypi/simple 2> /dev/null \
    && apt-get install python3-opencv -y

# 配置安装运行用户信息
RUN set -ex && apt update -y 2> /dev/null && apt install net-tools -y 2> /dev/null  && apt install iputils-ping -y 2> /dev/null \
    && echo "root:root" | chpasswd \
    && useradd -d /home/HwHiAiUser -m HwHiAiUser \
    && echo "HwHiAiUser:HwHiAiUser" | chpasswd \
    && chmod 750 /home/HwHiAiUser \
    && chmod u+w /etc/sudoers \
    && sed -i '/# User privilege specification/a\HwHiAiUser ALL=(ALL:ALL)   ALL' /etc/sudoers \
    && chmod u-w /etc/sudoers 

# 安装apt依赖
RUN set -ex && apt-get install -y gcc g++ make cmake zlib1g zlib1g-dev libbz2-dev libsqlite3-dev libssl-dev libxslt1-dev libffi-dev unzip pciutils net-tools libncursesw5-dev 2> /dev/null \
    && apt install ssh -y 2> /dev/null

ARG NNRT_PKG
ARG TOOLKIT_PKG
# 拷贝软件包
USER HwHiAiUser
WORKDIR /home/HwHiAiUser/
COPY --chown=HwHiAiUser:HwHiAiUser Python-3.7.5.tgz .
COPY --chown=HwHiAiUser:HwHiAiUser $TOOLKIT_PKG .
COPY --chown=HwHiAiUser:HwHiAiUser $NNRT_PKG .

# 安装python3.7
RUN set -ex && tar -zxvf Python-3.7.5.tgz \
    && cd Python-3.7.5 \
    && ./configure --prefix=/usr/local/python3.7.5 --enable-loadable-sqlite-extensions --enable-shared 2> /dev/null \
    && make 2> /dev/null \
    && echo 'HwHiAiUser' | sudo -S make install 2> /dev/null \
    && echo 'HwHiAiUser' | sudo -S cp /usr/local/python3.7.5/lib/libpython3.7m.so.1.0 /usr/lib


RUN set -ex && echo 'HwHiAiUser' | sudo -S ln -s /usr/local/python3.7.5/bin/python3 /usr/local/python3.7.5/bin/python3.7.5 \
    && echo 'HwHiAiUser' | sudo -S ln -s /usr/local/python3.7.5/bin/pip3 /usr/local/python3.7.5/bin/pip3.7.5 \
    && echo "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:/home/HwHiAiUser/Ascend/nnrt/latest/acllib/lib64:/usr/lib64:/home/HwHiAiUser/ascend_ddk/arm/lib:$LD_LIBRARY_PATH" >> ${HOME}/.bashrc \
    && echo "export PATH=/usr/local/python3.7.5/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/HwHiAiUser/Ascend/ascend-toolkit/latest/atc/ccec_compiler/bin:/home/HwHiAiUser/Ascend/ascend-toolkit/latest/atc/bin:$PATH" >> ${HOME}/.bashrc \
    && echo "export PYTHONPATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/pyACL/python/site-packages/acl:$PYTHONPATH" >> ${HOME}/.bashrc \
    && echo "export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest" >> ${HOME}/.bashrc \
    && echo "export ASCEND_OPP_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/opp" >> ${HOME}/.bashrc \
    && /bin/bash -c "source ${HOME}/.bashrc" \
# 安装pip依赖
RUN set -ex && /usr/local/python3.7.5/bin/pip3.7.5 install --upgrade pip --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install attrs --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install psutil --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install decorator --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install numpy --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install protobuf==3.11.3 --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install scipy --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install sympy --user \
    && /usr/local/python3.7.5/bin/pip3.7.5 install  cffi --user

USER HwHiAiUser
WORKDIR /home/HwHiAiUser/
ENV USER=HwHiAiUser
ENV LD_LIBRARY_PATH /usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
ENV PATH /usr/local/python3.7.5/bin:$PATH
RUN chmod +x $TOOLKIT_PKG \
    && /bin/bash $TOOLKIT_PKG --install
RUN chmod +x $NNRT_PKG \
    && /bin/bash $NNRT_PKG --install \
    && rm -rf $TOOLKIT_PKG \
    && rm -rf $NNRT_PKG \
    && rm -rf Python-3.7.5.tgz \