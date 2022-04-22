
# 使用 ada 安装 run包

## 注意！！如果使用 venv 安装了 ada

如果你使用 virtualenv 安装了 ada，需要额外注意的是，不可以在 venv 中直接运行 ada：

```shell
(venv) $ ada ...
```

这是当前 run 包安装的一个坑，如果在 venv 下安装 run 包，会导致 run 包中的 python packages 被安装到 venv 的 path 下。
然而在执行训练/推理脚本时，会从 `/usr/local/Ascend` 也就是 run 包的安装目录下面查找 python package，这就导致了执行脚本时找不到对应的 python 包。

因此，如果使用 venv 安装了 ada，最佳实践是使用如下方法执行 ada：

在 `/usr/local/bin` 或者任何一个在执行 PATH 的目录中新增一个 ada 文件，里面的内容如下所示：

```shell
#! /bin/bash
/path/to/venv/bin/python -m ada_cmd $*
```

退出 venv 正常执行 ada，此时实际会执行此ada脚本，从而规避上述问题。

## 安装 newest

在调试环境上，使用如下命令安装 atc, acllib, fwkacllib, opp 共四个 newest 包：

```shell
# ada -n atc,acllib,fwkacllib,opp -i
```

输入以上命令后，`ada` 会从 CI 上查找最新的 newest 包，并将其下载到当前目录，然后执行安装，其回显如下所示：

```shell
# ada -n atc,acllib,fwkacllib,opp -i
Begin to download newest run packages from 20211011_001128053_newest
Begin to download Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run to ./ ...... Done.
Begin to download Ascend-opp-1.79.t30.0.b300-ubuntu18.04.x86_64.run to ./ ...... Done.
Begin to download Ascend-acllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run to ./ . Done.
Begin to download Ascend-fwkacllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run to ./ ....... Done.
Begin to install package ./Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run ............................ Done.
Install package ./Ascend-atc-1.79.t30.0.b300-ubuntu18.04.x86_64.run success([Atc] [2021-10-11 17:46:31] [INFO]: Atc package install success! The new version takes effect immediately.)
Begin to install package ./Ascend-opp-1.79.t30.0.b300-ubuntu18.04.x86_64.run .................. Done.
Install package ./Ascend-opp-1.79.t30.0.b300-ubuntu18.04.x86_64.run success([Opp] [2021-10-11 17:46:53] [INFO]: Opp package install success! The new version takes effect immediately.)
Begin to install package ./Ascend-acllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run .... Done.
Install package ./Ascend-acllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run success([Acllib] [2021-10-11 17:46:57] [INFO]: Acllib package install success! The new version takes effect immediately.)
WARNING:root:try to install package fwkacllib, delete site-packages first
Begin to install package ./Ascend-fwkacllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run ............................ Done.
Install package ./Ascend-fwkacllib-1.79.t30.0.b300-ubuntu18.04.x86_64.run success([Fwkacllib] [2021-10-11 17:47:20] [INFO]: Fwkacllib package install success! The new version takes effect immediately.)
```

## 安装自编译的包

`ada` 也可以被用来安装自己编译的包，例如自行编译了 atc 和 opp 两个包，并希望做安装，命令示意为：

```shell
# ada -c 20211009_162917537_If6be636,atc,opp -i
```

需要注意的是，此时指定包的选项变为`-c`，并且后面跟的参数中，第一个参数代表了自编译包的路径，这个路径可以通过如下两种方式获得：

**方式1，通过编译包的路径**

打开编译包所在的 CI 页面，网址中如下一段便是此名字：

![](res/compile_package_page.PNG)    TODO: 补一张图

**方式2，通过编译时间推断**

在 CI 的构建历史页面中，会显示一个构建时间，此时间拼接上 change-id 的前 8 位，便是这个名字：

![](res/compile_package_history.PNG)    TODO: 补一张图
