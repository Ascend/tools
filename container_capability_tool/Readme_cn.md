# container_capability_tool工具
## 背景
原生Kubeedge支持特权容器、主机网络、root运行、主机挂载卷等容器高危险能力，AtlasEdge在商用软件
中对这些容器危险能力进行了限制，通过配置文件对这些能力进行了限制，通过修改配置文件可支持，可实现开源
原生Kubeedge容器部署能力，但开放这些能力存在安全风险(如容器逃逸)，请慎用并确保使用场景安全可信。

**免责声明**：若客户开放了Kubeedge这些高危险能力造成安全问题，与AtlasEdge商用软件无关。

## 约束
- 该工具需配套MindX Edge使用，支持配套MindX Edge 2.0.4.6及以后的版本

## 前置条件
1. MindX Edge已安装运行。

## 目录文件说明

1. modify_pod_config_cmd_executor.py: 提供执行shell命令的能力
2. modify_pod_config_item.py: 提供对容器开关参数的校验,修改方法
3. modify_pod_config_json.py: 修改容器危险能力开关程序入口
4. README.md: 帮助指导


## 工具使用方法
1. 获取工具脚本，并存放于{AtlasEdgeWorkDir}/edge_core/src/目录下，其中{AtlasEdgeWorkDir}为中间安装目录
2. 部署或删除容器执行命令如下：
```
python3 /opt/middleware/AtlasEdge/edge_work_dir/edge_core/src/modify_pod_config_json.py \
--useSecuritySetting=true \
--checkImageSha256=true \
--useCapability=false \
--usePrivileged=false \
--usePrivilegeEscalation=false \
--useRunAsRoot=false \
--useProbe=false \
--useStartCommand=false \
--useHostNetwork=false \
--useSeccomp=false \
--useDefaultContainerCap=false \
--setRootFsReadOnly=true \
--emptyDirVolume=false \
--containerCpuLimit=2.0 \
--containerNpuLimit=1.0 \
--containerMemoryLimit=2048 \
--maxContainerNumber=16 \
--totalModelFileNumber"=512 \
--containerModelFileNumber=48 \
--systemReservedCPUQuota=1.0 \
--systemReservedMemoryQuota=1024 \
--
imageSha256WhiteList=sha256:1f082f05a7fc20f99a4ccffc0484f45e6227984940f2c57d8617187b44fd5c46,sha256:b0b140824a486ccc0f7968f3c6ceb6982b4b77e82ef8b4faaf2806049fc266df \
--
addHostPath=/var/lib/docker/modelfile/,/var/lib/docker/modelfile/ \
--
deleteHostPath=/var/lib/docker/modelfile,/var/lib/docker/modelfile/ \
其中 /opt/middleware/AtlasEdge/edge_work_dir/edge_core/src/ 为配置脚本绝对路径,配置脚本为必选参数,用户请根据实际AtlasEdge安装目录进行修改。
```
参数说明如下：
* useSecuritySetting:取值true or false,默认配置为true。true表示进行容器安全校验,false不进行容器安全校验。修改为false有较大安全风险,建议设置为true。
* checkImageSha256: 取值true or false,默认配置为true。true表示进行容器镜像sha256校验,false表示不进行校验。修改为false会允许任意容器部署,有较大的安全风险,建议设置为true。
* useCapability: 取值true or false,默认配置为false。true表示允许容器配置能力项,false表示不支持容器配置能力项。修改为true有较大安全风险,建议设置为false。
* usePrivileged: 取值true or false,默认配置为false。true表示允许容器以特权模式运行,false表示不支持容器以特权模式运行。修改为true有较大安全风险,建议设置为false。
* usePrivilegeEscalation: 取值true or false,默认配置为false。true表示允许容器使用特权提升,false表示不运行容器使用特权提升。修改为true有较大安全风险,建议设置为false。
* useRunAsRoot: 取值true or false,默认配置为false。true表示允许容器以root用户运行,false表示不允许容器以root用户运行,普通用户的容器可运行。修改为true有较大安全风险,建议设置为false。如果设置为false且使用容器自带的用户运行时,自带用户必须为数字uid和gid。
* useProbe: 取值true or false,默认配置为false。true表示允许容器使用探针,false表示不允许容器使用探针。修改为true有较大安全风险,建议设置为false。
* useStartCommand: 取值true or false,默认配置为false。true表示允许容器使用启动命令,false表示不允许容器使用启动命令。修改为true有较大安全风险,建议设置为false。
* useHostNetwork：取值true or false,默认配置为false。true表示允许容器使用主机网络,false表示不允许容器使用主机网络。修改为true有较大安全风险,建议设置为false。
* useSeccomp: 取值true or false,默认配置为false。true表示允许容器使用自定义的Seccomp配置,false表示不允许使用自定义的Seccomp配置。如果为false,下发的容器会使用默认的Seccomp。
* imageSha256WhiteList: 取值类型为String。以字符串形式导入容器镜像sha256白名单,字符串内使用英文逗号分割容器镜像sha256值,每个容器镜像sha256值需要以sha256:为前缀,容器镜像sha256为容器引擎为镜像生成的64个字节的哈希值。单次最多导入8个容器镜像sha26白名单,总数不超过128个。
* useDefaultContainerCap: 取值true or false,默认配置为false。true表示可以使用Docker默认的14项能力,false表示不可使用Docker默认的14项能力。
* setRootFsReadOnly: 取值true or false,默认配置为true。true表示设置容器的根文件系统挂载为只读模式,false表示设置文件的根文件系统挂载为读写模式,建议设置为true。
* emptyDirVolume: 取值true or false,默认配置为false。true表示支持配置emptyDir挂载卷的容器,false表示不支持配置emptyDir挂载卷的容器,建议设置为false。
* containerCpuLimit: 取值类型为float。默认配置为2.0。表示单个容器需要使用的CPU资源上限,取值为单位时间内占用CPU核心的时间片份额,取值范围为[0.01,100.0]。
* containerNpuLimit: 取值类型为float。默认配置为1.0。表示单个容器需要使用的NPU资源上限,取值为单位时间内占用NPU核心的时间片份额,取值范围为[0,100.0]。
* containerMemoryLimit: 取值类型为int。默认配置为2048。表示单个容器需要使用的内存资源上限,单位为MB,取值范围为[4,65536]。
* addHostPath: 取值类型为String。以字符串形式导入主机挂载目录或文件白名单,多个主机挂载目录或文件须用英文逗号分隔,输入的每个目录或文件须以"/"开头以确保为绝对路径或处于绝对路径下，目录结尾需要带"/",文件结尾不带"/"。该命令无法与deleteHostPath命令同时执行。单个hostPath字符串长度不超过1024,最多添加256个。
* deleteHostPath: 取值类型为String。以字符串形式删除主机挂载目录或文件白名单,多个主机挂载目录或文件须用英文逗号分隔,输入的每个目录或文件应在白名单内,否则报错,同时应以"/"开头以确保为绝对路径或处于绝对路径下,目录结尾需要带"/",文件结尾不带"/"。该命令无法与addHostPath命令同时执行。
* maxContainerNumber: 取值类型为int。默认配置为16。表示设备上允许配置的最大容器个数,最多不超过128个。可配置的configmap个数为最大允许容器个数的4倍。
* totalModelFileNumber: 取值类型为int。默认配置为512。表示模型文件总量:默认配置为512,最大配置不超过2048。
* containerModelFileNumber: 取值类型为int。默认配置为48。单个容器的模型文件数量:默认配置为48,最大不超过模型文件总量的配置。
* systemReservedCPUQuota: 取值类型为float。默认配置为1.0。系统预留CPU资源,默认为系统预留1个CPU核心,其余CPU资源用于应用部署。取值范围[0.5,4.0]。
* systemReservedMemoryQuota: 取值类型为int。默认配置为1024。系统预留内存资源,默认为系统预留1024MB,其余内存资源用于应用部署。取值范围[512,4096]。

## 提示
关闭useSecuritySetting校验或者打开capability、privileged、allowPrivilegeEscalation、runAsRoot、probe、startCommand、useHostNetwork、useDefaultContainerCap等选项或关闭setRootFsReadOnly、checkImageSha256等选项,可能会有容器逃逸或系统资源受损的风险。