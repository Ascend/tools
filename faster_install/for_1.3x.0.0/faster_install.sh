#!/bin/bash
main()
{
    echo "Build environment"

    echo "Current ddk-version list:"
    echo "1.1.31.T15.B150"
    echo "2.1.31.T20.B200"
    echo "3.1.32.0.B080"
    read -p "Please input your ddk-verison in this list(eg:1):" DDK_VERSION
    if [[ ! $DDK_VERSION ]]; then
        echo "[ERROR] Input empty,please input ddk-verison(eg:1)"
        return 1
    else
        if [[ $DDK_VERSION"z" = "1z" ]];then
            Version="1.31"
            DDK_VERSION="T15.B150"
        elif [[ $DDK_VERSION"z" = "2z" ]];then
            Version="1.31"
            DDK_VERSION="T20.B200"
        elif [[ $DDK_VERSION"z" = "3z" ]];then
            Version="1.32"
            DDK_VERSION="0.B080"
        else
            echo "[ERROR] Input ddk-version Error,Please check your input"
            return 1
        fi
    fi
    
    sudo apt-get update
    if [[ $? -ne 0 ]];then
        echo "[ERROR] Please check if the network is connected or Check if the sources in /etc/apt/sources.list are available"
        return 1
    fi

    C31_flag=`find $HOME -maxdepth 1 -name "MindStudio-ubuntu" 2> /dev/null`
    if [[ $C31_flag ]];then
        read -p "[INFO] The Mindstudio is existence.Do you want to re-install ? [Y/N]: " response
        if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
            echo "Exit installation"
            return 1
        elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
            echo "[info] Please manually delete $HOME/MindStudio-ubuntu directorand re-execute this script"
            return 1
        else
            echo "[ERROR] Please input Y/N!"
            return 1
        fi
    fi

    package_flag=`find $HOME -maxdepth 1 -name "mindstudio.tar.gz" 2> /dev/null`
    if [[ ! $package_flag ]];then
        read -p "[INFO] can not get mindstudio.tar.gz in $HOME,Do you want download[Y/N]: " response
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
        
    DDK_flag=`find $HOME -maxdepth 1 -name "Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz" 2> /dev/null`
    if [[ ! $DDK_flag ]];then
        read -p "[INFO] can not get Ascend_DDK-${Version}.${DDK_VERSION} in $HOME,Do you want download[Y/N]: " response
        if [ $response"z" = "Nz" ] || [ $response"z" = "nz" ]; then
            echo "Exit installation"
            return 1
        elif [ $response"z" = "Yz" ] || [ $response"z" = "yz" ] || [ $response"z" = "z" ]; then
            DDK_Download="YES"
        else
            echo "[ERROR] Please input Y/N!"
            return 1
        fi
    fi
    
    if [[ $MIN_Download ]];then
        wget -O $HOME/mindstudio.tar.gz.asc "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/${DDK_VERSION}/mindstudio.tar.gz.asc"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/mindstudio.tar.gz.asc
            return 1
        fi
        wget -O $HOME/mindstudio.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/${DDK_VERSION}/mindstudio.tar.gz"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/mindstudio.tar.gz.asc
            rm -rf $HOME/mindstudio.tar.gz
            return 1
        fi
    fi

    if [[ $DDK_Download ]];then
        wget -O $HOME/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/${DDK_VERSION}/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz
            return 1
        fi
        wget -O $HOME/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz.asc "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/${DDK_VERSION}/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz.asc"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz
            rm -rf $HOME/Ascend_DDK-${Version}.${DDK_VERSION}-1.1.1-x86_64.ubuntu16.04.tar.gz.asc
            return 1
        fi
    fi
    
    dpkg -l xterm
    if [[ $? -ne 0 ]];then
        sudo apt-get install python python3 python-pip python3-pip
    else
        sudo apt-get install xterm python python3 python-pip python3-pip
    fi

    dpkg -l fonts-droid-fallback
    if [[ $? -ne 0 ]];then
        sudo apt-get install fonts-droid-fallback
    fi
    
    dpkg -l ttf-wqy-zenhei
    if [[ $? -ne 0 ]];then
        sudo apt-get install ttf-wqy-zenhei
    fi

    dpkg -l ttf-wqy-microhei
    if [[ $? -ne 0 ]];then
        sudo apt-get install ttf-wqy-microhei
    fi
 
    dpkg -l fonts-arphic-ukai
    if [[ $? -ne 0 ]];then
        sudo apt-get install fonts-arphic-ukai
    fi
 
    dpkg -l fonts-arphic-uming
    if [[ $? -ne 0 ]];then
        sudo apt-get install fonts-arphic-uming
    fi
    
    pip2 --version
    if [[ $? -ne 0 ]];then
        echo "[ERROR] Please check if pip2 is installed"
        return 1
    else
        if numpy_version=`python2 -c "import numpy;print(numpy.__version__)" 2>/dev/null`;then
            if [[ ${numpy_version} != "1.14.1" ]];then    
                pip2 install numpy==1.14 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
                if [[ $? -ne 0 ]];then
                    echo "[ERROR] pip2 install numpy faild ,Please manually install"
                    return 1
                fi
            fi
        else
            pip2 install numpy==1.14 --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
            if [[ $? -ne 0 ]];then
                echo "[ERROR] pip2 install numpy faild ,Please manually install"
                return 1
            fi
        fi
        decorator_version=`python2 -c "import decorator;print(decorator.__version__)"` 2>/dev/null`
        if [[ ! $decorator_version ]];then
            pip2 install decorator --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
            if [[ $? -ne 0 ]];then
                echo "[ERROR] pip2 install decorator faild ,Please manually install"
                return 1
            fi
        fi
    fi

    pip3 --version
    if [[ $? -ne 0 ]];then
        echo "[ERROR] Please check if pip3 is installed"
        return 1
    else
        numpy_version=`python3 -c "import numpy;print(numpy.__version__)" 2>/dev/null`
        if [[ ! $numpy_version ]];then
            pip3 install numpy --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
            if [[ $? -ne 0 ]];then
                echo "[ERROR] pip3 install numpy faild ,Please manually install"
                return 1
            fi
        fi
        decorator_version=`python3 -c "import decorator;print(decorator.__version__)"` 2>/dev/null`
        if [[ ! $decorator_version ]];then
            pip3 install decorator --user -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
            if [[ $? -ne 0 ]];then
                echo "[ERROR] pip3 install decorator faild ,Please manually install"
                return 1
            fi
        fi
    fi
    
    java -version
    if [[ $? -ne 0 ]];then
        sudo apt-get install -y openjdk-8-jdk
        java -version
        if [[ $? -ne 0 ]];then
            echo "apt-get install JDK failed ,please check your environment"
            return 1
        fi
        java_home="/usr/lib/jvm/java-8-openjdk-amd64"
    else
        java_flag=`java -version 2>&1 | sed '1!d' | sed -e 's/"//g' | awk '{print $3}'`
        fstr=`echo $java_flag | cut -d \_ -f 1`
        sstr=`echo $java_flag | cut -d \_ -f 2`
        fstr1=`echo $fstr | cut -d \. -f 1`
        fstr2=`echo $fstr | cut -d \. -f 2`
        fstr3=`echo $fstr | cut -d \. -f 3`
        version_ok=1
        if [[ $fstr1 -ge 1 ]];then
            if [[ $fstr2 -ge 8 ]];then
                if [[ $fstr3 -ge 0 ]];then
                    if [[ $sstr -ge 171 ]];then
                        version_ok=0
                    fi
                fi
            fi
        fi
        if [[ ! $version_ok ]];then
            echo "[ERROR] The JDK is currently installed and the version number is lower than 1.8.0_171, please uninstall the current JDK and re-execute this script"
            return 1
        else
            java_path=`which java`
            java_home=`echo ${java_path%/bin/java*}`
            if [[ ! $java_home ]];then
                read -p "[INFO] Can not get your JDK path,Please manually input: " java_home
                find_result=`find $java_home -maxdepth 1 -name "jre" 2> /dev/null`
                if [[ ! $find_result ]];then
                    echo "[ERROR] Please input correct path"
                    return 1
                fi
            else
                find_result=`find $java_home -maxdepth 1 -name "jre" 2> /dev/null`
                if [[ ! $find_result ]];then
                    echo "[ERROR] your JDK path is Error,Please checking"
                    return 1
                fi
            fi
        fi
    fi
    grep -Fx "export JAVA_HOME=$java_home" $HOME/.bashrc >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "export JAVA_HOME=$java_home" >> $HOME/.bashrc
    fi
    grep -Fx "export PATH=\$JAVA_HOME/bin:\$PATH" $HOME/.bashrc >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> $HOME/.bashrc
    fi
    source $HOME/.bashrc
    
    java_echoflag=`echo $JAVA_HOME`
    if [[ ! $java_echoflag ]];then
        echo "[ERROR] JAVA_HOME Configuration failed,Please configure manually"
        return 1
    fi
    JDK_whichflag=`which jconsole`
    if [[ ! $JDK_whichflag ]];then
        echo "[ERROR] JDK Configuration failed,Please configure manually"
        return 1
    fi
    
    tar -zxvf $HOME/mindstudio.tar.gz -C $HOME 2> /dev/null
    if [[ $? -ne 0 ]];then
        echo "[ERROR] Unable to decompress mindstudio.tar.gz,please check your package"
        return 1
    fi
    
    bash $HOME/MindStudio-ubuntu/bin/MindStudio.sh
}

main
