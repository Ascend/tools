EN|[CH](./README.md)

# for_1.3x.0.0

## File List

- Entry script for SD card making: make_sd_card.py

- Script for making a bootable SD card: make_ubuntu_sd.sh

- OS image of the Atlas 200 DK: ubuntu-16.04.xx-server-arm64.iso,[click jump](http://cdimage.ubuntu.com/ubuntu/releases/16.04/release/)

- Runtime package of the Atlas 200 DK: mini_developerkit-xxx.rar,[click jump](https://www.huaweicloud.com/ascend/resources/ResourceDownload/DE51187AC4F0F5DBAB3A468952C95CADAC6308BFFFB5D064B9A30DBD2B73B4ABCEC6BAF7F594AE3C3FA89621AFFF3E3CFB4ED973618F8857D07706003D546332/DDK%20&%20Runtime/be3564c84a0546959b6439ebc4e8ae30/2/1/1)

## Procedure

**Before starting SD card making, prepare the environment as follows.**

1. For details about how to download the software packages required for card making, see the "File List."     
	![download_deverlopkit](https://images.gitee.com/uploads/images/2020/0729/141200_ebfaba44_5395865.png "屏幕截图.png")

2. Download the SD card making script and ubuntu16.04.3-arm.iso.    
	Run the following command in the $HOME directory of a common user (for example, the ascend user) in the local environment to download code from the tools repository:   
	**git clone https://gitee.com/ascend/tools.git**   
	(If Git is not installed, run the sudo apt-get install git command to install it.)    

	Go to the C32 card making directory:  
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
	Download the ubuntu16.04.3-arm.iso image:  
	**wget http://old-releases.ubuntu.com/releases/16.04.3/ubuntu-16.04.3-server-arm64.iso**  
	(The file size is 744 MB. It takes about 8 minutes to download the file.)  
	
	After the download is complete, grant 755 permission to the script and image:  
	**chmod 755 make_sd_card.py make_ubuntu_sd.sh ubuntu-16.04.3-server-arm64.iso**  
	
3. Save the downloaded card making package to the $HOME/tools/makesd/for_1.3x.0.0 directory of the common user.  
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

4. Connect the card reader inserted with an SD card to the Ubuntu server to make a bootable SD card  

	Switch to the root user and prepare for card making:  
	**su - root**    
        **cd ${HOME}/tools/makesd/for_1.3x.0.0/**

	Run the SD card making script:   
	**python3 make_sd_card.py local /dev/sdb**   
	(Note: /dev/sdb is the device name of the SD card. You can run the fdisk -l command as the root user to query the device name.)   
	![mksd2](https://images.gitee.com/uploads/images/2020/0729/140246_f7c541a0_5395865.png)  
	When a message is displayed, asking you whether to continue the installation, enter **Y**.  
	Wait for about 7 minutes. The message "Make SD Card successfully!" is displayed, indicating that the SD card has been made successfully.  
	
5. Power on the Atlas 200 DK.  
	Insert the SD card into the Atlas 200 DK, power on the Atlas 200 DK, and connect it to the Ubuntu server.  
	**Note: During the upgrade of the Atlas 200 DK, two LED indicators blink. When the four LED indicators are on, the upgrade is successful. The upgrade takes about 5–10 minutes.**  