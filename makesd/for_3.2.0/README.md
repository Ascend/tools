中文|[英文](README_EN.md)

# for_3.2.0

## 文件列表

- 制卡入口脚本：make_sd_card.py

- 制作SD卡操作系统脚本：make_ubuntu_sd.sh

- 开发者板操作系统镜像包：ubuntu-18.04.xxserver-arm64.iso，[点击跳转](http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/)

- 固件与驱动包：A200dk-npu-driver-20.2.0-ubuntu18.04-aarch64-minirc.tar.gz，[点击跳转](https://ascend.huawei.com/#/hardware/firmware-drivers)

- 加速模块包：Ascend-cann-nnrt_xxx_linux-aarch64.run，[点击跳转](https://ascend.huawei.com/#/software/cann/community)


## 制卡步骤

**制卡之前需要先将环境准备好**

1. 如下图下载制卡需要的软件包  
    - 下载驱动包。   
	下载地址：**https://ascend.huawei.com/#/hardware/firmware-drivers**   
	![输入图片说明](https://images.gitee.com/uploads/images/2021/0316/115015_adf679f7_7985487.png "屏幕截图.png") 
    - 下载加速模块包。    
        下载地址：**https://ascend.huawei.com/#/software/cann/community**（历史版本中的3.2.0.alpha001）      
        ![输入图片说明](https://images.gitee.com/uploads/images/2021/0316/134749_e7061f53_7985487.png "屏幕截图.png")  
2. 下载制卡脚本和ubuntu18.04-arm.iso。  
	在本地环境普通用户（以HwHiAiUser用户为例）的$HOME目录下执行以下命令，下载tools仓代码。  
	**git clone https://gitee.com/ascend/tools.git**  
	（注：如果没有安装git，执行sudo apt-get install git 安装git）  

	执行以下命令，进入3.2.0制卡目录。  
	**cd $HOME/tools/makesd/for_3.2.0/**  
	```powershell  
	HwHiAiUser@ubuntu:~$ git clone https://gitee.com/ascend/tools.git
        Cloning into 'tools'...
        remote: Enumerating objects: 327, done.
        remote: Counting objects: 100% (327/327), done.
        remote: Compressing objects: 100% (47/47), done.
        remote: Total 3938 (delta 293), reused 291 (delta 276), pack-reused 3611
        Receiving objects: 100% (3938/3938), 56.64 MiB | 1.64 MiB/s, done.
        Resolving deltas: 100% (1691/1691), done.
        Checking connectivity... done.
        Checking out files: 100% (590/590), done.
	HwHiAiUser@ubuntu:~$ cd tools/makesd/for_3.2.0/
	HwHiAiUser@ubuntu:~/tools/makesd/for_3.2.0$ ls
	make_sd_card.py  make_ubuntu_sd.sh  README.md README_EN.md
	```  
	执行以下命令下载ubuntu18.04-arm.iso镜像。  
	**wget http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04.4-server-arm64.iso**  
	（文件大小为953M，下载约要10min）  
	
	下载完成后，执行以下命令，给脚本和iso镜像加权限。  
	**chmod 755 make_sd_card.py make_ubuntu_sd.sh ubuntu-18.04.4-server-arm64.iso**  
	
3. 将之前下载的制卡所需包放置到该目录（普通用户的 $HOME/tools/makesd/for_3.2.0）下。  
	```powershell  
	HwHiAiUser@ubuntu:~/tools/makesd/for_3.2.0$ ll
	total 80920
	drwxr-xr-x 2 HwHiAiUser HwHiAiUser     4096 Jul 28 04:33 ./
	drwxr-xr-x 4 HwHiAiUser HwHiAiUser     4096 Jul 28 04:23 ../
	-rw-r--r-- 1 HwHiAiUser HwHiAiUser 51804744 Jul 28 04:32 A200dk-npu-driver-20.2.0-ubuntu18.04-aarch64-minirc.tar.gz
	-rw-r--r-- 1 HwHiAiUser HwHiAiUser 100064987 Jul 28 04:33 Ascend-cann-nnrt_20.2.alpha001_linux-aarch64.run
	-rwxr-xr-x 1 HwHiAiUser HwHiAiUser    17633 Jul 28 04:23 make_sd_card.py*
	-rwxr-xr-x 1 HwHiAiUser HwHiAiUser    23797 Jul 28 04:23 make_ubuntu_sd.sh*
	-rw-r--r-- 1 HwHiAiUser HwHiAiUser      438 Jul 28 04:23 README.md
        -rw-r--r-- 1 HwHiAiUser HwHiAiUser      438 Jul 28 04:23 README_EN.md
	-rwxr-xr-x 1 HwHiAiUser HwHiAiUser 82800726 Jul 28 04:27 ubuntu-18.04.4-server-arm64.iso*
	HwHiAiUser@ubuntu:~/tools/makesd/for_3.2.0$ 
	```  

4. 将插有SD卡的读卡器连接Ubuntu服务器，制作SD卡：  

	执行以下命令，切换root用户，准备制卡。  
	**su - root**    
        **cd ${HOME}/tools/makesd/for_3.2.0/**

	执行以下命令，执行脚本准备制卡  
	**python3 make_sd_card.py local /dev/sdb**  
	（说明：/dev/sdb 是SD卡的设备名，可以在root用户下执行fdisk -l查看。）  
	![输入图片说明](https://images.gitee.com/uploads/images/2021/0316/134724_dd47fe7a_7985487.png "屏幕截图.png")
	如图，制卡过程中，提示是否继续安装，输入**Y**。  
	等待约7min，提示**Make SD Card successfully!**,则制卡成功。  
	
5. 上电Atlas 200DK开发板。  
	将制好的卡放入Atlas 200DK开发板，上电后连接Ubuntu服务器。  
	**注：开发板升级过程中会有两个灯闪烁，当四个灯常亮时即为升级成功，升级过程约5-10min**  