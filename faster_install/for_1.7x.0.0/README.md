# faster install

## 说明
faster install，开发环境快速安装脚本。建议新建虚拟机运行该脚本。

## 使用步骤
1. 下载仓内的faster_install脚本到普通用户的家目录中，保持文件名为faster_install.sh。

2. 运行以下命令，执行脚本安装开发环境。

    **bash faster_install.bash**

    出现以下提示，请分别填写**Y**，下载相应软件包。
    
    [INFO] can not find mindstudio.tar.gz in /home/test,Do you want download[Y/N]: Y    
    [INFO] can not find Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run in /home/test, Do you want download[Y/N]: Y    
    [INFO] can not find Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run in /home/test, Do you want download[Y/N]: Y    
    
    完成后会自动下载软件包并安装相关依赖，由网络决定耗时，正常网络下约耗时40分钟。

    安装完成后会自动打开Mindstudio。
    ![Mindstudio](https://images.gitee.com/uploads/images/2020/0810/174052_91495667_5395865.png "屏幕截图.png")
    