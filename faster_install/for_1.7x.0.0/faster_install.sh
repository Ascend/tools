#!/bin/bash
main()
{
	sudo apt-get update
	if [[ $? -ne 0 ]];then
			echo "Update failed.Please check the network."
			return 1
	fi
	
	read -p "Is this Ubuntu18.04? This script is only available for Ubuntu18.04. If not, please change the script or Ubuntu version. [Y/N]" response
        if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
                  echo "Exit installation"
                  return 1
        elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
                  echo "To be continue."
        else
                  echo "[ERROR] Please input Y/N!"
                  return 1
        fi

	mt=`free | tr [:blank:] \\\n | grep [0-9] | sed -n '1p'`
	mx=`expr $mt \/ 1024 \/ 1024 + 1`
	echo "linux memory is $mx G"
        if [ $mx \< 4 ]; then
		  echo "Linux Mem < 4G, please add mem for using MindStudio."
                  echo "Exit installation"
                  return 1
        else
                  echo "Memory is enough. To be continue."
        fi

	max_num=4
	df_num=`df -h |grep /dev/sda1|awk -F'[ G]+' '{print $4}'`
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

	C73_flag=`find $HOME -maxdepth 1 -name "MindStudio-ubuntu" 2> /dev/null`
    	if [[ $C73_flag ]];then
        	read -p "[INFO] The Mindstudio is existence.Do you want to re-install ? [Y/N]: " response
        	if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
            		echo "To be continue."
        	elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
            		rm -rf MindStudio-ubuntu
        	else
			echo "[ERROR] Please input Y/N!"
			return 1
        	fi
    	fi

	package_flag=`find $HOME -maxdepth 1 -name "mindstudio.tar.gz" 2> /dev/null`
    	if [[ ! $package_flag ]];then
        	read -p "[INFO] Can not find mindstudio.tar.gz in $HOME,Do you want download[Y/N]: " response
       		if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
            		echo "Exit installation"
            		return 1
        	elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
            		MIN_Download="YES"
        	else
            		echo "[ERROR] Please input Y/N!"
            		return 1
        	fi
    	fi

	TOOLKIT_flag=`find ~/Ascend/ascend-toolkit/ -name "20.0.*" 2> /dev/null`
	if [[ ! $TOOLKIT_flag ]];then
		TOOLKIT_flag_arm64=`find $HOME -maxdepth 1 -name "Ascend-Toolkit-*-arm64-linux_gcc7.3.0.run" 2> /dev/null`
    	if [[ ! $TOOLKIT_flag_arm64 ]];then
				echo "[Error]:Can not find the Ascend-Toolkit-[version]-arm64-linux_gcc7.3.0.run package, please go to the official website to download the Toolkit installation package you need."
				echo "Exit installation."
		return 1
		else
				TOOLKIT_arm64="YES"
    	fi

		TOOLKIT_flag_x86_64=`find $HOME -maxdepth 1 -name "Ascend-Toolkit-*-x86_64-linux_gcc7.3.0.run" 2> /dev/null`
        if [[ ! $TOOLKIT_flag_x86_64 ]];then
				echo "[Error]:Can not find the Ascend-Toolkit-[version]-x86_64-linux_gcc7.3.0.run package, please go to the official website to download the Toolkit installation package you need."
				echo "Exit installation."
		return 1
		else
				TOOLKIT_x86_64="YES"
		fi
	fi

	PiP_flag=`find / -maxdepth 3 -name "python3.7.5" 2> /dev/null`
        if [[ $PiP_flag ]];then
                echo "[INFO] the python3.7.5 is existence."
		else
				PiP_Download="YES"
        fi

	if [[ $MIN_Download ]];then
      		wget -O $HOME/mindstudio.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/C73B050/mindstudio.tar.gz" --no-check-certificate
			if [ $? -ne 0 ];then
            		echo "ERROR: download failed, please check Network."
            		rm -rf $HOME/mindstudio.tar.gz
            		return 1
        	fi
    	fi

	if [[ $TOOLKIT_arm64 ]];then
		find Ascend-Toolkit-*-arm64-linux_gcc7.3.0.run -exec chmod 777 {} \;
		find Ascend-Toolkit-*-arm64-linux_gcc7.3.0.run -exec ./{} --install \;
        	if [ $? -ne 0 ];then
            		echo "ERROR: install failed, please verify that the toolkit-arm64 package is installed."
            		rm -rf $HOME/Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run
            		return 1
        	fi
    	fi

	if [[ $TOOLKIT_x86_64 ]];then
		find Ascend-Toolkit-*-x86_64-linux_gcc7.3.0.run -exec chmod 777 {} \;
		find Ascend-Toolkit-*-x86_64-linux_gcc7.3.0.run -exec ./{} --install \;
        	if [ $? -ne 0 ];then
            		echo "ERROR: install failed, please verify that the toolkit-x86_64 package is installed."
            		rm -rf $HOME/Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run
            		return 1
			else
					Toolkit_bashrc_flag="YES"
			fi
    fi
	
	sudo apt-get install -y gcc g++ make cmake unzip zlib1g zlib1g-dev libsqlite3-dev openssl libssl-dev libffi-dev pciutils net-tools
	if [ $? -ne 0 ];then
                echo "[ERROR]: install failed, please check Network."
                return 1
        fi

	sudo apt-get install -y xterm firefox xdg-utils fonts-droid-fallback fonts-wqy-zenhei fonts-wqy-microhei fonts-arphic-ukai fonts-arphic-uming
        if [ $? -ne 0 ];then
                echo "[ERROR]: install failed, please check Network."
                return 1
        fi

	sudo apt-get -y install libcanberra-gtk-module openjdk-8-jdk
        if [ $? -ne 0 ];then
                echo "[ERROR]: install failed, please check Network."
                return 1
        fi

	sudo apt install  -y git
        if [ $? -ne 0 ];then
                echo "[ERROR]: install failed, please check Network."
                return 1
        fi

	sudo apt-get install -y qemu-user-static binfmt-support python3-yaml gcc-aarch64-linux-gnu g++-aarch64-linux-gnu g++-5-aarch64-linux-gnu
        if [ $? -ne 0 ];then
                echo "[ERROR]: install failed, please check Network."
                return 1
        fi

	if [[ $PiP_Download ]];then
		cd $HOME
		mkdir .pip
		touch .pip/pip.conf
		echo "[global]" > .pip/pip.conf
		echo "trusted-host = mirrors.aliyun.com" >> .pip/pip.conf
		echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> .pip/pip.conf

		find  ~/Python-3.7.5.tgz -exec rm -rf {} \;
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
	
		pip3.7.5 install attrs --user  
		pip3.7.5 install psutil --user
		pip3.7.5 install decorator --user
		pip3.7.5 install numpy --user
		pip3.7.5 install protobuf==3.11.3 --user
		pip3.7.5 install scipy --user
		pip3.7.5 install sympy --user
		pip3.7.5 install cffi --user
		pip3.7.5 install grpcio --user
		pip3.7.5 install grpcio-tools --user
		pip3.7.5 install requests --user
		pip3.7.5 install gnureadline --user
		pip3.7.5 install coverage --user
		pip3.7.5 install matplotlib --user
		pip3.7.5 install PyQt5==5.14.0 --user
		pip3.7.5 install tensorflow==1.15 --user
		pip3.7.5 install pylint --user
		pip3.7.5 install tornado==5.1.0 --user
		Pip_bashrc_flag="YES"
	fi

	cd ~
	tar zxvf mindstudio.tar.gz
	
	if [[ $Min_bashrc_flag ]];then
			echo "export LD_LIBRARY_PATH=${install_path}/atc/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc
			echo "export ASCEND_OPP_PATH=${install_path}/opp" >> ~/.bashrc
	fi
	
	if [[ $Toolkit_bashrc_flag ]];then
			find ~/Ascend/ascend-toolkit/ -name "20.0.*" -exec echo "export install_path={}" >> ~/.bashrc \;
	fi
	
	if [[ $Pip_bashrc_flag ]];then
			echo "export PATH=/usr/local/python3.7.5/bin:${install_path}/atc/ccec_compiler/bin:${install_path}/atc/bin:$PATH" >> ~/.bashrc
			echo "export PYTHONPATH=${install_path}/atc/python/site-packages/te:${install_path}/atc/python/site-packages/topi:$PYTHONPATH" >> ~/.bashrc
	fi
	
	source ~/.bashrc
			
	echo "The C73 environment was successfully deployed, with MindStudio version 2.3.3"
	
	echo "MindStudio is about to open."
	bash $HOME/MindStudio-ubuntu/bin/MindStudio.sh
}
main
