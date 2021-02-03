# for_20.2
**注意1：该脚本是将aicpu，pyacl，acllob从20.1升级20.2的工具脚本。需要先升级driver包后再使用该脚本升级。**
**注意2：该脚本仅限于20.1升级20.2使用！**

## 文件列表

- 加速模块包：Ascend-acllib-*-linux.aarch64.run，[点击跳转](https://www.huaweicloud.com/ascend/cann-download)
- 升级脚本：update_200dk_20.2.sh

## 制卡步骤

**制卡之前需要先将环境准备好**

1. 下载脚本及加速模块包。  

    开发环境中普通用户执行以下命令下载tools仓。   
    **cd $HOME**
    **git clone https://gitee.com/ascend/tools.git**    
	（注：如果没有安装git，执行sudo apt-get install git 安装git）   
    执行以下命令进入升级目录。    
    **cd tools/update_200dk/for20.2**    
    下载加速模块包，并上传到该目录下。
   
2. 将脚本和加速模块包上传到开发板上任意目录，如：/home/HwHiAiUser/update。   

    **scp update_200dk_20.2.sh HwHiAiUser@XXXX:/home/HwHiAiUser/update**    
    **scp Ascend-acllib-*-linux.aarch64.run HwHiAiUser@XXXX:/home/HwHiAiUser/update**    
    (注：XXXX代表开发板登录ip，请根据情况自行替换)

3. 登录开发板并进入升级文件夹。  

    **ssh HwHiAiUserr@XXXX**
    **cd /home/HwHiAiUser/update**    
    **su root**   
    (注：登录和root用户密码默认都为Mind@123)

4. 执行升级脚本  

	**bash update_200dk_20.2.sh**      