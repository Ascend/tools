# docker镜像使用指导

本指导将提供ubuntu环境下拉取20.1版本docker开发环境的方法。   
 **docker容器中普通用户用户名：HwHiAiUser，密码：Mind@123      
            root用户用户名：root，密码：root**     
 
## 第一步：安装docker（如果已经安装docker可跳过该步骤）
1. 非root用户在命令行中输入如下命令来获取安装docker的脚本。   
    **curl -fsSL https://get.docker.com -o get-docker.sh**  
    > **说明：**     
    >
    > -   如果命令失败，按照提示执行sudo apt install curl。若再次提示curl: (1) Protocol https not supported or disabled in libcurl报错，请输入apt-get update更新软件源。
    
2. 执行以下命令进行docker的安装。   
    **sh get-docker.sh**   
    > **说明：**     
    >
    > -   如果安装失败，请进行[换源操作](#zh-cn_topic_2_2)，将本地源更换为清华源。

3. 安装成功后请在命令行中顺序执行如下指令将当前使用的普通用户添加到docker用户组内。   
    **sudo groupadd docker**   
    **sudo gpasswd -a ${USER} docker**   
    **sudo service docker restart**   
    **newgrp docker**   

    -   _用户名_：当前使用的普通用户用户名，如ascend。   
    > **注意：**     
    >
    > -   以上命令只需要执行一次，如果打开新的终端使用普通用户执行docker指令时还是报权限不足时，只要在此终端下执行**newgrp docker**命令即可。

## 第二步：配置镜像加速
**如果已经配置请跳过该步骤，这里提供了阿里云和华为云镜像加速，可以自行替换**

1. 命令行下顺序执行以下命令,使用Root用户创建/etc/docker/daemon.json文件。    
    **su root**   
    **vi /etc/docker/daemon.json**   

2. 编辑/etc/docker/daemon.json内容为：

    ```
    {
     "registry-mirrors": ["https://bem5fwjv.mirror.aliyuncs.com"]
    }
    ```

    修改完成后输入:wq!保存退出。   
    > **注意：**     
    >
    > -   如果安装较慢，可以体验华为的镜像加速。如下所示：
    >   ```
    >   {
    >    "registry-mirrors": ["https://050670bd850026be0f43c0086d8b54a0.mirror.swr.myhuaweicloud.com"]
    >   }
    >   ```

3. 执行如下命令，退出root用户，并重启docker。   
    **exit**    
    **sudo systemctl daemon-reload**   
    **sudo systemctl restart docker**

## 第三步：拉取docker镜像

命令行中执行如下命令拉取20.1版本开发环境docker镜像：   
**docker pull dopa6/ascenddev_20.1:atlas**

## 第四步：创建并配置docker环境

1. 查看容器ID。
    执行如下命令查看下载的镜像ID（即ascenddev_20.1:atlas的IMAGEID）。   
    **docker images**   

2. 创建并进入容器。
    执行如下命令创建容器，ImageID替换为查看到的镜像ID。   
    >   docker run -t -i --privileged --net=host -v /dev:/dev -v /tmp:/tmp -e DISPLAY=\\$DISPLAY [ImageID]    
    -   ImageID：需要运行的镜像ID。   
    -   --net=host： 表示使用主机的网络。   
    -   -v /dev:/dev：docker中挂载主机对应目录，也相当于共享文件夹。其余-v参数含义一致。   
    -   -e：传递环境变量，其余-e参数含义一致。   
    
    此指导中镜像image如上图为b481780952e4，则命令执行示例如下：   
    **docker run -t -i --privileged -v /dev:/dev -v /tmp:/tmp --net=host -e DISPLAY=\\$DISPLAY b481780952e4**   
    
    命令执行后即可进入容器。   
    > **说明：**     
    >
    > -   该命令只是在创建容器时运行，后续进入容器不需要使用此命令。

3. 配置虚拟网卡。
    此容器内的网络环境与外界宿主机(host)一样，可参考[官方配置文档](https://support.huaweicloud.com/dedg-A200dk_3000_c75/atlased_04_0015.html)配置宿主机网络与开发板联通。


## 常用操作

1. <a name="zh-cn_topic_2_2"></a>**换源操作**

    1. 命令行执行以下命令，备份原来的更新源。   
        **cp /etc/apt/sources.list /etc/apt/sources.list.backup**

    2. 修改更新源。　  
        打开sources.list (这就是存放更新源的文件)。   
        **gedit /etc/apt/sources.list**
        
        将下面所有内容复制，粘贴并覆盖sources.list文件中的所有内容，覆盖后保存。   
        ```
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
        deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
        ```

    3. 让更新源生效。   
        **sudo apt-get update**

2. **docker常用操作指令集**

    1. 如何查看镜像。   
        **docker images**

    2. 如何创建容器。   
        有了镜像以后，可通过docker run命令创建容器，在本应用场景下创建容器指令如下。   
        **docker run -t -i --privileged -v \\$HOME/.Xauthority:/root/.Xauthority --net=host -e DISPLAY=\\$DISPLAY  
   [ImageID]**

    3. 退出容器。   
        在容器中，使用exit指令退出容器，但是如果是docker run命令进入的容器，则退出后容器就会停止。
    
    4. 查看容器。   
        查看所有容器，包括已经停止的容器。   
        **docker ps -a**

        查看正在运行的容器。   
        **docker ps**

    5. 进入容器   
        - docker run 命令创建完容器，exit后，请用如下的方式进入。   
            命令行中使用如下指令查看刚才退出的容器ID。   
            **docker ps -a**

            执行如下指令启动容器，容器ID要替换为查到的CONTATNER_ID。   
            **docker start 容器ID**

            继续执行如下指令，进入容器，容器ID要替换为查到的CONTATNER_ID。   
            **docker exec -it 容器ID /bin/bash**

        - docker exec方式进入容器，exit后，容器并不会停止，下次进入仍然使用docker exec方式进入即可。   
            命令行中使用如下指令查看刚才退出的容器ID。   
            **docker ps -a**

            执行如下指令，进入容器，容器ID要替换为查到的CONTATNER_ID。   
            **docker exec -it 容器ID /bin/bash**

    6. 停止容器。   
        **docker stop 容器ID**

    7. 启动容器。   
        **docker start 容器ID**

    8. 删除容器。   
        需要在容器停止的时候才可以删除。   
        **docker rm 容器ID**

    9. 删除镜像。   
        需要在镜像创建的所有容器都停止的情况下才可以删除。   
        **docker rmi 镜像ID**
    
    10. 将主机中的数据拷贝到容器中。   
        **docker cp 主机文件路径 容器ID:/容器中存放数据的目录**
        
    11. 如何清理docker内存（谨慎使用）。   
        以下分别进行容器清理、镜像清理、volumes目录清理。   
        **docker ps --filter status=dead --filter status=exited -aq | xargs -r docker rm -v**    
        **docker images --no-trunc | grep '<none>' | awk '{ print $3 }' | xargs -r docker rmi**    
        **docker volume ls -f dangling=true | awk '{ print $2 }' | xargs docker volume rm**

## 参考资料

1. docker中文入门手册。   
    http://www.docker.org.cn/book/docker/what-is-docker-16.html

2. docker官方快速入门。   
    https://docs.docker.com/get-started/

3. 昇腾社区官网。   
    https://www.huaweicloud.com/ascend

4. 昇腾社区Atlas200DK板块论坛。   
    https://bbs.huaweicloud.com/forum/forum-949-1.html








