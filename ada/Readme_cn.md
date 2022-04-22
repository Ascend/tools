# Ascend Debugging Assistant (ADA)

## 介绍

`ada` 的目标是帮助 Ascend 开发者完成一些黄区 debug 时的重复或等待工作。当前 `ada` 支持如下功能：

* [从 CI 上下载 run  包，并将其在环境上安装](doc/ada_install.md)
* [解析GE profiling的dump结果，生成分析报告](doc/ada_pa.md)

欲求详细使用方法，请点击上文链接。

## 安装

当前 `ada` 仅支持在黄区安装和使用，在希望使用 `ada` 的环境上，使用 `pip` 来安装 `ada`：

```shell
pip install -U --trusted-host 10.29.78.105 -f http://10.29.78.105:8081/pypi/ ada
```

> 注：`ada` 仅支持 `Python3`

安装完成后，可以使用 `ada` 和 `ada-pa` 命令了：

```shell
$ ada
ada     ada-pa  

$ ada
No packages to download, you must specify one package to download at least

$ ada-pa
usage: ada-pa [-h] [-o OUTPUT] [--reporter REPORTER] input_file
ada-pa: error: the following arguments are required: input_file
```

PS: 为了避免对全局环境的污染，可以考虑使用venv环境来安装ada。

## 问题反馈

`ada` 工具内部开源，可以在如下 repo 中查看源码和提交 issue

`https://codehub-y.huawei.com/s00538840/ada/home`

## 开发者

如果你对ada感兴趣，希望对其做加强，可以查看其开发者文档：

* [ada-pa设计](doc/ada_pa_dev.md)
