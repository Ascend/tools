#!/bin/bash 

package_dir="${HOME}/faster_install_packages"
script_path="$( cd "$(dirname $BASH_SOURCE)" ; pwd -P)"

AscendToolkitInstallDir="${HOME}/Ascend/ascend-toolkit/"
MindStudioDir="${HOME}/MindStudio-ubuntu/"



function check_package()
{
	echo "start to check ascend package"
	case ${1} in
	"20.0.0") 
		#  check 20.0 toolkit arm package 
		if [[ ! -f $(find ${package_dir} -name "Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run" 2>/dev/null) ]];then 
			toolkit_20_0_arm=`cat ${script_path}/param.conf | grep "toolkit_20_0_arm" | awk -F'[ =]+' '{print $2}'`
			if [[ ${toolkit_20_0_arm}"x" = "x" ]];then
				echo "ERROR: invalid toolkit_20_0_arm url, please check param.conf "
				return 1
			fi
			wget -O ${package_dir}/"Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run"  ${toolkit_20_0_arm}  --no-check-certificate
			if [ $? -ne 0 ];then
				echo "download Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run failed, please check Network."
				return 1
			fi
		fi
		#  check 20.0 toolkit x86 package 
		if [[ ! -f $(find ${package_dir} -name "Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run" 2>/dev/null) ]];then 
			toolkit_20_0_x86=`cat ${script_path}/param.conf | grep "toolkit_20_0_x86" | awk -F'[ =]+' '{print $2}'`
			if [[ ${toolkit_20_0_x86}"x" = "x" ]];then
				echo "ERROR: invalid toolkit_20_0_x86 url, please check param.conf "
				return 1
			fi
			wget -O ${package_dir}/"Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run"  ${toolkit_20_0_x86}  --no-check-certificate
			if [ $? -ne 0 ];then
				echo "download Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run failed, please check Network."
				return 1
			fi
		fi
		# check mindstudio package 
		if [[ ! -f $(find ${package_dir} -name "mindstudio.tar.gz" 2>/dev/null) ]];then 
			MindStudio_20_0=`cat ${script_path}/param.conf | grep "MindStudio_20_0" | awk -F'[ =]+' '{print $2}'`
			if [[ ${MindStudio_20_0}"x" = "x" ]];then
				echo "ERROR: invalid MindStudio package  url, please check param.conf "
				return 1
			fi
			wget -O ${package_dir}/"mindstudio.tar.gz"  ${MindStudio_20_0}  --no-check-certificate
			if [ $? -ne 0 ];then
				echo "download mindstudio.tar.gz failed, please check Network."
				return 1
			fi
		fi
		;;
	"20.1") 
		#  check 20.1 toolkit arm package 
		if [[ ! -f $(find ${package_dir} -name "Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run" 2>/dev/null) ]];then 
			toolkit_20_1_arm=`cat ${script_path}/param.conf | grep "toolkit_20_1_arm" | awk -F'[ =]+' '{print $2}'`
			if [[ ${toolkit_20_1_arm}"x" = "x" ]];then
				echo "ERROR: invalid toolkit_20_1_arm url, please check param.conf "
				return 1
			fi
			wget -O ${package_dir}/"Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run"  ${toolkit_20_1_arm}  --no-check-certificate
			if [ $? -ne 0 ];then
				echo "download Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run failed, please check Network."
				return 1
			fi
		fi
		#  check 20.1 toolkit x86 package 
		if [[ ! -f $(find ${package_dir} -name "Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run" 2>/dev/null) ]];then 
			toolkit_20_1_x86=`cat ${script_path}/param.conf | grep "toolkit_20_1_x86" | awk -F'[ =]+' '{print $2}'`
			if [[ ${toolkit_20_1_x86}"x" = "x" ]];then
				echo "ERROR: invalid toolkit_20_1_x86 url, please check param.conf "
				return 1
			fi
			wget -O ${package_dir}/"Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run"  ${toolkit_20_1_x86}  --no-check-certificate
			if [ $? -ne 0 ];then
				echo "download Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run failed, please check Network."
				return 1
			fi
		fi
		# check mindstudio package 
		if [[ ! -f $(find ${package_dir} -name "MindStudio_2.0.0-beta2_ubuntu18.04-x86_64.tar.gz" 2>/dev/null) ]];then 
			MindStudio_20_1=`cat ${script_path}/param.conf | grep "MindStudio_20_1" | awk -F'[ =]+' '{print $2}'`
			if [[ ${MindStudio_20_1}"x" = "x" ]];then
				echo "ERROR: invalid MindStudio package  url, please check param.conf "
				return 1
			fi
			wget -O ${package_dir}/"MindStudio_2.0.0-beta2_ubuntu18.04-x86_64.tar.gz"  ${MindStudio_20_1}  --no-check-certificate
			if [ $? -ne 0 ];then
				echo "download MindStudio_2.0.0-beta2_ubuntu18.04-x86_64.tar.gz failed, please check Network."
				return 1
			fi
		fi
		;;
	*) 
		echo "[ERROR] Invalid Ascend Version."
		return 1
		;;
	esac 
	return 0
}

function install_toolkit() {
	echo "begin to install Ascend Toolkit"
	case ${1} in
	"20.0.0")
		cd ${package_dir}
		chmod 750 Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run 
		./Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run --install
		if [ $? -ne 0 ];then
			echo "install Ascend-Toolkit-20.0.RC1-arm64-linux_gcc7.3.0.run failed"
			return 1
		fi 	
		echo "install success, the 20.0 toolkit-arm64-linux package is installed."

		chmod 750 Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run
		./Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run --install
		if [ $? -ne 0 ];then
			echo "install Ascend-Toolkit-20.0.RC1-x86_64-linux_gcc7.3.0.run failed"
			return 1
		fi 	
		echo "install success, the 20.0 toolkit-x86_64 package is installed."

		;;
	"20.1")
		cd ${package_dir}
		chmod 750 Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run
		./Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run --install
		if [ $? -ne 0 ];then
			echo "install Ascend-cann-toolkit_20.1.rc1_linux-aarch64.run failed"
			return 1
		fi 	

		echo "install success, the 20.1 toolkit-arm64-linux package is installed."

		chmod 750 Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run
		./Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run --install
		if [ $? -ne 0 ];then
			echo "install Ascend-cann-toolkit_20.1.rc1_linux-x86_64.run failed"
			return 1
		fi 	

		echo "install success, the 20.1 toolkit-x86_64 package is installed."
		;;	
	*)
		echo "[ERROR] Invalid Ascend Version."
		return 1
		;;
	esac

	return 0
}


function check_hardware_environment() {
	# 检查当前ubuntu的版本
	Ubuntu_version=`cat /etc/issue | grep Ubuntu |awk -F'[ ]+' '{print $2}'`
	if [ ! $Ubuntu_version ] || [ ${Ubuntu_version%.*} != "18.04" ]; then
		echo "This script is only available for Ubuntu18.04. If not, please change the script or Ubuntu version. Exit installation"
		return 1
	fi

	# 检查当前ubuntu系统的剩余的内存,内存小于4G 返回失败报错
	mt=`free | tr [:blank:] \\\n | grep [0-9] | sed -n '3p'`
	mx=`expr $mt \/ 1024 \/ 1024`
	echo "linux memory is $mx G"
	if [ $mx -lt 4 ]; then
		echo "Linux Mem ${mx} < 4G, please add mem for using MindStudio."
		echo "Exit installation"
		return 1
	else
		echo "Memory is enough. To be continue."
	fi

	# 检查当前ubuntu系统剩余的硬盘空间,硬盘空间小于4G 返回失败报错
	max_num=4
	df_num=`df -h | awk -F' ' '$6 ~ /^\/$/ {print $4}'|awk -F'[ Gg]+' '{print $1}'`
	echo "linux space is $df_num G"
	if [ $df_num -lt $max_num ]; then
		echo "Linux Space is ${df_num}G < 4G. is not enough, please manually release space to download mindstudio and toolkit."
		echo "Exit installation"
		return 1
	else
		echo "Space is enough. To be continue."
	fi

	return 0
}


function install_dependencies() {
	echo "The next step is system update and install Necessary dependent software"
	sudo apt update
	if [[ $? -ne 0 ]];then
		echo "Update failed.Please check the network"
		return 1
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

    return 0
}

function uninstallMindStudio() {
	# uninstall 20.0 20.1
	echo "uninstall MindStudio"
	rm -rf ${MindStudioDir}
	rm -rf ${HOME}/.cache/Huawei/MindStudioMS-*.*
	rm -rf ${HOME}/.config/Huawei/MindStudioMS-*.*
	rm -rf ${HOME}/.mindstudio
	rm -rf ${HOME}/.MindStudioMS-*
	return 0
}

function uninstallToolkit() {
	# uninstall 20.0 20.1
	sudo rm -rf ${AscendToolkitInstallDir}
	return 0
}

function install_mindstudio() {
	echo "begin to install Mind Studio"
	case ${1} in
	"20.0.0")
		tar -zxvf ${package_dir}/mindstudio.tar.gz -C ${HOME}
		if [ $? -ne 0 ];then
			echo "tar -zxvf ${package_dir}/mindstudio.tar.gz -C ${HOME} failed"
			return 1
		fi 
		;;
	"20.1")
		tar -zxvf ${package_dir}/MindStudio_2.0.0-beta2_ubuntu18.04-x86_64.tar.gz -C ${HOME}
		if [ $? -ne 0 ];then
			echo "tar -zxvf ${package_dir}/MindStudio_2.0.0-beta2_ubuntu18.04-x86_64.tar.gz -C ${HOME} failed"
			return 1
		fi 	
		;;	
	*)
		echo "[ERROR] Invalid Ascend Version."
		return 1
		;;
	esac
	echo "MindStudio is about to open."
	bash ${HOME}/MindStudio-ubuntu/bin/MindStudio.sh &
	return 0
}

main()
{
    check_hardware_environment
	if [ $? -ne 0 ];then
		return 1
	fi 

	declare -i toolkit_flag=0
	declare -i mindstudio_flag=0
	declare -i uninstall_mode=0
	if [[ -d "${AscendToolkitInstallDir}" ]] || [[ -d "${MindStudioDir}" ]];then
		if [[ -d "${AscendToolkitInstallDir}" ]];then 
			toolkit_flag=1
			echo "Tookit package has been found in current environment"
			toolkitVersion=$(cat ${HOME}/Ascend/ascend-toolkit/latest/toolkit/version.info 2>/dev/null)
			if [[ ${toolkitVersion}"x" != "x" ]];then
				if [[ "${toolkitVersion}" =~ "1.75" ]];then
					echo "surent toolkit version is 20.1"
				elif [[ "${toolkitVersion}" =~ "1.73" ]];then
					echo "current toolkit version is 20.0.0"
				fi
			fi
		fi

		if [[ -d "${MindStudioDir}" ]];then 
			mindstudio_flag=1
			echo "MindStudio has been found in current environment"
		fi

		if [[ ${toolkit_flag} -eq 1 ]] && [[ ${mindstudio_flag} -eq 1 ]];then
			uninstall_mode=1
			confirm_tips="Do you want to uninstall the current Ascend toolkit and Mind Studio ?. default option is Y: "
		elif [[ ${toolkit_flag} -eq 0 ]] && [[ ${mindstudio_flag} -eq 1 ]];then
			uninstall_mode=2
			confirm_tips="Do you want to uninstall the current Mind Studio?. default option is Y: "
		elif [[ ${toolkit_flag} -eq 1 ]] && [[ ${mindstudio_flag} -eq 0 ]];then
			uninstall_mode=3
			confirm_tips="Do you want to uninstall the current Ascend toolkit?. default option is Y: "
		fi

		response=""
		declare -i choiceTimes=0
		while [[ ${response}"x" = "x" ]];do
			[[ ${choiceTimes} -ge 3 ]] && exit 1 || ((choiceTimes++))
			read -p "${confirm_tips}" response
			if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
				echo "exit this script"
        		return 0
			elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
				echo "begin to uninstall..."
				break
			else
				echo "[ERROR] Please input Y/N!"
       	 		response=""
			fi
		done 

		case ${uninstall_mode} in 
		1)
			uninstallMindStudio
			uninstallToolkit
			;;
		2)
			uninstallMindStudio
			;;
		3)
			uninstallToolkit
			;;
		*)
			;;
		esac
	fi

cat << EOF
"Current Ascend-version list:"
    "1 : 20.0.0"
    "2 : 20.1"
EOF
	response=""
	declare -i choiceTimes=0
	while [[ ${response}"x" = "x" ]];do
		[[ ${choiceTimes} -ge 3 ]] && exit 1 || ((choiceTimes++))
		read -p "please input your Ascend-verison in this list(eg:1):" response
		case ${response} in
		"1") 
			Ascend_version="20.0.0"
			;;
		"2") 
			Ascend_version="20.1"
			;;
		*) 
			response=""
			echo "[ERROR] Input Ascend-version Error,Please check your input"
			;;
		esac 
	done 
	
	check_package "${Ascend_version}"
	if [[ $? -ne 0 ]];then
		echo "failed to prepare necessary software package "
		return 1
	fi

	echo "finished preparing necessary software package"

    install_dependencies
	if [[ $? -ne 0 ]];then
		echo "install dependent software failed.Please check the network"
		return 1
	fi

    bash ${script_path}/python_install.sh
	if [[ $? -ne 0 ]];then
		echo "prepare python environment failed"
		return 1
	fi

	install_toolkit "${Ascend_version}"
	if [[ $? -ne 0 ]];then
		echo "failed to install ${Ascend_version} Ascend Toolkit."
		return 1
	fi

	install_mindstudio "${Ascend_version}"
	if [[ $? -ne 0 ]];then
		echo "failed to install ${Ascend_version} Mind Studio."
		return 1
	fi

	echo "The ${Ascend_version} environment was successfully deployed"
	return 0
}
main
