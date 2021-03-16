# update_200dk
**注意：该脚本是将aicpu，pyacl，acllib从3.1.0及以上版本升级至3.2.0及以上版本的工具脚本。**   

## 文件列表

- 加速模块包：Ascend-cann-nnrt*_linux.aarch64.run，[点击跳转](https://www.huaweicloud.com/ascend/cann-download)
- 升级脚本：update_200dk.sh

## 制卡步骤

**制卡之前需要先将环境准备好**

1. 下载脚本及加速模块包。  
 
    开发环境中普通用户执行以下命令下载tools仓。    
    **cd $HOME**     
    **git clone https://gitee.com/ascend/tools.git**    
    （注：如果没有安装git，执行sudo apt-get install git 安装git）   
    执行以下命令进入升级目录。    
    **cd tools/update_200dk**    
    下载加速模块包，并上传到该目录下。  
   
2. 将脚本和加速模块包上传到开发板上任意目录，如：/home/HwHiAiUser/update。   

    **scp update_200dk.sh HwHiAiUser@XXXX:/home/HwHiAiUser/update**    
    **scp Ascend-acllib-*-linux.aarch64.run HwHiAiUser@XXXX:/home/HwHiAiUser/update**    
    (注：XXXX代表开发板登录ip，请根据情况自行替换)

3. 登录开发板并进入升级文件夹。  

    **ssh HwHiAiUser@XXXX**    
    **cd /home/HwHiAiUser/update**    
    **su root**   
    (注：登录和root用户密码默认都为Mind@123)     

4. 执行升级脚本  

	**bash update_200dk.sh**      