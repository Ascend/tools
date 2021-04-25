# docker镜像使用指导

该使用指导将指导你拉取一个3.3.0.alpha001  atlas200dk的开发运行环境。环境内已经安装好了开发和运行环境，用户直接运行样例。    
 **docker容器中普通用户用户名：HwHiAiUser，密码：HwHiAiUser     
            root用户用户名：root，密码：root**     
 
**1、安装Atlas200DK运行环境**

​	搭建最新版本运行环境（3.3.0alpha001，读卡器场景）

​	[制卡方式](https://support.huaweicloud.com/environment-deployment-Atlas200DK202/atlased_04_0012.html)    

**2、配置Atlas200DK连接网络**    
参考[开发者板设置联网](https://gitee.com/ascend/samples/blob/master/cplusplus/environment/prepare_ENV/README_200DK_CN.md)

**3、更换apt源（可选）**

官方源推荐外国用户使用

```
deb http://ports.ubuntu.com/ bionic main restricted universe multiverse

deb-src http://ports.ubuntu.com/ bionic main restricted universe multiverse

deb http://ports.ubuntu.com/ bionic-updates main restricted universe multiverse

deb-src http://ports.ubuntu.com/ bionic-updates main restricted universe multiverse

deb http://ports.ubuntu.com/ bionic-security main restricted universe multiverse

deb-src http://ports.ubuntu.com/ bionic-security main restricted universe multiverse

deb http://ports.ubuntu.com/ bionic-backports main restricted universe multiverse

deb-src http://ports.ubuntu.com/ bionic-backports main restricted universe multiverse

deb http://ports.ubuntu.com/ubuntu-ports/ bionic main universe restricted

deb-src http://ports.ubuntu.com/ubuntu-ports/ bionic main universe restricted
```



国内用户可使用华为arm源

```
sudo wget -O /etc/apt/sources.list https://repo.huaweicloud.com/repository/conf/Ubuntu-Ports-bionic.list
```

**4、切换到root用户，更新源并安装docker，这里使用docker.io即可**

```
su - root
apt-get update
apt-get install docker.io
```

**5、创建docker用户组，应用用户加入docker组**

（1）创建docker用户组

```
 sudo groupadd docker
```

（2） 应用用户加入docker用户组**

```
 sudo usermod -aG docker ${USER}
```

（3）重启docker服务

```
 sudo systemctl restart docker
```

（4）切换或者退出当前账户再从新登入

```
su root             切换到root用户
su ${USER}          再切换到原来的应用用户以上配置才生效
```
### 直接拉取atlas200dk合设环境镜像
命令行中执行如下命令拉取镜像：
    
**docker pull swr.cn-north-4.myhuaweicloud.com/ascend-develop/atlas200dk-catenation:3.3.0.alpha001-full**


### 配置合设环境

1. 用如下命令查看下载的镜像，可以看到你刚才下载的镜像ID.。

    **docker images**

2. 用如下命令创建容器，镜像ID替换为你查到的。

    >   docker run -it --privileged --net=host --device=/dev/davinci0 --device=/dev/davinci_manager --device=/dev/svm0 --device=/dev/log_drv --device=/dev/event_sched --device=/dev/upgrade --device=/dev/hi_dvpp --device=/dev/memory_bandwidth --device=/dev/ts_aisle -v /var:/var -v /etc/hdcBasic.cfg:/etc/hdcBasic.cfg -v /etc/rc.local:/etc/rc.local -v /sys:/sys -v /usr/bin/sudo:/usr/bin/sudo -v /usr/lib/sudo/:/usr/lib/sudo/ -v /etc/sudoers:/etc/sudoers/  -v /usr/lib64:/usr/lib64 atlas200dk-catenation:3.3.0.alpha001-full bash
    

    > **说明：**     
    >
    > -   该命令只是在创建容器时运行一次即可，后面在进入容器无需这么复杂的命令。

3. 此容器内的网络环境与外界宿主机(host)一样，参考如下链接的官方文档配置宿主机网络可以与开发板联通。

    [https://support.huaweicloud.com/usermanual-A200dk_3000/atlas200dk_02_0012.html](https://support.huaweicloud.com/usermanual-A200dk_3000/atlas200dk_02_0012.html)


### 常用操作

1. <a name="zh-cn_topic_2_2"></a>**换源操作**

    1. 命令行执行以下命令，备份原来的更新源

        **cp /etc/apt/sources.list /etc/apt/sources.list.backup**

    2. 修改更新源　

        打开sources.list (这就是存放更新源的文件)。

        **gedit /etc/apt/sources.list**
        
        将下面所有内容复制，粘贴并覆盖sources.list文件中的所有内容，覆盖后保存。
        
        \# deb cdrom:[Ubuntu 16.04 LTS _Xenial Xerus_ - Release amd64 (20160420.1)]/ xenial main restricted
        
        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted
    
        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial universe

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates universe

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial multiverse

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates multiverse

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security universe

        deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security multiverse

    3. 让更新源生效

        sudo apt-get update

2. **docker常用操作指令集**

    1. 如何查看镜像。
       
        **docker images**

    2. 如何创建容器。

        有了镜像以后，可通过docker run命令创建容器，在本应用场景下创建容器指令如下。

        **docker run -t -i --privileged -v \\$HOME/.Xauthority:/root/.Xauthority --net=host -e DISPLAY=\\$DISPLAY  
   [ImageID]**

    3. 如何退出容器。
       
        在容器中，使用exit指令退出容器，但是如果是docker run命令进入的容器，则退出后容器就会停止。
    
    4. 如何查看容器

        查看所有容器，包括已经停止的容器
        
        **docker ps -a**

        查看正在运行的容器

        **docker ps**

    5. 如何进入容器

        - docker run 命令创建完容器，exit后，请用如下的方式进入。
        
            命令行中使用如下指令查看你刚才退出的容器ID

            **docker ps -a**

            执行如下指令启动容器，容器ID要替换为你查到的CONTATNER_ID。

            **docker start 容器ID**

            继续执行如下指令，进入容器，容器ID要替换为你查到的CONTATNER_ID。

            **docker exec -it 容器ID /bin/bash**

        - docker exec方式进入容器，exit后，容器并不会停止，下次进入仍然使用docker exec方式进入即可

            命令行中使用如下指令查看你刚才退出的容器ID

            **docker ps -a**

            执行如下指令，进入容器，容器ID要替换为你查到的CONTATNER_ID。

            **docker exec -it 容器ID /bin/bash**

    6. 如何停止容器。

        **docker stop 容器ID**

    7. 如何启动容器。

        **docker start 容器ID**

    8. 如何删除容器。

        需要在容器停止的时候才可以删除。
        
        **docker rm 容器ID**

    9. 如何删除镜像。

        需要在镜像创建的所有容器都停止的情况下才可以删除。
        
        **docker rmi 镜像ID**
    
    10. 如何将主机中的数据拷贝到容器中。

        **docker cp 主机文件路径 容器ID:/容器中存放数据的目录**
        
    11. 如何清理docker内存。

        以下分别进行容器清理、镜像清理、volumes目录清理。

        **docker ps --filter status=dead --filter status=exited -aq | xargs -r docker rm -v**

        **docker images --no-trunc | grep '<none>' | awk '{ print $3 }' | xargs -r docker rmi**

        **docker volume ls -f dangling=true | awk '{ print $2 }' | xargs docker volume rm**

## 参考资料

1. docker中文入门手册

    http://www.docker.org.cn/book/docker/what-is-docker-16.html

2. docker官方快速入门

    https://docs.docker.com/get-started/

3. 昇腾社区官网

    https://www.huaweicloud.com/ascend

4. 昇腾社区Atlas200DK板块论坛

    https://bbs.huaweicloud.com/forum/forum-949-1.html








