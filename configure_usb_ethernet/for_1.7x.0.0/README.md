# configure_usb_ethernet(for_1.7x.0.0)

1. 下载脚本。   
	在本地环境普通用户（以HwHiAiUser用户为例）的$HOME目录下执行以下命令，下载tools仓代码。  
	**git clone https://gitee.com/ascend/tools.git**    
	（注：如果没有安装git，执行sudo apt-get install git 安装git）  

	执行以下命令，进入1.7x配置脚本目录。  
	**cd $HOME/tools/configure_usb_ethernet/for_1.7x.0.0/**  
	
2. 切换root用户。    
    **su root**
 
3. 执行如下命令进行USB网卡IP地址的配置。  
    **bash configure_usb_ethernet.sh -s ip_address**      
    以指定的IP地址配置Ubuntu服务器中USB网卡的静态IP地址，如果直接执行bash configure_usb_ethernet.sh，则以默认IP地址“192.168.1.166”进行配置。     
    
    - 注：如果存在多个USB网卡，则首先执行ifconfig命令查询USB网卡名称（若系统中有多个USB网卡，可以通过拔插开发者板进行判定，Ubuntu服务器会将Atlas 200 DK开发者板识别为虚拟USB网卡），再执行如下命令配置指定网卡的IP地址。    
        **bash configure_usb_ethernet.sh -s usb_nic_name ip_address**   
        usb_nic_name：USB网卡名称。
        ip_address：配置的IP地址。
        命令示例，配置Ubuntu服务器的USB网卡IP为192.168.1.223：    
        **bash configure_usb_ethernet.sh -s enp0s20f0u8 192.168.1.223**

    配置完成后，可执行ifconfig命令查看IP是否生效。