# edge_ability_tool 工具

## 功能描述
- AtlasEdge部分功能为可选特性，客户根据需要自行打开对应能力项，该工具实现对Web部署容器和模型文件下载能力配置

## 约束
- 该工具需配套MindX Edge使用，支持配套MindX Edge 2.0.4.6、3.0.RC2及以后的版本

## 前置条件
1. MindX Edge已安装运行。

## 工具使用说明
1. 以root用户登录设备执行如下命令修改文件属性

    ```chattr -i AtlasEdge软件安装路径/edge_work_dir/edge_om/package/edge_om/src/utils/high_risk/*.py```

2. 拷贝 site_high_risk_ops_cli.py

    ```cp -f site_high_risk_ops_cli.py AtlasEdge软件安装路径/edge_work_dir/edge_om/package/edge_om/src/utils/high_risk/ ```

3. 执行命令切换到入口脚本路径

    ```cd AtlasEdge软件安装路径/edge_work_dir/edge_om/bin/```

4. 根据需要使用以下命令：

    ```./site_ability_policy.sh disable_all --on 禁止能力项总开关打开，禁止所有能力项。```

    ```./site_ability_policy.sh allow op1 op2 开启能力项op1、op2。op的可选参数请参见表2。```

    ```./site_ability_policy.sh -h（或--h，-help，--help）显示主命令帮助信息。```

    ```./site_ability_policy.sh disable_all -h（或--help）显示disable_all子命令帮助信息。```

    ```./site_ability_policy.sh allow -h（或--help）显示allow子命令帮助信息。```


表1  disable_all子命令参数说明

| 参数   | 说明               |
|:-----|:-----------------|
| --on | 禁止能力项总开关，禁止所有能力项 |

### 关闭所有能力示例：

```./site_ability_policy.sh disable_all --on```

表2 allow子命令参数说明

| 参数                    | 说明           |
|:----------------------|:-------------|
| --create_container    | 开启Web部署容器能力项 |
| --download_model_file | 开启模型文件下载能力项  |

### 开启部署容器和模型文件能力示例：

 ```./site_ability_policy.sh allow --create_container --download_model_file```

5. 执行如下命令重启中间件使配置生效：
```
AtlasEdge软件安装路径/run.sh restart
```

----结束