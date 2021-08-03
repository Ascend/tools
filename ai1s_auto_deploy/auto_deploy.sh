# 1.下载驱动、固件、toolkit包、mindstudio包
# 2.安装依赖
# 3.安装新驱动
# 4.安装toolkit，Mindstudio，配置好bashrc，重启

driver_addr='https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/turing/resourcecenter/Software/AtlasI/A300-3010 1.0.10/A300-3010-npu-driver_21.0.1_ubuntu18.04-x86_64.run'
toolkit_addr='https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/5.0.2.alpha005/Ascend-cann-toolkit_5.0.2.alpha005_linux-x86_64.run'
mindstudio_addr='https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/MindStudio/MindStudio%203.0.2/MindStudio_3.0.2_linux.tar.gz'


script_path="$( cd "$(dirname $BASH_SOURCE)" ; pwd -P)"
cd ${script_path}



function download_software_package()
{
	wget "${driver_addr}" --no-check-certificate
	wget "${toolkit_addr}" --no-check-certificate
	wget "${mindstudio_addr}" --no-check-certificate
}

function change_apt_source()
{
tsinghua_source='deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse'

echo "${tsinghua_source}" > /etc/apt/sources.list

apt-get update
}

function change_pip_source()
{
tsinghua_pip_source='[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = https://pypi.tuna.tsinghua.edu.cn'

mkdir -p /home/HwHiAiUser/.pip
touch /home/HwHiAiUser/.pip/pip.conf
echo "${tsinghua_pip_source}" > /home/HwHiAiUser/.pip/pip.conf

chown -R HwHiAiUser:HwHiAiUser /home/HwHiAiUser/.pip
}


function install_dependencies()
{
change_apt_source

apt-get install -y gcc g++ make cmake zlib1g zlib1g-dev openssl libsqlite3-dev libssl-dev libffi-dev unzip pciutils net-tools libblas-dev gfortran libblas3 libopenblas-dev libncursesw5-dev

apt-get install -y openjdk-11-jdk

apt-get -y install xterm firefox xdg-utils fonts-droid-fallback fonts-wqy-zenhei fonts-wqy-microhei fonts-arphic-ukai fonts-arphic-uming gnome-keyring

change_pip_source
su - HwHiAiUser -c "pip3.7 install attrs numpy==1.17.2 decorator sympy cffi pyyaml pathlib2 psutil protobuf scipy requests --user"

su - HwHiAiUser -c "/usr/local/python3.7.5/bin/pip3 install --user  coverage gnureadline pylint matplotlib pandas xlrd absl-py"

#用于设置python3.7.5库文件路径
echo "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH" >> /home/HwHiAiUser/.bashrc
#如果用户环境存在多个python3版本，则指定使用python3.7.5版本
echo "export PATH=/usr/local/python3.7.5/bin:$PATH" >> /home/HwHiAiUser/.bashrc

echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /home/HwHiAiUser/.bashrc
echo "export PATH=$JAVA_HOME/bin:$PATH" >> /home/HwHiAiUser/.bashrc

sed -i "s#HwHiAiUser.*#HwHiAiUser:x:1000:1000::/home/HwHiAiUser:/bin/bash#g" /etc/passwd

chown -R HwHiAiUser:HwHiAiUser /home/HwHiAiUser/*
}

function install_new_driver()
{
bash A300-3010-npu-driver_21.0.1_ubuntu18.04-x86_64.run --full --quiet

}

function install_new_software()
{
su HwHiAiUser -c "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH && 
export PATH=/usr/local/python3.7.5/bin:$PATH &&
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 &&
export PATH=$JAVA_HOME/bin:$PATH &&
bash Ascend-cann-toolkit_5.0.2.alpha005_linux-x86_64.run --install"

su HwHiAiUser -c "tar zxvf MindStudio_3.0.2_linux.tar.gz"
}



function main()
{
download_software_package
install_dependencies
install_new_driver
install_new_software
reboot
}

main $@