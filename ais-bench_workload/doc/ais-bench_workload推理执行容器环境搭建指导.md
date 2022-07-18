# ais-bench_workload推理执行容器环境搭建指导

## 1. 简介

本文基于华为昇腾镜像仓库推理基准镜像algorithm增加相关命令，用于构建容器环境，用于Ais-Bench推理负载包运行。

## 2. 下载基础镜像

本文基于昇腾镜像仓库algorithm基础镜像制作，链接为 (https://ascendhub.huawei.com/#/detail/algorithm) 请进入点击 "获取镜像"按钮，下载基础镜像。

本文示例基于华为昇腾基础镜像algorithm 22.0.RC1, CANN 5.1.RC1。镜像名称，22.0.RC1-ubuntu18.04。该镜像已经安装nnrt和python3.7.5。该类镜像有多个发行平台都可以作为基础镜像。

拉取基础镜像的方法请参照**附录1**进行。

下载完毕后，请按该官网"如何使用镜像"来配置物理机环境。其步骤3，可以参考附录2。

## 3.基于基准镜像构建新镜像

### 3.1 准备依赖程序包

工作目录algorithm文件如下：

目录文件树

```
root@root:/home/lhb/tool/algorithm# tree
.
├── aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
├── Dockerfile
└── loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl
```

说明：

- aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl， 来自于ais-bench_workload发行包aclruntime-aarch64.tar.gz
- loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl， 来自于ais-bench_workload发行包Ais-Bench-LoadGen-aarch64-1.1.tar.gz

### 3.2 创建Dockerfile

```bash
FROM ascendhub.huawei.com/public-ascendhub/algorithm:22.0.RC1-ubuntu18.04

MAINTAINER liangchaoming

USER root
RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak
# apt源加速
RUN sed -i "s@/archive.ubuntu.com/@/mirrors.163.com/@g" /etc/apt/sources.list  && rm -rf /var/lib/apt/lists/*  && apt-get update --fix-missing -o Acquire::http::No-Cache=True
# 恢复基础容器中python3.7.5在容器中的指向.容器支持python3、python3.7.5的python调用
RUN  mkdir -p /opt/package
RUN  ln -s /usr/local/python37/bin/python3 /usr/bin/python3.7.5 && ln -s /usr/local/python37/bin/pip3 /usr/bin/pip3.7.5

# 安装系统依赖
RUN apt-get install libglib2.0-dev libgl1-mesa-glx -y  && apt install vim -y
# 安装pip3依赖。
RUN pip3 install numpy tqdm  pycocotools  scikit-learn transformers  tokenization opencv_python -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
WORKDIR /opt/package
# 安装推理运行环境aclruntime和loadgen
COPY aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl /opt/package/aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
COPY loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl /opt/package/loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl
RUN pip3 install aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
RUN pip3 install loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl
# online install tensorflow1.15
RUN pip3 install https://files.pythonhosted.org/packages/35/9a/985a1642bc493b96c340da6db366124b2609c7a42ca53f643585c01e4d33/tensorflow_ascend-1.15.0-cp37-cp37m-manylinux2014_aarch64.whl
CMD ["source", "/usr/local/Ascend/nnrt/set_env.sh"]
```

说明：

如果需要网络代理，请在Dockerfile增加网络代理环境变量。在“USER root"下一行，增加类似如下环境变量：

```bash
# 设置网络代理环境变量
ENV http_proxy "http://xxxx:xxxx"
ENV https_proxy "http://xxxx:xxxx"
ENV ftp_proxy "http://xxxx:xxxx"
```



### 3.3 构建镜像

编译指令：

```
docker build -t ais-bench_workload-inference-arm:1.0 .
```

执行成功后，回显如下：

```
root@root:/home/lhb/tool/algorithm# docker images
REPOSITORY                                           TAG                       IMAGE ID            CREATED             SIZE
ais-bench_workload-inference-arm                     1.0                  d16debfbde9c        About an hour ago   2.83GB
```

## 3. 运行镜像

```
root@root:/home/lhb/tool/algorithm# docker run -itd -u root  -v /home/:/home --name asend_inference_aarch64  -e ASCEND_VISIBLE_DEVICES=0 52dbef81d817  /bin/bash
a1ed8ed48256f7ece143c986fd337aefb29f50a307f342cee1e88881618eb29a
root@root:/home/lhb/tool/algorithm# docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
a1ed8ed48256        52dbef81d817        "/bin/bash"         4 seconds ago       Up 3 seconds                            asend_inference_aarch64
root@root:~# docker exec -it a1ed8ed48256 bash
root@a1ed8ed48256:/opt/package#
```

说明：

- -d参数，后台执行。退出容器后容器还存在着

- 以root用户登录将物理机的/home目录映射到容器的/home目录

- 52dbef81d817是推理镜像ID

- A500小站驱动等部署较为特殊，其容器启动命令有其特殊性

  ```bash
  docker run -itd -u root --device=/dev/davinci0 --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc -v /usr/local/bin/npu-smi/:/usr/local/bin/npu-smi/ -v /home/data/miniD/driver/lib64/:/home/data/miniD/driver/lib64/ -v /home/:/home/ -e ASCEND_VISIBLE_DEVICES=0 52dbef81d817 /bin/bash
  ```

  容器拉起后，进入容器中，执行以下语句声明下系统库最新路径

  ```
  expert LD_LIBRARY_PATH=/home/data/miniD/driver/lib64/:$LD_LIBRARY_PATH
  ```

  A500环境资源有限，请及时清理docker资源保证推理测试顺利进行

## 4. 附录

### 4.1 修改linux用户HwHiAiUser的id值为1000

背景：物理机当前HwHiAiUser的id是1001，zjut-msadvisor用户的id是1000

步骤：

```bash
root@root:~# usermod -u 1003 zjut-msadvisor
usermod: user zjut-msadvisor is currently used by process 91928
root@root:~# ps -ef |grep 91928
zjut-ms+ 91928     1  0 12:33 ?        00:00:00 /lib/systemd/systemd --user
zjut-ms+ 91929 91928  0 12:33 ?        00:00:00 (sd-pam)
root     94128 92493  0 12:49 pts/0    00:00:00 grep --color=auto 91928
root@root:~# kill -9 91928 91929
root@root:~# usermod -u 1003 zjut-msadvisor
usermod: user zjut-msadvisor is currently used by process 92042
root@root:~# kill -9 92042
root@root:~# usermod -u 1003 zjut-msadvisor
root@root:~# groupmod -g 1003 zjut-msadvisor
root@root:~# id zjut-msadvisor
uid=1003(zjut-msadvisor) gid=1003(zjut-msadvisor) groups=1003(zjut-msadvisor)
root@root:~# usermod -u 1000 HwHiAiUser
root@root:~# groupmod -g 1000 HwHiAiUser
root@root:~# id HwHiAiUser
uid=1000(HwHiAiUser) gid=1000(HwHiAiUser) groups=1000(HwHiAiUser)
```

说明：新id--1003不得与现有用户id重复
