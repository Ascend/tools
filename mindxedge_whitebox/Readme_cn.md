# MindXEdge 白牌化安装工具

## 功能
支持Atlas500智能小站的白牌化软件包的首次安装，安装后设备将变为白牌化的设备。注意：仅首次安装涉及，白牌升级场景无需调用。

## 使用环境
1. 用户环境为Atlas 500智能小站

2. 已安装Atlas 500智能小站升级包

3. Atlas500智能小站的升级包版本为21.0.4及以上版本（具体为2.0.4.6及以上的）


## 预置条件

1. 已下载与Atlas 500智能小站升级包配套的Ascend-mindxedge-whitebox_{version}_linux.zip白牌软件包


## 工具获取
###1. 说明：白牌化安装工具的目录为tools/mindxedge_whitebox，可以通过如下方法下载tools总包：

**方法1. 下载压缩包方式获取**

将 https://github.com/Ascend/tools 仓中的脚本下载至服务器（或下载到本地电脑）的任意目录。

例如存放路径为：$HOME/AscendProjects/tools。


**方法2. 命令行使用git命令方式获取**

在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

    git clone https://github.com/Ascend/tools.git

###2. 下载完成后，tools目录下的mindxedge_whitebox子目录即为存放白牌化安装工具的目录，相关目录结构关系如下：
```
       toolsg根目录：
           |--mindxedge_whitebox
                 |--README.md
                 |--install_whitebox.sh
                 |--load_install.sh
```
mindxedge_whitebox目录下的关键文件说明：

--load_install.sh：为执行白牌安装的入口脚本

--install_whitebox.sh：执行安装的依赖脚本

--README.md：为操作指导说明


## 使用方法

### 1. 制作mindxedge_whitebox.zip包（在本地电脑上执行）  
    a. 将Ascend-mindxedge-whitebox_{version}_linux.zip白牌软件包放在工具的mindxedge_whitebox子目录下
       即tools/mindxedge_whitebox目录
    b. 将mindxedge_whitebox目录压缩为mindxedge_whitebox.zip包


### 2. 将mindxedge_whitebox.zip包上传到Atlas 500小站的/tmp/目录下，并解压
    a. 进入tmp目录：cd /tmp
    b. 解压mindxedge_whitebox.zip包：unzip mindxedge_whitebox.zip
    c. 解压后，进入mindxedge_whitebox目录：cd mindxedge_whitebox


### 3. 执行白牌化安装操作
    在/tmp/mindxedge_whitebox目录下，执行安装命令: /bin/bash load_install.sh
    等待执行结束后，再进行下一步操作
    注：如果安装失败，可查看/var/plog/upgrade.log日志进行定位

    安装成功结束后，服务会自动重启，待服务启动完成登录web查看登录界面，此时web显示的信息仅包含用户白牌化信息而非华为设备商信息。

### 4. 安装结束后的处理
    安装结束后，需要手动删除/tmp目录下的mindxedge_whitebox.zip文件和mindxedge_whitebox目录及文件
    命令: rm -rf /tmp/mindxedge_whitebox.zip
    命令: rm -rf /tmp/mindxedge_whitebox
