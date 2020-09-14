#!/bin/bash 
function check_python3_lib() {
	echo "Check python3 libs ......"

	attrs_flag=`pip3.7.5 show attrs 2>/dev/null`
	if [[ ! $attrs_flag ]];then
		pip3.7.5 install attrs --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install attrs faild ,Please manually attrs"
			return 1
		fi
	fi

	psutil_flag=`pip3.7.5 show psutil 2>/dev/null`
	if [[ ! $psutil_flag ]];then
		pip3.7.5 install psutil --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install psutil faild ,Please manually psutil"
			return 1
		fi
	fi

	decorator_flag=`pip3.7.5 show decorator 2>/dev/null`
	if [[ ! $decorator_flag ]];then
		pip3.7.5 install decorator --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install decorator faild ,Please manually decorator"
			return 1
		fi
	fi

	numpy_flag=`pip3.7.5 show numpy 2>/dev/null`
	if [[ ! $numpy_flag ]];then
		pip3.7.5 install numpy --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install numpy faild ,Please manually numpy"
			return 1
		fi
	fi

	protobuf_version=`pip3.7.5 show protobuf | grep Version| awk -F'[: ]+' '{print $2}' 2>/dev/null`
	if [[ ! $protobuf_version ]] || [ $protobuf_version != "3.11.3" ];then
		pip3.7.5 install protobuf==3.11.3 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install  protobuf==3.11.3 faild ,Please manually protobuf"
			return 1
		fi
	fi

	scipy_flag=`pip3.7.5 show scipy 2>/dev/null`
	if [[ ! $scipy_flag ]];then
		pip3.7.5 install scipy --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install scipy faild ,Please manually scipy"
			return 1
		fi
	fi

	sympy_flag=`pip3.7.5 show sympy 2>/dev/null`
	if [[ ! $sympy_flag ]];then
		pip3.7.5 install sympy --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install sympy faild ,Please manually sympy"
			return 1
		fi
	fi

	cffi_flag=`pip3.7.5 show cffi 2>/dev/null`
	if [[ ! $cffi_flag ]];then
		pip3.7.5 install cffi --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install cffi faild ,Please manually cffi"
			return 1
		fi
	fi

	grpcio_flag=`pip3.7.5 show grpcio 2>/dev/null`
	if [[ ! $grpcio_flag ]];then
		pip3.7.5 install grpcio --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install grpcio faild ,Please manually grpcio"
			return 1
		fi
	fi

	grpcio_tools_flag=`pip3.7.5 show grpcio-tools 2>/dev/null`
	if [[ ! $grpcio_tools_flag ]];then
		pip3.7.5 install grpcio-tools --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install grpcio-tools faild ,Please manually grpcio-tools"
			return 1
		fi
	fi

	requests_flag=`pip3.7.5 show requests 2>/dev/null`
	if [[ ! $requests_flag ]];then
		pip3.7.5 install requests --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install requests faild ,Please manually requests"
			return 1
		fi
	fi

	gnureadline_flag=`pip3.7.5 show gnureadline 2>/dev/null`
	if [[ ! $gnureadline_flag ]];then
		pip3.7.5 install gnureadline --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install gnureadline faild ,Please manually gnureadline"
			return 1
		fi
	fi

	coverage_flag=`pip3.7.5 show coverage 2>/dev/null`
	if [[ ! $coverage_flag ]];then
		pip3.7.5 install coverage --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install coverage faild ,Please manually coverage"
			return 1
		fi
	fi

	matplotlib_flag=`pip3.7.5 show matplotlib 2>/dev/null`
	if [[ ! $matplotlib_flag ]];then
		pip3.7.5 install matplotlib --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install matplotlib faild ,Please manually matplotlib"
			return 1
		fi
	fi

	PyQt5_version=`pip3.7.5 show PyQt5 | grep Version| awk -F'[: ]+' '{print $2}' 2>/dev/null`
	if [[ ! $PyQt5_version ]] || [ $PyQt5_version != "5.14.0" ];then
		pip3.7.5 install PyQt5==5.14.0 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install  PyQt5==5.14.0 faild ,Please manually PyQt5"
			return 1
		fi
	fi

	tensorflow_version=`pip3.7.5 show tensorflow | grep Version| awk -F'[: ]+' '{print $2}' 2>/dev/null`
	if [[ ! $tensorflow_version ]] || [ $tensorflow_version != "1.15" ];then
		pip3.7.5 install tensorflow==1.15 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install  tensorflow==1.15 faild ,Please manually tensorflow"
			return 1
		fi
	fi

	pylint_flag=`pip3.7.5 show pylint 2>/dev/null`
	if [[ ! $pylint_flag ]];then
		pip3.7.5 install pylint --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install pylint faild ,Please manually pylint"
			return 1
		fi
	fi

	tornado_version=`pip3.7.5 show tornado | grep Version| awk -F'[: ]+' '{print $2}' 2>/dev/null`
	if [[ ! $tornado_version ]] || [ $tornado_version != "5.1.0" ];then
		pip3.7.5 install tornado==5.1.0 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install tornado==5.1.0 faild ,Please manually tornado"
			return 1
		fi
	fi

	return 0
	echo "python3 libs have benn prepared."
}

function install_python3.7.5() {
	sudo rm -rf  /usr/bin/python3.7.5
	sudo rm -rf  /usr/bin/pip3.7.5
	sudo rm -rf  /usr/bin/python3.7
	sudo rm -rf  /usr/bin/pip3.7

	echo "python3.7.5 and pip3.7.5 are about to install."
	cd $HOME		
	find  ~/Python-3.7.5.tgz -exec rm -rf {} +
	find  ~/Python-3.7.5 -exec sudo rm -rf {} +

	wget https://www.python.org/ftp/python/3.7.5/Python-3.7.5.tgz
	if [ $? -ne 0 ];then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	tar -zxvf Python-3.7.5.tgz
	cd Python-3.7.5
	./configure --prefix=/usr/local/python3.7.5 --enable-shared
	make
	sudo make install

	sudo cp /usr/local/python3.7.5/lib/libpython3.7m.so.1.0 /usr/lib
	sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/bin/python3.7
	sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/bin/pip3.7
	sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/bin/python3.7.5
	sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/bin/pip3.7.5
	return 0
}

function install_toolkit() {
	TOOLKIT_flag_arm64=`find $HOME -maxdepth 1 -name "Ascend-*-arm64-*.run" 2> /dev/null`
	TOOLKIT_flag_x86_64=`find $HOME -maxdepth 1 -name "Ascend-*-x86_64-*.run" 2> /dev/null`
	if [[ ! $TOOLKIT_flag_arm64 ]] && [[ ! $TOOLKIT_flag_x86_64 ]];then
		echo "[Error]:Can not find the Ascend-Toolkit-[version]-arm64-linux_gcc7.3.0.run package and Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run package "
		echo "please go to the official website to download the Toolkit installation package you need."
		echo "Exit installation."
		return 1
	elif [ $TOOLKIT_flag_arm64 ] && [ $TOOLKIT_flag_x86_64 ];then
		echo "find the Ascend-Toolkit-[version]-arm64-linux_gcc7.3.0.run package and Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run package "
		TOOLKIT_arm64="YES"
		TOOLKIT_x86_64="YES"
	elif [ $TOOLKIT_flag_arm64 ];then
		echo "only find Ascend-Toolkit-[version]-arm64-linux_gcc7.3.0.run package"
		echo "please go to the official website to download Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run package."
		return 1;
	elif [ $TOOLKIT_flag_x86_64 ];then
		echo "only find Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run package"
		echo "please go to the official website to download Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run package."
		return 1;
	fi
	return 0
}

main()
{
	Ubuntu_version=`cat /etc/issue | grep Ubuntu |awk -F'[ ]+' '{print $2}'`
	if [ ! $Ubuntu_version ] || [ ${Ubuntu_version%.*} != "18.04" ]; then
		echo "This script is only available for Ubuntu18.04. If not, please change the script or Ubuntu version. Exit installation"
		return 1
	fi

	mt=`free | tr [:blank:] \\\n | grep [0-9] | sed -n '1p'`
	mx=`expr $mt \/ 1024 \/ 1024`
	echo "linux memory is $mx G"
	if [ $mx -lt 4 ]; then
		echo "Linux Mem < 4G, please add mem for using MindStudio."
		echo "Exit installation"
		return 1
	else
		echo "Memory is enough. To be continue."
	fi

	max_num=4
	df_num=`df -h | awk -F' ' '$6 ~ /^\/$/ {print $4}'|awk -F'[ Gg]+' '{print $1}'`
	echo "linux space is $df_num G"
	if [ $df_num -le $max_num ]; then
		echo "Space is not enough, please manually release space to download mindstudio and toolkit."
		echo "Exit installation"
		return 1
	else
		echo "Space is enough. To be continue."
	fi

	echo "The C73 development environment is about to be installed."
	echo "ubuntu : 18.04"
	echo "MindStudio: 2.3.3"

	echo "The next step is system update"
	sudo apt update
	if [[ $? -ne 0 ]];then
		echo "Update failed.Please check the network"
		return 1
	fi

	C73_flag=`find $HOME -maxdepth 1 -name "MindStudio-ubuntu" 2> /dev/null`
	if [[ $C73_flag ]];then
		read -p "[INFO] The Mind Studio is existence. Do you want to re-install ? [Y/N]. default option is Y: " response
		if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
			echo "MindStudio is about to open."
			bash $C73_flag/bin/MindStudio.sh &
			return 0
		elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
			rm -rf $C73_flag
			rm -rf .mindstudio
			rm -rf .MindStudioMS-2.3
		else
			echo "[ERROR] Please input Y/N!"
			return 1
		fi
	fi


	package_flag=`find $HOME -maxdepth 1 -name "mindstudio.tar.gz" 2> /dev/null`
	if [[ ! $package_flag ]];then
		read -p "[INFO] Can not find mindstudio.tar.gz in $HOME,do you want download ? [Y/N]. default option is Y: " response
		if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
			echo "Exit installation"
			return 1
		elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
			MIN_Download="YES"
		else
			echo "[ERROR] Please input Y/N!"
			return 1
		fi
	else
		echo "tar zxvf $package_flag" 
		tar zxvf $package_flag
	fi


	TOOLKIT_flag=`find ~/Ascend/ascend-toolkit/ -name "20.0.*" 2> /dev/null`
	if [ $TOOLKIT_flag ]; then
		read -p "ascend-toolkit have been installed , do you want to reinstall ascend-toolkit ? [Y/N]. default option is N: " response
		if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]|| [ $response"z" = "z" ]; then
			echo "To be continue."
		elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ]; then
			sudo rm -rf ~/Ascend
			echo "To be continue."
			install_toolkit
			if [ $? -ne 0 ];then
				return 1
			fi 
		else
			echo "[ERROR] Please input Y/N!"
			return 1
		fi
	else
		install_toolkit
		if [ $? -ne 0 ];then
			return 1
		fi 
	fi

	sudo apt-get install -y gcc g++ make cmake unzip wget zlib1g zlib1g-dev libsqlite3-dev openssl libssl-dev libffi-dev pciutils net-tools 2>/dev/null
	if [ $? -ne 0 ];then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	sudo apt-get install -y xterm firefox xdg-utils fonts-droid-fallback fonts-wqy-zenhei fonts-wqy-microhei fonts-arphic-ukai fonts-arphic-uming 2>/dev/null
	if [ $? -ne 0 ];then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	sudo apt-get -y install libcanberra-gtk-module openjdk-8-jdk 2>/dev/null
	if [ $? -ne 0 ];then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	sudo apt install  -y git 2>/dev/null
	if [ $? -ne 0 ];then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	sudo apt-get install -y qemu-user-static binfmt-support python3-yaml gcc-aarch64-linux-gnu g++-aarch64-linux-gnu g++-5-aarch64-linux-gnu 2>/dev/null
	if [ $? -ne 0 ];then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	pip_flag=`pip3.7.5  --version 2>/dev/null`
	python_flag=`python3.7.5  --version 2>/dev/null`
	if [[ $pip_flag ]] && [[ $python_flag ]];then
		read -p "python3.7.5 and pip3.7.5 have been installed , do you want to reinstall python3.7.5 ?. [Y/N]. default option is N: " response
		if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ] || [ $response"z" = "z" ]; then
			check_python3_lib
			if [ $? -ne 0 ];then
				echo "python3.7.5 libs install failed! "
				echo "Now reinstalling python3.7.5 "
				install_python3.7.5
				if [ $? -ne 0 ];then
					echo "reinstall python3.7.5 failed"
					return 1
				fi
				check_python3_lib
				if [ $? -ne 0 ];then
					echo "installing python libs failed"
					return 1
				fi
			fi
		elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ]; then
			install_python3.7.5
			if [ $? -ne 0 ];then
				echo "reinstall python3.7.5 failed"
				return 1
			fi
			check_python3_lib
			if [ $? -ne 0 ];then
				echo "installing python libs failed"
				return 1
			fi
		else
			echo "[ERROR] Please input Y/N!"
			return 1
		fi
	else
		install_python3.7.5
		if [ $? -ne 0 ];then
			echo "install python3.7.5 failed"
			return 1
		fi
		check_python3_lib
		if [ $? -ne 0 ];then
			echo "install python libs failed"
			return 1
		fi
	fi

	if [[ $MIN_Download ]];then
		wget -O $HOME/mindstudio.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/C73B050/mindstudio.tar.gz" --no-check-certificate
		if [ $? -ne 0 ];then
			echo "ERROR: download failed, please check Network."
			rm -rf $HOME/mindstudio.tar.gz
			return 1
		else
			cd $HOME
			tar zxvf mindstudio.tar.gz
		fi
	fi

	cd $HOME
	if [[ $TOOLKIT_arm64 ]];then
		find Ascend-*-arm64-*.run -exec chmod 777 {} +
		find Ascend-*-arm64-*.run -exec ./{} --install \;
		if [ $? -ne 0 ];then
			echo "ERROR: install failed, please verify that the toolkit-arm64 package is installed."
			return 1
		else 
			echo "install success, the toolkit-arm64 package is installed."
		fi
	fi

	if [[ $TOOLKIT_x86_64 ]];then
		find Ascend-*-x86_64-*.run -exec chmod 777 {} +
		find Ascend-*-x86_64-*.run -exec ./{} --install \;
		if [ $? -ne 0 ];then
			echo "ERROR: install failed, please verify that the toolkit-x86_64 package is installed."
			return 1
		else 
			echo "install success, the toolkit-x86_64 package is installed."
		fi
    fi

	echo "The C73 environment was successfully deployed, with MindStudio version 2.3.3"
	
	echo "MindStudio is about to open."
	bash $HOME/MindStudio-ubuntu/bin/MindStudio.sh &
}
main
