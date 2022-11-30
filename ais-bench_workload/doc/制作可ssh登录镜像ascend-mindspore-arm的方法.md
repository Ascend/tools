





# 制作可ssh登录镜像ascend-mindspore-arm的方法


本文均以Dockerfile实现镜像说明。
## 1.获取基础镜像
### 1.1 华为开源arm镜像

华为开源镜像库网址：https://ascendhub.huawei.com/#/index
以下以基础镜像ascend-mindspore-arm为例，集成mindspore r1.5来说明：

- 基础镜像ascend-mindspore-arm网址：https://ascendhub.huawei.com/#/detail/ascend-mindspore-arm。 ubuntu18.04系统
- 登录基础镜像网址，点击“获取镜像”
- 在随后出现的Uniportal帐号登录界面，选择账号/邮箱登录、手机号码登录、短信登录三种方式之一，登入。如果网页出现“禁止”字样，请更换登录方式。建议“短信登录”方法登录。
- 版本界面，选择版本“21.0.1.spc001”， 点击下载列表对应的“立即下载”，进入下载界面
- 下载界面会显示下载步骤，请按步骤执行。

​示例：

​获取登录访问权限并复制到工作节点执行：

```
docker login -u WX926930 -p 4u9xchG5IzMuGgVFxvvMVH895SwE0tIXAQrBwl0C46uHzhMwYEq5eWV0EvYbG7CdO ascendhub.huawei.com
```

​下载镜像：

```
docker pull ascendhub.huawei.com/public-ascendhub/ascend-mindspore-arm:21.0.1.spc001
```

-   在工作节点查询镜像：

```
(base) root@node62:/home/lhb/code/ascend-mindspore-arm_ssh# docker images |grep ascend-mindspore-arm
ascendhub.huawei.com/public-ascendhub/ascend-mindspore-arm   21.0.1.spc001       67bcd3733d57        5 weeks ago         6.67GB
(base) root@node62:/home/lhb/code/ascend-mindspore-arm_ssh#
```
### 1.2 自定义欧拉镜像
以下以EulerOS 2.0(SP8)平台ascend-mindspore-arm-base:1.0基础镜像为例说明：
+ 镜像功能内部集成训练通用的第三方库（系统包、pip3、openssh_server）, 未集成MindSpore框架、ascend toolkit工具包
+ 以下仅以实现ssh登录说明,请自行部署业务驱动和工具包
## 2.目标镜像制作
工作目录ascend-mindspore-arm_ssh

### 2.1 镜像相关文件准备
#### 2.1.1 华为开源arm镜像

目录文件如下：

- ​Ascend-cann-toolkit_5.0.3_linux-aarch64.run  请自行下载
- ​ Dockerfile。内容如2.2.1 小节所示
- ​ 容器启动run_container.sh脚本

​内容：

```
docker run -it --ipc=host --device=/dev/davinci0 --device=/dev/davinci1 --device=/dev/davinci2 --device=/dev/davinci3 --device=/dev/davinci4 --device=/dev/davinci5 --device=/dev/davinci6 --device=/dev/davinci7 --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc -v /usr/local/Ascend/driver:/usr/local/Ascend/driver -v /usr/local/Ascend/add-ons/:/usr/local/Ascend/add-ons/ -v /var/log/npu/:/usr/slog  -v /home/:/home -p 8000:22  ascend-mindspore-arm:ms1.5  bash  -c "/etc/init.d/ssh start && /bin/bash"
```

说明：-p 8000:22 表示外部端口8000映射容器22端口，提供外部ssh访问能力
#### 2.1.2 自定义欧拉镜像
目录文件如下：
- Dockerfile 内容如2.2.2小节所示。
- sshpass-1.06.tar.gz  点[这里](https://nchc.dl.sourceforge.net/project/sshpass/sshpass/1.06/sshpass-1.06.tar.gz)下载
- run_container.sh容器拉起脚本
内容：
```
docker run -it --ipc=host --device=/dev/davinci0 --device=/dev/davinci1 --device=/dev/davinci2 --device=/dev/davinci3 --device=/dev/davinci4 --device=/dev/davinci5 --device=/dev/davinci6 --device=/dev/davinci7 --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc -v /usr/local/Ascend/driver:/usr/local/Ascend/driver -v /usr/local/Ascend/add-ons/:/usr/local/Ascend/add-ons/ -v /var/log/npu/:/usr/slog  -v /home/:/home -p 8000:22  ascend-mindspore-arm-base:ms1.5  bash  -c "/usr/sbin/sshd -D && /bin/bash"
```

### 2.2 创建Dockerfile
#### 2.2.1 华为开源arm镜像
工作目录创建名字为Dockerfile文件，内容如下：

```bash
FROM ascendhub.huawei.com/public-ascendhub/ascend-mindspore-arm:21.0.1.spc001
MAINTAINER liangchaoming
RUN apt-get update \
    && /usr/bin/python3.7 -m pip install --upgrade pip \
    && apt-get install libnuma-dev openssh-server apt-utils sshpass -y \
    && /usr/local/Ascend/nnae/latest/script/uninstall.sh
ADD Ascend-cann-toolkit_5.0.3_linux-aarch64.run /opt/packet/Ascend-cann-toolkit_5.0.3_linux-aarch64.run
RUN /opt/packet/Ascend-cann-toolkit_5.0.3_linux-aarch64.run --full \
    && pip install https://ms-release.obs.cn-north-4.myhuaweicloud.com/1.5.0/MindSpore/ascend/aarch64/mindspore_ascend-1.5.0-cp37-cp37m-linux_aarch64.whl --trusted-host ms-release.obs.cn-north-4.myhuaweicloud.com -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && echo 'root:root'|chpasswd \
    && mkdir -p /var/run/sshd \
    && sed -i 's/.*PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config
EXPOSE  22
CMD     ["/usr/sbin/sshd", "-D"]
```
#### 2.2.2 自定义欧拉镜像

```bash
FROM ascend-mindspore-base:1.0
MAINTAINER liangchaoming
COPY sshpass-1.0.6.tar.gz /opt/packet/sshpass-1.0.6.tar.gz
RUN cd /opt/packet/ \
    && tar -xvzf sshpass-1.0.6.tar.gz \
    && cd sshpass-1.0.6 \
    && ./configure --prefix=/usr/local/ \
    && make && make install
RUN echo 'root:root'|chpasswd \
    && mkdir -p /var/run/sshd \
    && sed -i 's/.*PermitRootLogin.*/PermitRootLogin yes/g' /etc/ssh/sshd_config
EXPOSE  22
```

### 2.3 编译镜像

- 创建指令：

```
docker build -t ascend-mindspore-arm-base:ms1.5 .
```
如果在黄区需要自定义在线安装软件包，请增加代理参数执行以下指令：
```
docker build --build-arg http_proxy=http://ptaishanpublic2:Huawei123#10.174.217.27:8080 --build-arg https_proxy=http://ptaishanpublic2:Huawei123#10.174.217.27:8080 --build-arg ftp_proxy=ftp://ptaishanpublic2:Huawei123#10.174.217.27:8080 -t ascend-mindspore-arm-base:ms1.5 .
```

注意：指令末尾的"."，表示使用当前目录的Dockfile。tag--ms1.5, 请自己决定，这里仅仅示意

- 查询当前节点镜像列表：

```
(base) root@node64:/home/lhb/test2# docker images |grep ascend-mindspore-arm
ascend-mindspore-arm-base                 ms1.5               2454f44b88ee        5 hours ago         12.1GB
```

- 执行./run_container.sh创建工作容器，并查询容器状态

```
(base) root@node64:/home/lhb/test2# docker ps
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS                  NAMES
0f6f9971a646        ascend-mindspore-arm-base:ms1.5   "bash -c '/etc/init.…"   3 hours ago         Up 3 hours          0.0.0.0:8000->22/tcp   compassionate_cerf
```
## 3. 拉起容器
执行命令：bash run_container.sh
## 4. ssh登录验证

在其它节点执行 ssh root@{IP} -p 8000

示例：ssh root@90.90.66.64 -p 8000（密码root)

执行结果：

```
[root@node66 ~]# ssh root@90.90.66.64 -p 8000
root@90.90.66.64's password:
Welcome to Ubuntu 18.04.5 LTS (GNU/Linux 4.15.0-29-generic aarch64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage
This system has been minimized by removing packages and content that are
not required on a system that users do not log into.

To restore this content, you can run the 'unminimize' command.
Last login: Thu Nov 18 09:10:30 2021 from 90.90.66.66
root@0f6f9971a646:~#
```

