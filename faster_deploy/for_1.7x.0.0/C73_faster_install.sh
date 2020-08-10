#!/bin/bash
main()
{
	echo "The C73 development environment is about to be installed."
	echo "ubuntu : 18.04"
	echo "MindStudio: 2.3.3"
	echo "Toolkit: 20.0.RC1"

	sudo apt-get update
    	if [[ $? -ne 0 ]];then
        	echo "[ERROR] Please check if the network is connected or Check if the sources in /etc/apt/sources.list are available"
         	return 1
    	fi

	C73_flag=`find $HOME -maxdepth 1 -name "MindStudio-ubuntu" 2> /dev/null`
    	if [[ $C73_flag ]];then
        	read -p "[INFO] The Mindstudio is existence.Do you want to re-install ? [Y/N]: " response
        	if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
            		echo "Exit installation"
            		return 1
        	elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
            		rm -rf MindStudio-ubuntu
        	else
			echo "[ERROR] Please input Y/N!"
			return 1
        	fi
    	fi

	package_flag=`find $HOME -maxdepth 1 -name "mindstudio.tar.gz" 2> /dev/null`
    	if [[ ! $package_flag ]];then
        	read -p "[INFO] can not find mindstudio.tar.gz in $HOME,Do you want download[Y/N]: " response
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

	TOOLKIT_flag_arm64=`find $HOME -maxdepth 1 -name "Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run" 2> /dev/null`
    	if [[ ! $TOOLKIT_flag_arm64 ]];then
        	read -p "[INFO] can not find Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run in $HOME, Do you want download[Y/N]: " response
        	if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
            		echo "Exit installation"
            		return 1
        	elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
            		TOOLKIT_arm64_Download="YES"
        	else
            		echo "[ERROR] Please input Y/N!"
            		return 1
        	fi
    	fi

	TOOLKIT_flag_x86_64=`find $HOME -maxdepth 1 -name "Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run" 2> /dev/null`
        if [[ ! $TOOLKIT_flag_x86 ]];then
                read -p "[INFO] can not find Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run in $HOME, Do you want download[Y/N]: " response
                if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
                        echo "Exit installation"
                        return 1
                elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
                        TOOLKIT_x86_64_Download="YES"
                else
                        echo "[ERROR] Please input Y/N!"
                        return 1
                fi
        fi

	if [[ $MIN_Download ]];then
      		wget -O $HOME/mindstudio.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/C73B050/mindstudio.tar.gz" --no-check-certificate
        	if [ $? -ne 0 ];then
            		echo "ERROR: download failed, please check Network."
            		rm -rf $HOME/mindstudio.tar.gz
            		return 1
        	fi
    	fi

	if [[ $TOOLKIT_arm64_Download ]];then
        	wget -O $HOME/Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/C73B050/Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run" --no-check-certificate
        	if [ $? -ne 0 ];then
            		echo "ERROR: download failed, please check Network."
            		rm -rf $HOME/Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run
            		return 1
        	fi
    	fi

	if [[ $TOOLKIT_x86_64_Download ]];then
                wget -O $HOME/Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/C73B050/Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run"  --no-check-certificate
		if [ $? -ne 0 ];then
                        echo "ERROR: download failed, please check Network."
                        rm -rf $HOME/Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run
                        return 1
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

	cd $HOME
	mkdir .pip
	touch .pip/pip.conf
	echo "[global]" > .pip/pip.conf
	echo "trusted-host = mirrors.aliyun.com" >> .pip/pip.conf
	echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> .pip/pip.conf

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

	cd $HOME
	chmod 777 Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run
	chmod 777 Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run
	./Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run --install
	./Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run --install
	tar zxvf mindstudio.tar.gz	

	echo "export install_path=${HOME}/Ascend/ascend-toolkit/20.0.RC1" >> ~/.bashrc
	echo "export PATH=/usr/local/python3.7.5/bin:${install_path}/atc/ccec_compiler/bin:${install_path}/atc/bin:$PATH" >> ~/.bashrc
	echo "export PYTHONPATH=${install_path}/atc/python/site-packages/te:${install_path}/atc/python/site-packages/topi:$PYTHONPATH" >> ~/.bashrc
	echo "export LD_LIBRARY_PATH=${install_path}/atc/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc
	echo "export ASCEND_OPP_PATH=${install_path}/opp" >> ~/.bashrc
	source ~/.bashrc

	echo "The C73 environment was successfully deployed, with MindStudio version 2.3.3 and Toolkit version 20.0.RC1"
	
	echo "MindStudio is about to open."
	bash $HOME/MindStudio-ubuntu/bin/MindStudio.sh
}
main
