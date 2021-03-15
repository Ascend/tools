中文|[英文](README_EN.md)

# for_3.0.0

**本文档只提供读卡器制卡方式指导，更多详细指导可以参考[官方制卡文档](https://support.huaweicloud.com/usermanual-A200dk_3000/atlas200dk_02_0010.html)**

## 文件列表

- 制卡入口脚本：make_sd_card.py

- 制作SD卡操作系统脚本：make_ubuntu_sd.sh

- 开发者板操作系统镜像包：ubuntu-18.04.xxserver-arm64.iso，[点击跳转](http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/)

- 固件与驱动包：Ascend310-driver-xxx-ubuntu18.04.aarch64-minirc.tar.gz、Ascend310-aicpu_kernels-xxx-minirc.tar.gz、Ascend-acllib-xxx-ubuntu18.04.aarch64-minirc.run，[点击跳转](https://www.huaweicloud.com/ascend/resource/Software)

## 制卡步骤

**制卡之前需要先将环境准备好**

1. 如下图下载制卡需要的软件包  
	下载地址：**https://www.huaweicloud.com/ascend/resource/Software**  
	![](https://images.gitee.com/uploads/images/2020/1205/162945_e7c3bea4_5400693.png "package.png")

2. 下载制卡脚本和ubuntu18.04-arm.iso。  
	在本地环境普通用户（以ascend用户为例）的$HOME目录下执行以下命令，下载tools仓代码。  
	**git clone https://gitee.com/ascend/tools.git**  
	（注：如果没有安装git，执行sudo apt-get install git 安装git）  

	执行以下命令，进入3.0.0制卡目录。  
	**cd $HOME/tools/makesd/for_3.0.0/**  
	```powershell  
	ascend@ubuntu:~$ git clone https://gitee.com/ascend/tools.git
	Cloning into 'tools'...
	remote: Enumerating objects: 273, done.
	remote: Counting objects: 100% (273/273), done.
	remote: Compressing objects: 100% (263/263), done.
	remote: Total 273 (delta 128), reused 0 (delta 0), pack-reused 0
	Receiving objects: 100% (273/273), 533.57 KiB | 877.00 KiB/s, done.
	Resolving deltas: 100% (128/128), done.
	ascend@ubuntu:~$ cd tools/
	amexec/  .git/    img2bin/ makesd/  
	ascend@ubuntu:~$ cd tools/makesd/for_3.0.0/
	ascend@ubuntu:~/tools/makesd/for_3.0.0$ ls
	make_sd_card.py  make_ubuntu_sd.sh  README.md
	```  
	执行以下命令下载ubuntu18.04-arm.iso镜像。  
	**wget http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04.4-server-arm64.iso**  
	（文件大小为953M，下载约要10min）  
	
	下载完成后，执行以下命令，给脚本和iso镜像加权限。  
	**chmod 755 make_sd_card.py make_ubuntu_sd.sh ubuntu-18.04.4-server-arm64.iso**  
	
3. 将之前下载的制卡所需包放置到该目录（普通用户的 $HOME/tools/makesd/for_3.0.0）下。  
	```powershell  
	ascend@ubuntu:~/tools/makesd/for_3.0.0$ ll
	total 80920
	drwxr-xr-x 2 ascend ascend     4096 Jul 28 04:33 ./
	drwxr-xr-x 4 ascend ascend     4096 Jul 28 04:23 ../
	-rw-r--r-- 1 ascend ascend   173441 Jul 28 04:32 Ascend310-aicpu_kernels-1.73.5.1.b050-minirc.tar.gz
	-rw-r--r-- 1 ascend ascend 79395214 Jul 28 04:32 Ascend310-driver-1.73.5.1.b050-ubuntu18.04.aarch64-minirc.tar.gz
	-rw-r--r-- 1 ascend ascend  4457767 Jul 28 04:33 Ascend-acllib-1.73.5.1.b050-ubuntu18.04.aarch64-minirc.run
	-rwxr-xr-x 1 ascend ascend    17633 Jul 28 04:23 make_sd_card.py*
	-rwxr-xr-x 1 ascend ascend    23797 Jul 28 04:23 make_ubuntu_sd.sh*
	-rw-r--r-- 1 ascend ascend      438 Jul 28 04:23 README.md
	-rwxr-xr-x 1 ascend ascend 82800726 Jul 28 04:27 ubuntu-18.04.4-server-arm64.iso*
	ascend@ubuntu:~/tools/makesd/for_3.0.0$ 
	```  

4. 将插有SD卡的读卡器连接Ubuntu服务器，制作SD卡：  

	执行以下命令，切换root用户，准备制卡。  
	**su - root**    
        **cd ${HOME}/tools/makesd/for_3.0.0/**

	执行以下命令，执行脚本准备制卡  
	**python3 make_sd_card.py local /dev/sdb**  
	（说明：/dev/sdb 是SD卡的设备名，可以在root用户下执行fdisk -l查看。）  
	![mksd2](https://images.gitee.com/uploads/images/2020/0729/140246_f7c541a0_5395865.png)  
	如图，制卡过程中，提示是否继续安装，输入**Y**。  
	等待约7min，提示**Make SD Card successfully!**,则制卡成功。  
	
5. 上电Atlas 200DK开发板。  
	将制好的卡放入Atlas 200DK开发板，上电后连接Ubuntu服务器。  
	**注：开发板升级过程中会有两个灯闪烁，当四个灯常亮时即为升级成功，升级过程约5-10min**  