### 华为云Ai1S开发&运行环境一键部署脚本

#### 适用版本
Driver：21.0.1

CANN：5.0.2_alpha005

MindStudio： 3.0.2

#### 使用方式
- 以root用户登陆到新创建好的Ai1S环境中
- 在/home/HwHiAiUser目录下任意创建一个文件夹(命名举例：package)
- 把auto_deply.sh脚本下载到这个文件夹"package"内
- cd /home/HwHiAiUser/package
- bash auto_deploy.sh

脚本执行完后会自动重启，重启后可自行修改HwHiAiUser用户的密码，然后以HwHiAiUser用户登陆到环境上,
cd /home/HwHiAiUser/package/MindStudio/bin
./MindStudio.sh
即可启动MindStudio开发工具。