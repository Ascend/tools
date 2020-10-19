## atlasboost
[TOC]
### 产品介绍
atlasboost提供了如下功能：
(1) 一键式地启动单机或多机上的训练脚本，并行执行训练任务；
(2) 自动收集参与训练的device信息，生成rank table file；
(3) 通过mpi重定向功能，可实时的监控训练过程；

### 目录结构
源代码的目录结构如下：
```
.
├── atlasboost
│   ├── common
│   │   ├── bin
│   │   ├── CMakeLists.txt
│   │   ├── context.cpp
│   │   ├── context.h
│   │   ├── control.cpp
│   │   ├── control.h
│   │   ├── json.cpp
│   │   ├── json.h
│   │   ├── operations.cpp
│   │   └── operations.h
│   └── tensorflow
│       ├── basics.py
│       ├── __init__.py
│       └── mpi_ops.py
├── build
│   ├── build.sh
|   ├── compile.sh
|   ├── compile_for_ci.sh
|   └── openmpi_setup.sh
├── config
├── lib
├── doc
├── opensource
├── output
├── README.md
└── test
    ├── mpi_local.sh
    ├── mpi.sh
    └── test_tensorflow.py
```
目录结构说明如下：
(1) atlasboost: 用户在训练python脚本中导入的模块；
(2) common: C++源代码，用于收集device信息，生成rank table file；
(3) tensorflow: 支持tensorflow框架，设置环境变量，对外提供python接口；
(4) build: 编译脚本，用于编译common中的C++源代码；
(5) test: 测试脚本，可用于测试运行环境；
### 支持的产品
Ascend 910
### 支持的版本

### atlasboost引入
（1）按照目录结构放入到一个公共的目录中,比如当前服务器创建一个目录public,把以上目录结构放到public中，则通过修改PYTHONPATH=$PYTHONPATH:./public/,外部就可以使用atlasboot接口了。
（2）通过执行./setup --path dir(可选，root用户的默认目录是/usr/local/atlasboost,非root用户默认目录是/home/username/atlasboost),则会在默认路径或者dir目录下创建atlasboost文件夹,把安装的内容放在此目录下,若dir/atlasboost已经存在,则会有交互提示(是否继续在此目录下安装,请输入y/n),输入y则会覆盖此目录下重名的文件,输入n则会退出安装。

### 环境依赖
atlasboost依赖于开源库Open MPI和Ascend 910软件中的DSMI接口；
(1) 安装Open MPI
下载4.0.2版本的Open MPI，下载地址：
https://www.open-mpi.org/software/ompi/v4.0/
解压
```
tar -jxvf openmpi-4.0.2.tar.bz2
```
配置，编译和安装
```
./configure
make && make install
```
使配置生效
```
ldconfig
```
测试
```
mpirun --version
```
(2) DSMI
atlasboost中调用DSMI接口获取device的相关信息，编译脚本compile.sh内容如下：
```
#!/bin/bash

export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:/usr/local/Ascend/driver/kernel/inc/driver
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/Ascend/driver/lib64/driver

CUR_DIR=$(dirname $(readlink -f $0))
cd ${CUR_DIR}/../atlasboost/common
echo 2 > /proc/sys/kernel/randomize_va_space
cmake .
make
```
其中CPLUS_INCLUDE_PATH和LIBRARY_PATH分别指定了DSMI头文件和对应的动态链接库路径。
### 使用说明
提示：由于通过gethostbyname获取服务器IP，故需要配置host。
#### 1.单机环境测试
将源代码在服务器上解压，然后编译：
```
cd atlasboost/build
./compile.sh
```
然后执行atlasboost/test目录下的测试脚本：
```
./mpi_local.sh
```
该测试程序创建了4条进程，分别收集了服务器上device0到device3的信息，在atlasboost/test生成一份rank_table_file，检查一下该文件中信息是否正确。
#### 2.单机多卡训练
将atlasboost文件夹复制到训练脚本中(只要Python导入模块时能找到) ，在python的启动脚本中导入atlasboost模块：
```
import atlasboost.tensorflow.mpi_ops as atlasboost
```
在python的启动脚本开始时调用atlasboost接口，在main函数中添加如下代码：
```
初始化时传入支持的框架(tensorflow或者mindspore)，默认是tensorflow.
atlasboost.init(frame="tensorflow") 
device_id = atlasboost.local_rank()
atlasboost. set_device_id (device_id)
```
提示：若非mpi启动训练任务请不要调用以上接口,并且同一台机器上的device_id不要相同。
atlasboost模块初始化之后，每条进程会动态生成一个进程id，若在一台服务器上创建了n条进程，则进程id分别为0到n-1，用户需要根据进程id为每条进程分配一个device(process_id映射到device_id)，可直接使用进程id作为device id，如上所示。
执行命令启动训练脚本：
```
mpirun -np 8 -bind-to none -map-by slot --allow-run-as-root ./start.sh
```
其中，-np参数指定启动进程个数，该命令在当前服务器上启动8条进程，start.sh为模型的启动脚本， atlasboost模块会在当前目录为每一台服务器创建rank_table_file，文件在启动目录中。
#### 3.多机环境部署与测试
首先在每台参与训练的服务器中进行单机环境测试；
在多机环境下使用atlasboost，需要配置启动训练服务器到其他参与训练服务器SSH免密登录；
在启动服务器生成公钥：
```
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
```
将启动服务器的公钥发送到其他每台服务器
测试：
```
ssh xx.xx.xx.xx
```
若免密登录配置成功，则可直接使用SSH登录到xx.xx.xx.xx。
在每台服务器的相同位置保存一份atlasdc，若OS属于不同的CPU架构(arm或X86)，需要重新编译；在启动服务器中，切换到atlasdc/test目录下，配置mpi.sh脚本：
```
#!/bin/bash

mpirun -H xx.xx.xx.xx:2,xx.xx.xx.xx:4 \
       --allow-run-as-root \
       --mca btl_tcp_if_exclude lo,docker0,endvnic \
       python3 test_tensorflow.py
```
该脚本为在多台服务器上同时启动多条进程的命令，其中-H参数指定了启动哪些服务器上的test_tensorflow.py脚本以及每台服务器上启动几条进程，其中冒号后数值即为在该服务器上启动进程数，根据自己的环境进行配置。
执行测试脚本：
```
./mpi.sh
```
若多机环境正常，则会在每台服务器的atlasboost/test目录下生成进程的工作目录，工作目录中生成了rank table file。
#### 4.多机多卡训练
训练脚本经过单机多卡分布式部署的配置之后，将训练脚本复制到每台参与训练服务器的相同位置，然后执行如下命令：
```
mpirun -H xx.xx.xx.xx:8,xx.xx.xx.xx:8 \
       --allow-run-as-root \
       -bind-to none -map-by slot \
       --mca btl_tcp_if_exclude lo,docker0,endvnic \
       ./mpi_start.sh
```
该命令在每台服务器上都启动了8条进程进行训练，每台服务器都生成了rank_table_file，其中--mca btl_tcp_if_exclude参数用于限制tcp通信时使用的网卡(不使用lo,docker0,endvnic)。

