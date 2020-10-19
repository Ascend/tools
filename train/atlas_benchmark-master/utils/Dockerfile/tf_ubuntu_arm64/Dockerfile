# VERSION: 20.0.0.RC1
# 说明：提前下载好昇腾cmake包和OpenMPI软件包在在目录下
FROM ubuntu:18.04

ENV http_proxy="http://ptaishanpublic2:Huawei123@90.90.64.10:8080"
ENV https_proxy="http://ptaishanpublic2:Huawei123@90.90.64.10:8080"
ENV no_proxy=127.0.0.1,.huawei.com,localhost,local,.local


ARG TF_PKG=tensorflow-1.15.0-cp37-cp37m-linux_aarch64.whl
ARG HOST_ASCEND_BASE=/usr/local/Ascend
ARG NNAE_PATH=/usr/local/Ascend/nnae/latest
ARG TF_PLUGIN_PATH=/usr/local/Ascend/tfplugin/latest
ARG INSTALL_ASCEND_PKGS_SH=install_ascend_pkgs.sh
ARG PREBUILD_SH=prebuild.sh
ARG POSTBUILD_SH=postbuild.sh
WORKDIR /tmp
COPY . ./
COPY sources.list /etc/apt/ 
COPY pip.conf /root/.pip/

# 触发prebuild.sh
RUN bash -c "test -f $PREBUILD_SH && bash $PREBUILD_SH || true"


# 系统包
RUN apt update
RUN apt install --no-install-recommends python3.7 python3.7-dev -y
RUN apt install --no-install-recommends curl g++ gcc pkg-config unzip -y
RUN apt install --no-install-recommends libblas3 liblapack3 liblapack-dev libblas-dev gfortran libhdf5-dev libffi-dev libssl-dev\
                                        libicu60 libxml2 -y
# benchmark系统依赖包
RUN apt-get update
RUN apt-get install -y openssh-client
RUN apt-get install -y net-tools
RUN apt-get install -y openssh-server
RUN apt-get install -y inetutils-ping
RUN apt-get install -y psmisc
RUN apt-get install -y iproute2
RUN apt-get install -y wget
RUN apt-get install -y vim

# pip3.7
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    cd /tmp && \
    apt-get download python3-distutils && \
    dpkg-deb -x python3-distutils_*.deb / && \
    rm python3-distutils_*.deb && \
    cd - && \
    python3.7 get-pip.py && \
    rm get-pip.py

# HwHiAiUser
RUN groupadd HwHiAiUser && \
    useradd -g HwHiAiUser -m -d /home/HwHiAiUser HwHiAiUser

# python包
RUN pip3.7 install numpy && \
    pip3.7 install decorator && \
    pip3.7 install attrs && \
    pip3.7 install sympy==1.4 && \
    pip3.7 install cffi==1.12.3 && \
    pip3.7 install pyyaml && \
    pip3.7 install wheel && \
    pip3.7 install pathlib2 && \
    pip3.7 install grpcio && \
    pip3.7 install grpcio-tools && \
    pip3.7 install protobuf && \
    pip3.7 install scipy && \
    pip3.7 install Pillow==5.3.0 && \
    pip3 install torchvision --no-deps && \
    pip3.7 install requests

# Ascend包
RUN bash $INSTALL_ASCEND_PKGS_SH

# 安装Cmake
RUN tar -zxvf cmake-3.18.0.tar.gz
WORKDIR cmake-3.18.0
RUN mkdir -p /usr/local/cmake-3.18.0
RUN ./configure --prefix=/usr/local/cmake-3.18.0
RUN make && make install

# 安装OpenMPI开源库
WORKDIR /tmp

RUN tar -jxvf openmpi-4.0.2.tar.bz2
WORKDIR openmpi-4.0.2
RUN mkdir -p /usr/local/mpirun4.0.2
RUN ./configure --prefix=/usr/local/mpirun4.0.2
RUN make && make install

WORKDIR /tmp

# TF安装
ENV LD_LIBRARY_PATH=\
/usr/lib/aarch64-linux-gnu/hdf5/serial:\
$HOST_ASCEND_BASE/add-ons:\
$NNAE_PATH/fwkacllib/lib64:\
$HOST_ASCEND_BASE/driver/lib64/common:\
$HOST_ASCEND_BASE/driver/lib64/driver:$LD_LIBRARY_PATH

RUN pip3.7 install $TF_PKG

# 环境变量
ENV GLOG_v=2
ENV TBE_IMPL_PATH=$NNAE_PATH/opp/op_impl/built-in/ai_core/tbe
ENV TF_PLUGIN_PKG=$TF_PLUGIN_PATH/tfplugin/python/site-packages
ENV FWK_PYTHON_PATH=$NNAE_PATH/fwkacllib/python/site-packages
ENV PATH=$NNAE_PATH/fwkacllib/ccec_compiler/bin:$PATH
ENV ASCEND_OPP_PATH=$NNAE_PATH/opp
ENV PYTHONPATH=\
$FWK_PYTHON_PATH:\
$FWK_PYTHON_PATH/auto_tune.egg:\
$FWK_PYTHON_PATH/schedule_search.egg:\
$TF_PLUGIN_PKG:\
$TBE_IMPL_PATH:\
$PYTHONPATH
ENV OPENMPI=/usr/local/mpirun4.0.2/
ENV LD_LIBRARY_PATH=$OPENMPI/lib/
ENV PATH=$OPENMPI/bin:$PATH

# 免密登录
RUN ssh-keygen -t rsa -f ~/.ssh/id_rsa -P '' && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    sed -i 's/PermitEmptyPasswords yes/PermitEmptyPasswords no /' /etc/ssh/sshd_config && \ 
    sed -i 's/PermitRootLogin without-password/PermitRootLogin yes /' /etc/ssh/sshd_config && \ 
    echo " StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \ 
    echo " UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config && \ 
    echo "root:1234" | chpasswd 
CMD [ "sh", "-c", "sudo service ssh start; bash"]


# 触发postbuild.sh
RUN bash -c "test -f $POSTBUILD_SH && bash $POSTBUILD_SH || true" && \
    rm $POSTBUILD_SH