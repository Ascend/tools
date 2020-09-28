中文|[EN](README_EN.md)

# 昇腾开发环境，适用于Atlas200DK，Atlas300

#### 介绍
该脚本适用于Ubuntu18.04操作系统，可以快速安装C7x的开发环境，包括Python环境与MindStudio。

#### 使用前准备
1、Ubuntu18.04 （x86）

2、到网站（https://www.huaweicloud.com/ascend/resource/Software ）下载用于安装MindStudio的Toolkit包，名字为Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run、Ascend-Toolkit-[version]-arm-linux_gcc7.3.0.run，将两个包放于$HOME目录下。

由于有些样例（指一些需要用到摄像头的样例）需要用到以下包：Ascend310-driver-[version]-ubuntu18.04.aarch64-minirc.tar.gz，故也可以下载下来并自行解压即可（在上面的网站链接中即可下载）。

3、自行配置下载源。（可选，如果已经配置过源，请跳过，以下给出一种配置源的方法）

（1）点击左边如下图“步骤1”中的图标。
![](img/pic1.png "步骤1")

（2）点击图“步骤2”中上方红色框图标。
![](img/pic2.png "步骤1")

（3）勾选图“步骤3”中的第5个选项，并选择other选项。
![](img/pic3.png "步骤1")

（4）如图选择你所需要的源。
![](img/pic4.png "步骤1")

#### 使用方法
1、下载快速安装脚本。Ubuntu服务器的命令行中执行以下命令进入$HOME目录。

**cd $HOME** 

命令行中使用以下命令下载faster-install脚本。

**git clone https://gitee.com/ascend/tools.git** 

将faster-install目录下的faster_install.sh脚本拷贝到$HOME目录下。

**cp ~/tools/faster_install/for_1.7x.0.0/faster_install.sh  .**

执行脚本。

 **bash faster-install.sh** 

2、安装完成之后会显示以下界面。选择下图中红框选项（第三行）并点击OK。

![](img/pic7.png "界面1")

3、点击界面中的红色框内的选项。

![](img/pic5.png "界面2")

4、选择下图中的选项，点OK即可。

![](img/pic6.png "界面3")

5、此时会自动关闭MindStudio，重新启动MindStudio即可。到此C7x开发环境安装完成。