# docker镜像使用指导

该使用指导将指导你拉取一个3.2.0.alpha001he 3.3.0.alpha001  atlas300的开发运行环境。环境内已经安装好了开发和运行环境，用户直接运行样例。    
 **docker容器中普通用户用户名：HwHiAiUser，密码：Mind@123     
            root用户用户名：root，密码：root**     
 ### 准备动作： 
1.需用户自行安装docker（版本要求大于等于18.03）。   
- 切换到root用户，更新源并安装docker，这里使用docker.io即可    
su - root   
apt-get update   
apt-get install docker.io   
- 创建docker用户组，应用用户加入docker组    
（1）创建docker用户组     
    sudo groupadd docker     
（2）应用用户加入docker用户组     
   sudo usermod -aG docker ${USER}     
（3）重启docker服务    
   sudo systemctl restart docker     
（4）切换或者退出当前账户再从新登入

  su root             切换到root用户    
  su ${USER}          再切换到原来的应用用户以上配置才生效    
（5）查看docker是否安装完成和docker版本    
    docker version   
 ![输入图片说明](https://images.gitee.com/uploads/images/2021/0326/112909_b5956577_7985487.png "屏幕截图.png")
  
    
2.宿主机需要安装驱动和固件，详情请参见[《CANN 软件安装指南 (开发&运行场景, 通过命令行方式)》](https://support.huaweicloud.com/instg-cli-cann330/atlasrun_03_0015.html)的“准备硬件环境”章节。     
  [驱动包下载](https://ascend.huawei.com/#/hardware/firmware-drivers)   
  ![输入图片说明](https://images.gitee.com/uploads/images/2021/0326/113114_05e5e3d4_7985487.png "屏幕截图.png")  
  解压A300-3010-npu_20.2.0_ubuntu18.04-x86_64.zip后得到
驱动安装包A300-3010-npu-driver_20.2.0_ubuntu18.04-x86_64.run和固件安装包A300-3000-3010-npu-firmware_1.76.22.3.220.run    
  [安装驱动包](https://support.huawei.com/enterprise/zh/doc/EDOC1100079287/65a1ae8d)    
  [安装固件包](https://support.huawei.com/enterprise/zh/doc/EDOC1100079287/7c53cdbb)

3.宿主机需要安装实用工具包toolbox，详情请参见[《CANN 软件安装指南 (开发&运行场景, 通过命令行方式)》](https://support.huaweicloud.com/instg-cli-cann202/atlasrun_03_0113.html)的“安装运行环境（推理）>在容器安装>在宿主机安装实用工具包”章节。    
  [toolbox下载地址](https://ascend.huawei.com/#/software/cann/commercial)    
  ![输入图片说明](https://images.gitee.com/uploads/images/2021/0326/113703_0d25732d_7985487.png "屏幕截图.png")   
  安装方法参考下方文档：   
https://support.huaweicloud.com/instg-cli-cann202/atlasrun_03_0101.html
### 直接拉取atlas300合设环境镜像
 命令行中执行如下命令拉取镜像：
  - 3.2.0.alpha001版本  
     **docker pull swr.cn-north-4.myhuaweicloud.com/ascend-develop/atlas300-catenation:3.2.0.alpha001**   
  - 3.3.0.alpha001版本  
     **docker pull swr.cn-north-4.myhuaweicloud.com/ascend-develop/atlas300-catenation:3.3.0.alpha001** 


### 配置合设环境

1. 用如下命令查看下载的镜像，可以看到你刚才下载的镜像ID.。

    **docker images**

2. 用如下命令创建容器，镜像ID替换为你查到的。
AscendDocker Runtime默认挂载的内容如[AscendDocker Runtime](https://support.huaweicloud.com/instg-container-image202/atlasdo_03_0027.html)默认挂载内容所示。命令示例如下（请根据实际情况修改）：   

  **docker run -it -e ASCEND_VISIBLE_DEVICES=xxx -v \\${install_path}/driver:${install_path}/driver -v /usr/local/dcmi:/usr/local/dcmi -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi image-name** 

其中${install_path}为驱动安装路径。  
![输入图片说明](https://images.gitee.com/uploads/images/2021/0318/152256_790a9ef8_7985487.png "屏幕截图.png")