EN|[CH](README.md)

# for_1.7x.0.0

## File List

- Entry script for SD card making: **make_sd_card.py**

- Entry script for SD card making: **make_ubuntu_sd.sh**

- Entry script for SD card making: **ubuntu-18.04.xxserver-arm64.iso**.[click jump](http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/)

- Entry script for SD card making: **Ascend310-firmware-xxx-minirc.run**, **Ascend310-aicpu_kernels-xxx-minirc.tar.gz**, **Ascend-acllib-xxx-ubuntu18.04.aarch64-minirc.run**.[click jump](https://www.huaweicloud.com/ascend/resource/Software)

## Procedure

**Before starting SD card making, prepare the environment as follows.**

1. Download the software packages required for SD card making from  
	**https://www.huaweicloud.com/intl/en-us/ascend/resource/Software**  
        ![下载制卡包](https://images.gitee.com/uploads/images/2020/0810/100322_a78ef230_5395865.png "屏幕截图.png")

2. Download the SD card making script and ubuntu18.04-arm.iso。  
	Run the following command in the $HOME directory of a common user (for example, the ascend user) in the local environment to download code from the tools repository:  
	**git clone https://gitee.com/ascend/tools.git**  
	(If Git is not installed, run the sudo apt-get install git command to install it.)  

	Go to the C73 card making directory:  
	**cd $HOME/tools/makesd/for_1.7x.0.0/**  
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
	ascend@ubuntu:~$ cd tools/makesd/for_1.7x.0.0/
	ascend@ubuntu:~/tools/makesd/for_1.7x.0.0$ ls
	make_sd_card.py  make_ubuntu_sd.sh  README.md
	ascend@ubuntu:~/tools/makesd/for_1.7x.0.0$ ^C
	ascend@ubuntu:~/tools/makesd/for_1.7x.0.0$ 
	```  
	Download the ubuntu18.04-arm.iso image:  
	**wget http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04.4-server-arm64.iso**  
	(The file size is 953 MB. It takes about 10 minutes to download the file.)  
	
	After the download is complete, grant 755 permission to the script and image:  
	**chmod 755 make_sd_card.py make_ubuntu_sd.sh ubuntu-18.04.4-server-arm64.iso**  
	
3. Save the downloaded card making package to the $HOME/tools/makesd/for_1.7x.0.0 directory of the common user.  
	```powershell  
	ascend@ubuntu:~/tools/makesd/for_1.7x.0.0$ ll
	total 80920
	drwxr-xr-x 2 ascend ascend     4096 Jul 28 04:33 ./
	drwxr-xr-x 4 ascend ascend     4096 Jul 28 04:23 ../
	-rw-r--r-- 1 ascend ascend   173441 Jul 28 04:32 Ascend310-aicpu_kernels-1.73.5.1.b050-minirc.tar.gz
	-rw-r--r-- 1 ascend ascend   449942 Jul 28 04:32 Ascend310-firmware-1.73.5.1.b050-minirc.run
	-rw-r--r-- 1 ascend ascend  4457767 Jul 28 04:33 Ascend-acllib-1.73.5.1.b050-ubuntu18.04.aarch64-minirc.run
	-rwxr-xr-x 1 ascend ascend    17633 Jul 28 04:23 make_sd_card.py*
	-rwxr-xr-x 1 ascend ascend    23797 Jul 28 04:23 make_ubuntu_sd.sh*
	-rw-r--r-- 1 ascend ascend      438 Jul 28 04:23 README.md
	-rwxr-xr-x 1 ascend ascend 82800726 Jul 28 04:27 ubuntu-18.04.4-server-arm64.iso*
	ascend@ubuntu:~/tools/makesd/for_1.7x.0.0$ 
	```  

4. Save the downloaded card making package to the $HOME/tools/makesd/for_1.7x.0.0 directory of the common user.  

	Switch to the root user and prepare for card making:  
	**su root**

	Switch to the root user and prepare for card making:  
	**python3 make_sd_card.py local /dev/sdb**  
	(Note: /dev/sdb is the device name of the SD card. You can run the fdisk -l command as the root user to query the device name.)  
	![mksd2](https://images.gitee.com/uploads/images/2020/0729/140246_f7c541a0_5395865.png)  
	When a message is displayed, asking you whether to continue the installation, enter **Y**.  
	Wait for about 7 minutes. The message "Make SD Card successfully!" is displayed, indicating that the SD card has been made successfully.  
	
5. Power on the Atlas 200 DK.  
	Insert the SD card into the Atlas 200 DK, power on the Atlas 200 DK, and connect it to the Ubuntu server.  
	Note: During the upgrade of the Atlas 200 DK, two LED indicators blink. When the four LED indicators are on, the upgrade is successful. The upgrade takes about 5–10 minutes.  