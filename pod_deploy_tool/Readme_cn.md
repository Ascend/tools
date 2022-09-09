# pod_deploy_tool工具
## 概述
该工具实现在Atlas 500和Atlas 500Pro设备后台部署容器，并支持在FD上迁移。

## 约束
- 该工具只支持部署单pod单容器。
- 该工具部署容器不支持附加文件、模型文件。
- 该工具在纳管为FD网管模式后，不支持操作容器。
- 该工具需使用root用户执行。
- 使用该工具部署容器，需在设备上提前加载对应容器镜像。
- 该工具需配套MindX Edge使用，支持配套MindX Edge 2.0.3及以后的版本

## 前置条件
1. MindX Edge已安装运行。

## 目录文件说明
1. pod_deploy.sh: 命令执行执行入口脚本
2. pod_deploy.py: 解析pod配置文件信息，建立mqtt客户端将操作信息发送给edge_core进行处理
3. pod.yaml: pod示例配置文件，用户根据需要自行修改
4. README.md: 帮助指导


## 工具使用方法
1. 获取工具脚本，存放在环境任意目录下
2. 部署或删除容器执行命令如下：
```
bash pod_deploy.sh --work_dir={AtlasEdgeWorkDir} --operate={Operation} --pod_file={PodConfigFile}
```
参数说明如下：
* AtlasEdgeWorkDir: 中间件运行路径
* Operation: pod部署或删除操作，取值create或delete
* PodConfigFile: pod配置文件绝对路径，配置文件中metadata name字段格式为：实例名-uuid4

3. 容器部署或删除后使用docker ps命令查看容器是否执行成功
