#!/bin/bash 

package_dir="${HOME}/faster_install_packages"
python3_7_5_package="https://www.python.org/ftp/python/3.7.5/Python-3.7.5.tgz"


function checkandinstall_python3_lib() {
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

	xlrd_flag=`pip3.7.5 show xlrd 2>/dev/null`
	if [[ ! $xlrd_flag ]];then
		pip3.7.5 install xlrd --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install xlrd faild ,Please manually xlrd"
			return 1
		fi
	fi

	pandas_flag=`pip3.7.5 show pandas 2>/dev/null`
	if [[ ! $pandas_flag ]];then
		pip3.7.5 install pandas --user  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [[ $? -ne 0 ]];then
			echo "[ERROR] pip3.7.5 install pandas faild ,Please manually pandas"
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

	mkdir -p ${package_dir}
	sudo find  ${package_dir}/Python-3.7.5.tgz -exec rm -rf {} + 2>/dev/null
	sudo find  ${package_dir}/Python-3.7.5 -exec sudo rm -rf {} + 2>/dev/null

	wget -O ${package_dir}/Python-3.7.5.tgz ${python3_7_5_package} --no-check-certificate
	if [[ $? -ne 0 ]] || [[ $(echo "7802b6b70bb7a785e264b8cb4e9b9bcd  ${package_dir}/Python-3.7.5.tgz" | md5sum --status -c) -ne 0 ]] ;then
		echo "[ERROR]: install failed, please check Network."
		return 1
	fi

	tar -zxvf ${package_dir}/Python-3.7.5.tgz -C ${package_dir}

	cd ${package_dir}/Python-3.7.5

	./configure --prefix=/usr/local/python3.7.5 --enable-shared
	if [[ $? -ne 0 ]];then
        echo "./configure --prefix=/usr/local/python3.7.5 --enable-shared failed"
        return 1
    fi

	make
	if [[ $? -ne 0 ]];then
        echo "compile python3.7.5 failed"
        return 1
    fi

	sudo apt install -y zlib1g zlib1g-dev libffi-dev
	sudo make install
	if [[ $? -ne 0 ]];then
        echo "make install python3.7.5 failed"
        return 1
    fi

	sudo cp /usr/local/python3.7.5/lib/libpython3.7m.so.1.0 /usr/lib
	if [[ $? -ne 0 ]];then
        echo "sudo cp /usr/local/python3.7.5/lib/libpython3.7m.so.1.0 /usr/lib failed"
        return 1
    fi
	sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/bin/python3.7
	if [[ $? -ne 0 ]];then
        echo "sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/bin/python3.7 failed"
        return 1
    fi
	sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/bin/pip3.7
	if [[ $? -ne 0 ]];then
        echo "sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/bin/pip3.7 failed"
        return 1
    fi
	sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/bin/python3.7.5
	if [[ $? -ne 0 ]];then
        echo "sudo ln -s /usr/local/python3.7.5/bin/python3 /usr/bin/python3.7.5 failed"
        return 1
    fi
	sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/bin/pip3.7.5
	if [[ $? -ne 0 ]];then
        echo "sudo ln -s /usr/local/python3.7.5/bin/pip3 /usr/bin/pip3.7.5 failed"
        return 1
    fi

	return 0
}

function CheckPythonEnvironment() {
    pip_flag=`pip3.7.5  --version 2>/dev/null`
    python_flag=`python3.7.5  --version 2>/dev/null`
    if [[ -n "${pip_flag}" ]] && [[ -n "${python_flag}" ]];then
		response=""
		while [[ ${response}"X" == "X" ]];do
			read -p "python3.7.5 and pip3.7.5 have been installed , do you want to reinstall python3.7.5 ?. [Y/N]. default option is N: " response
			if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ] || [ $response"z" = "z" ]; then

				checkandinstall_python3_lib
				if [ $? -ne 0 ];then
					echo "python3.7.5 libs install failed! "

					echo "Now reinstalling python3.7.5 "
		
					install_python3.7.5
					if [ $? -ne 0 ];then
						echo "reinstall python3.7.5 failed"
						return 1
					fi
	
					checkandinstall_python3_lib
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

				checkandinstall_python3_lib
				if [ $? -ne 0 ];then
					echo "installing python libs failed"
					return 1
				fi
			else
				response=""
				echo "[ERROR] Please input Y/N!"
			fi
		done
    else

        install_python3.7.5
        if [ $? -ne 0 ];then
            echo "install python3.7.5 failed"
            return 1
        fi

        checkandinstall_python3_lib
        if [ $? -ne 0 ];then
            echo "install python libs failed"
            return 1
        fi
    fi
    return 0
}
CheckPythonEnvironment

