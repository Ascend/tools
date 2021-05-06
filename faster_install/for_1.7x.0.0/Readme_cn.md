中文|[EN](Readme.md)

# 昇腾开发环境，适用于Atlas200DK，Atlas300
# 版本：目前可以安装20.0.0.RC1 （1.73） 20.1（1.75）
#### 介绍
该脚本适用于Ubuntu18.04操作系统，可以快速安装C7x的开发环境，包括Python环境与MindStudio。

#### 使用前准备
1、Ubuntu18.04 （x86）

2、快速安装脚本支持在线下载和本地读取python3.7.5的源码包、各个版本的开发套件包以及版本匹配的MindStudio安装包 进行快速安装这两种方式。

如果选择使用脚本中的在线下载功能，可以跳过本节。如果选择自行下载安装所需的包，可以将包放到**${HOME}/faster_install_packages**目录下，脚本会自动读取安装包并进行校验安装。

|                       |                    arm版本开发套件包                     |                 x86版本开发套件包                 |                      MindStudio安装包                       |                         Python 3.7.5                         |
| :-------------------: | :------------------------------------------------------: | :-----------------------------------------------: | :---------------------------------------------------------: | :----------------------------------------------------------: |
| **获取地址/安装命令** | https://ascend.huawei.com/zh/#/hardware/firmware-drivers | https://www.huaweicloud.com/ascend/cann-download  | https://ascend.huawei.com/zh/#/software/mindstudio/download | wget https://www.python.org/ftp/python/3.7.5/Python-3.7.5.tgz |
|     **20.0版本**      |     Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run     | Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run |                        2.0.0 (beta1)                        |                       Python-3.7.5.tgz                       |
|     **20.1版本**      |      Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run      |   Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run   |                        2.0.0 (beta2)                        |                       Python-3.7.5.tgz                       |

3、自行配置下载源。（可选，如果已经配置过源，请跳过，以下给出一种配置源的方法）

我们是在普通用户下安装的，首先确保当前环境中有一个普通用户和一个root用户，如果是新建的虚拟机需要先给root用户配置密码后才可以正常登录root用户（sudo passwd root）。以下安装普通用户以ascend举例  

&emsp;&emsp;（a）用户权限配置。

&emsp;&emsp;普通用户安装开发套件，需要有sudo权限，所以首先需要给普通用户配置权限。  
&emsp;&emsp;切换为root用户。  
&emsp;&emsp;**su root**   
&emsp;&emsp;给sudoer文件配置写权限，并打开该文件。  
&emsp;&emsp;**chmod u+w /etc/sudoers**   
&emsp;&emsp;**vi /etc/sudoers**   

&emsp;&emsp;在该文件“ # User privilege specification”下面增加如下内容：

&emsp;&emsp;![输入图片说明](https://images.gitee.com/uploads/images/2020/1121/171509_8e9cf604_5408865.png "屏幕截图.png")    

&emsp;&emsp;其中，ascend为开发环境种普通用户用户名，需要根据自己的环境修改。

&emsp;&emsp;完成后，执行以下命令取消“ /etc/sudoers”文件的写权限。

&emsp;&emsp;**chmod u-w /etc/sudoers** 


&emsp;&emsp;（b）源配置。

&emsp;&emsp;由于安装过程中涉及很多apt依赖的安装，所以配置一个国内源是一个加快进度的好办法。  
&emsp;&emsp;配置ubuntu18.04-x86的apt清华源。  

&emsp;&emsp;root用户下打开apt源文件。  

&emsp;&emsp;**vi /etc/apt/sources.list** 

&emsp;&emsp;将源文件内容替换为以下ubuntu18.04-x86的apt清华源。

```bash
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
```
&emsp;&emsp;执行以下命令更新源。

&emsp;&emsp;**apt-get update** 

> 如果apt-get update失败，可以试用其他的国内源 https://www.cnblogs.com/dream4567/p/9690850.html


#### 使用方法
1、下载快速安装脚本。Ubuntu服务器的命令行中执行以下命令进入$HOME目录。

**cd $HOME** 

命令行中使用以下命令下载faster-install脚本。

**git clone https://github.com/Ascend/tools.git** 

将faster-install目录下的faster_install.sh脚本拷贝到$HOME目录下。

**cp ~/tools/faster_install/for_1.7x.0.0/faster_install.sh  .**

执行脚本。

 **bash faster_install.sh** 

2、安装完成之后会显示以下界面。选择下图中红框选项（第三行）并点击OK。

![](img/pic7.png "界面1")

3、点击界面中的红色框内的选项。

![](img/pic5.png "界面2")

4、选择下图中的选项，点OK即可, 下图中以20.0 为例举例说明

![](img/pic6.png "界面3")

