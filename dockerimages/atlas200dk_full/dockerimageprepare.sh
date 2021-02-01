#!/bin/bash
main()
{
    DDK_flag=`find $HOME/dockerimages/atlas200dk_full -maxdepth 1 -name "Ascend_DDK-1.32.0.B080-1.1.1-x86_64.ubuntu16.04.tar.gz" 2> /dev/null`
    if [[ ! $DDK_flag ]];then
        echo "Downloading Ascend_DDK, please waiting..."
        wget -O $HOME/dockerimages/atlas200dk_full/Ascend_DDK-1.32.0.B080-1.1.1-x86_64.ubuntu16.04.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/0.B080/Ascend_DDK-1.32.0.B080-1.1.1-x86_64.ubuntu16.04.tar.gz"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/dockerimages/atlas200dk_full/Ascend_DDK-1.32.0.B080-1.1.1-x86_64.ubuntu16.04.tar.gz
            return 1
        fi
    fi
    mindstudio_flag=`find $HOME/dockerimages/atlas200dk_full -maxdepth 1 -name "mindstudio.tar.gz" 2> /dev/null`
    if [[ ! $mindstudio_flag ]];then
        echo "Downloading mindstudio, please waiting..."
        wget -O $HOME/dockerimages/atlas200dk_full/mindstudio.tar.gz "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/0.B080/mindstudio.tar.gz"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/dockerimages/atlas200dk_full/mindstudio.tar.gz
            return 1
        fi
    fi
    runpackage_flag=`find $HOME/dockerimages/atlas200dk_full -maxdepth 1 -name "mini_developerkit_1.32.0.B080.rar" 2> /dev/null`
    if [[ ! $runpackage_flag ]];then
        echo "Downloading developerkitpackage, please waiting..."
        wget -O $HOME/dockerimages/atlas200dk_full/mini_developerkit_1.32.0.B080.rar "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/0.B080/mini_developerkit_1.32.0.B080.rar"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/dockerimages/atlas200dk_full/mini_developerkit_1.32.0.B080.rar
            return 1
        fi
    fi
    runpackageasc_flag=`find $HOME/dockerimages/atlas200dk_full -maxdepth 1 -name "mini_developerkit_1.32.0.B080.rar.asc" 2> /dev/null`
    if [[ ! $runpackage_flag ]];then
        echo "Downloading ascdeveloperkitpackage, please waiting..."
        wget -O $HOME/dockerimages/atlas200dk_full/mini_developerkit_1.32.0.B080.rar.asc "https://mindstudio--ddk.obs.cn-north-1.myhuaweicloud.com/0.B080/mini_developerkit_1.32.0.B080.rar.asc"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/dockerimages/atlas200dk_full/mini_developerkit_1.32.0.B080.rar.asc
            return 1
        fi
    fi

    make_sd_card_flag=`find $HOME/dockerimages/atlas200dk_full -maxdepth 1 -name "make_sd_card.py" 2> /dev/null`
    if [[ ! $make_sd_card_flag ]];then
        echo "Downloading make_sd_card.py, please waiting..."
        wget -O $HOME/dockerimages/atlas200dk_full/make_sd_card.py "https://obs-book.obs.cn-east-2.myhuaweicloud.com/liuyuan/make_sd_card.py"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/dockerimages/atlas200dk_full/make_sd_card.py
            return 1
        fi
    fi

    make_ubuntu_flag=`find $HOME/dockerimages/atlas200dk_full -maxdepth 1 -name "make_ubuntu_sd.sh" 2> /dev/null`
    if [[ ! $make_ubuntu_flag ]];then
        echo "Downloading make_ubuntu_sd.sh, please waiting..."
        wget -O $HOME/dockerimages/atlas200dk_full/make_ubuntu_sd.sh "https://obs-book.obs.cn-east-2.myhuaweicloud.com/liuyuan/make_ubuntu_sd.sh"  --no-check-certificate --quiet
        if [ $? -ne 0 ];then
            echo "ERROR: download failed, please check Network."
            rm -rf $HOME/dockerimages/atlas200dk_full/make_ubuntu_sd.sh
            return 1
        fi
    fi
}
main
