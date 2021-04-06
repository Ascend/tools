### Atlas200DK上安装并使用3.3.0alpha001合设docker镜像

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

**6、文件准备**

| 软件包                                         | 说明                                        | 获取方法                                                     |
| ---------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| 	Ascend-cann-nnrt_3.3.0.alpha001_linux-aarch64.run | 离线推理引擎包。 | [获取链接](https://ascend.huawei.com/#/software/cann/community) |
| Dockerfile                                     | 制作镜像需要。                              | [获取链接](https://c7xcode.obs.cn-north-4.myhuaweicloud.com/3.3.0%20200dk%20docker/Dockerfile)                                         |
| Ascend-cann-toolkit_3.3.0.alpha001_linux-aarch64.run                            | 开发套件软件包                          | [获取链接](https://ascend.huawei.com/#/software/cann/community)   |
| A200dk-npu-driver-20.2.0-ubuntu18.04-aarch64-minirc.tar.gz                                   | 开发者板驱动包                          | [获取链接](https://ascend.huawei.com/#/hardware/firmware-drivers) |
| Python-3.7.5.tgz                                      |      python3.7.5安装包                                |   [获取链接](https://www.python.org/ftp/python/3.7.5/Python-3.7.5.tgz)  

**7、将准备的软件包和Dockerfile上传到Atlas200DK的同一目录（如“/home/HwHiAiUser/test”）**


**8、进入软件包所在目录，执行以下命令，构建容器镜像**

```
 docker build -t image-name --build-arg NNRT_PKG=Ascend-cann-nnrt_3.3.0.alpha001_linux-aarch64.run --build-arg  TOOLKIT_PKG=Ascend-cann-toolkit_3.3.0.alpha001_linux-aarch64.run . 
```

注意不要遗漏命令结尾的 **“.”** （执行docker bulid命令后需等待两个小时，因为dockerfile里面有安装opencv protobuf等，用户可根据自己要求增删）

当出现“Successfully built xxx”表示镜像构建成功。

**9、构建完成后，执行以下命令查看镜像信息**

**docker images**

显示示例：

```
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
atlas200dk      v1.0                1372d2961ed2        About an hour ago   12.3GB
```

**10、执行以下命令启动容器镜像（用户请根据实际情况修改）**

```
docker run -it --privileged --net=host --device=/dev/davinci0 --device=/dev/davinci_manager --device=/dev/svm0 --device=/dev/log_drv --device=/dev/event_sched --device=/dev/upgrade --device=/dev/hi_dvpp --device=/dev/memory_bandwidth --device=/dev/ts_aisle -v /var:/var -v /etc/hdcBasic.cfg:/etc/hdcBasic.cfg -v /etc/rc.local:/etc/rc.local -v /sys:/sys -v /usr/bin/sudo:/usr/bin/sudo -v /usr/lib/sudo/:/usr/lib/sudo/ -v /etc/sudoers:/etc/sudoers/  -v /usr/lib64:/usr/lib64 atlas200dk:v1.0 bash
```


**11、执行样例**

[快去跑一跑样例体验下吧~](https://gitee.com/ascend/samples/tree/master)

说明：容器内日志查看与日志级别设置方法同宿主机。



**附录：**

这里制作好了现成的，大家按照以上的方法安装了docker后，拉下来并用上方的启动容器镜像命令就可以用了。

```
docker pull swr.cn-north-4.myhuaweicloud.com/ascend-develop/atlas200dk-catenation:3.3.0.alpha001-full
```
**FAQ** ：
问题描述：在运行docker load 加载镜像时报错 dockerError processing tar file(exit status 1): no space left on device     
问题分析：造成以上报错的原因是因为docker加载镜像的空间不足了    
解决方法：   
修改 **docker root path**   
step 1: sudo docker info明确 Docker Root Dir: 为 **/var/lib/docker**   
step 2: 关闭 docker 服务 **sudo systemctl stop docker**    
step 3: 新建docker root 路径 **sudo mkdir /home/docker**    
step 4: 新建 docker 配置文件 **sudo touch /etc/docker/daemon.json**     
step 5: vim写入文件 **vim /etc/docker/daemon.json**     
step 6: 我的 docker 版本为 v19.03.2(docker版本可用docker --version查看)，在文件中加入json语句 **{"graph": "/home/docker"}** 问题得到了解决。网上解决办法还有当版本太低的时候，需要将上面的json语句替换为 **{"data-root": "/home/docker"}**     
step 7: 重启docker 服务 **sudo systemctl start docker** ，并 查看 **docker info** 的 **docker root dir** 是否变为指定的root路径 **/home/docker**    