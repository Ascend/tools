中文|[英文](README_EN.md)

# for_1.3x.0.0

## 文件列表

- 制卡入口脚本：make_sd_card.py

- 制作SD卡操作系统脚本：make_ubuntu_sd.sh

- 开发者板操作系统镜像包：ubuntu-16.04.xx-server-arm64.iso，[点击跳转](http://cdimage.ubuntu.com/ubuntu/releases/16.04/release/)

- 开发者板系统运行包：mini_developerkit-xxx.rar，[点击跳转](https://www.huaweicloud.com/ascend/resources/ResourceDownload/DE51187AC4F0F5DBAB3A468952C95CADAC6308BFFFB5D064B9A30DBD2B73B4ABCEC6BAF7F594AE3C3FA89621AFFF3E3CFB4ED973618F8857D07706003D546332/DDK%20&%20Runtime/be3564c84a0546959b6439ebc4e8ae30/2/1/1)

## 制卡步骤

**制卡之前需要先将环境准备好**

1. 如下图下载制卡需要的软件包  
	下载地址参见文件列表。 
	![download_deverlopkit](https://images.gitee.com/uploads/images/2020/0729/141200_ebfaba44_5395865.png "屏幕截图.png")

2. 下载制卡脚本和ubuntu16.04.3-arm.iso。  
	在本地环境普通用户（以ascend用户为例）的$HOME目录下执行以下命令，下载tools仓代码。  
	**git clone https://gitee.com/ascend/tools.git**  
	（注：如果没有安装git，执行sudo apt-get install git 安装git）  

	执行以下命令，进入C32制卡目录。  
	**cd $HOME/tools/makesd/for_1.3x.0.0/**  
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
	ascend@ubuntu:~$ cd tools/makesd/for_1.3x.0.0/
	ascend@ubuntu:~/tools/makesd/for_1.3x.0.0$ ls
	make_sd_card.py  make_ubuntu_sd.sh  README.md
	ascend@ubuntu:~/tools/makesd/for_1.3x.0.0$ ^C
	ascend@ubuntu:~/tools/makesd/for_1.3x.0.0$ 
	```  
	执行以下命令下载ubuntu16.04.3-arm.iso镜像。  
	**wget http://old-releases.ubuntu.com/releases/16.04.3/ubuntu-16.04.3-server-arm64.iso**  
	（文件大小为744M，下载约要8min）  
	
	下载完成后，执行以下命令，给脚本和iso镜像加权限。  
	**chmod 755 make_sd_card.py make_ubuntu_sd.sh ubuntu-16.04.3-server-arm64.iso**  
	
3. 将之前下载的制卡所需包放置到该目录（普通用户的 $HOME/tools/makesd/for_1.3x.0.0）下。  
	```powershell  
	ascend@ubuntu:~/tools/makesd/for_1.3x.0.0$ ll
	total 80920
	drwxr-xr-x 2 ascend ascend     4096 Jul 28 04:33 ./
	drwxr-xr-x 4 ascend ascend     4096 Jul 28 04:23 ../
	-rw-r--r-- 1 ascend ascend 74438310 Jul 28 04:32 mini_developerkit_1.32.0.B080.rar
	-rwxr-xr-x 1 ascend ascend    17633 Jul 28 04:23 make_sd_card.py*
	-rwxr-xr-x 1 ascend ascend    23797 Jul 28 04:23 make_ubuntu_sd.sh*
	-rw-r--r-- 1 ascend ascend      438 Jul 28 04:23 README.md
	-rwxr-xr-x 1 ascend ascend 82800726 Jul 28 04:27 ubuntu-16.04.3-server-arm64.iso*
	ascend@ubuntu:~/tools/makesd/for_1.3x.0.0$ 
	```  

4. 将插有SD卡的读卡器连接Ubuntu服务器，制作SD卡：  

	执行以下命令，切换root用户，准备制卡。  
	**su - root**    
        **cd ${HOME}/tools/makesd/for_1.3x.0.0/** 

	执行以下命令，执行脚本准备制卡  
	**python3 make_sd_card.py local /dev/sdb**  
	（说明：/dev/sdb 是SD卡的设备名，可以在root用户下执行fdisk -l查看。）  
	![mksd2](https://images.gitee.com/uploads/images/2020/0729/140246_f7c541a0_5395865.png)  
	如图，制卡过程中，提示是否继续安装，输入**Y**。  
	等待约7min，提示**Make SD Card successfully!**,则制卡成功。  
	
5. 上电Atlas 200DK开发板。  
	将制好的卡放入Atlas 200DK开发板，上电后连接Ubuntu服务器。  
	**注：开发板升级过程中会有两个灯闪烁，当四个灯常亮时即为升级成功，升级过程约5-10min**  