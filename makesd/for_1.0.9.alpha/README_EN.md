EN|[CH](README.md)

# for_1.0.9.alpha

## Supporting relationship

The business card requires the firmware and driver package and the community version cann_nnrt package, which have corresponding firmware and driver version numbers and CANN version numbers respectively.
The following table shows the matching table of **hardware version and CANN version**. Please select the corresponding CANN version package for card making according to the hardware version.

| Firmware and driver version | CANN version |
|---|---|
|  1.0.8.alpha |  3.1.0.alpha001 |
|  1.0.9.alpha |  3.2.0.alpha001/3.3.0.alpha001 |

## File List

- Entry script for SD card making: **make_sd_card.py**

- Entry script for SD card making: **make_ubuntu_sd.sh**

- Entry script for SD card making: **ubuntu-18.04.xxserver-arm64.iso**.[click jump](http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/)

- Entry script for SD card making: **A200dk-npu-driver-20.2.0-ubuntu18.04-aarch64-minirc.tar.gz**, **Ascend-cann-nnrt_xxx_linux-aarch64.run**.[click jump](https://www.huaweicloud.com/ascend/resource/Software)

## Procedure

**Before starting SD card making, prepare the environment as follows.**

1. Download the software packages required for SD card    
   -Download the driver package 
	**https://ascend.huawei.com/en/#/hardware/firmware-drivers**  
        ![输入图片说明](https://images.gitee.com/uploads/images/2021/0316/141137_996f972b_7985487.png "屏幕截图.png")  
   - Download the acceleration module package    
        **https://ascend.huawei.com/zh/#/software/cann/community**   (**3.2.0 in the history version/3.3.0, Take 3.2.0 as an example**)    
        ![输入图片说明](https://images.gitee.com/uploads/images/2021/0316/134749_e7061f53_7985487.png "屏幕截图.png")   


2. Download the SD card making script and ubuntu18.04-arm.iso。  
	Run the following command in the $HOME directory of a common user (for example, the ascend user) in the local environment to download code from the tools repository:  
	**git clone https://gitee.com/ascend/tools.git**  
	(If Git is not installed, run the sudo apt-get install git command to install it.)  

	Go to the C76 card making directory:  
	**cd $HOME/tools/makesd/for_1.0.9.alpha/**  
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
	HwHiAiUser@ubuntu:~$ cd tools/makesd/for_1.0.9.alpha/
	HwHiAiUser@ubuntu:~/tools/makesd/for_1.0.9.alpha$ ls
	make_sd_card.py  make_ubuntu_sd.sh  README.md README_EN.md
	```  
	Download the ubuntu18.04-arm.iso image:  
	**wget http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04.4-server-arm64.iso**  
	(The file size is 953 MB. It takes about 10 minutes to download the file.)  
	
	After the download is complete, grant 755 permission to the script and image:  
	**chmod 755 make_sd_card.py make_ubuntu_sd.sh ubuntu-18.04.4-server-arm64.iso**  
	
3. Save the downloaded card making package to the $HOME/tools/makesd/for_1.0.9.alpha directory of the common user.     
	```powershell  
	HwHiAiUser@ubuntu:~/tools/makesd/for_1.0.9.alpha$ ll
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
	HwHiAiUser@ubuntu:~/tools/makesd/for_1.0.9.alpha$ 
	```  
4. Connect the card reader inserted with an SD card to the Ubuntu server to make a bootable SD card.  

	Switch to the root user and prepare for card making:  
	**su - root**    
        **cd ${HOME}/tools/makesd/for_1.0.9.alpha/**

	Run the SD card making script:  
	**python3 make_sd_card.py local /dev/sdb**  
	(Note: /dev/sdb is the device name of the SD card. You can run the fdisk -l command as the root user to query the device name.)  

	Asking you whether to continue the installation, enter **Y**.  
	Wait for about 7 minutes. The message "Make SD Card successfully!" is displayed, indicating that the SD card has been made successfully.  
	
5. Power on the Atlas 200 DK.  
	Insert the SD card into the Atlas 200 DK, power on the Atlas 200 DK, and connect it to the Ubuntu server.  
	Note: During the upgrade of the Atlas 200 DK, two LED indicators blink. When the four LED indicators are on, the upgrade is successful. The upgrade takes about 5–10 minutes.  