# tfdbg_ascend

## 环境准备

> 要求系统安装了[pybind11](https://github.com/pybind/pybind11) ，同时系统满足以下要求：

- Linux OS
- GCC >= 7.3.0
- CMake >= 3.14.0

## 安装

### 从源码安装

您可以从源代码构建 tfdbg_ascend 软件包并将其安装在GPU或CPU的AI计算环境上。
> tfdbg_ascend 与 Tensorflow 有严格的匹配关系，从源码构建前，您需要确保已经正确安装了[Tensorflow v2.4 或 V2.6 版本](https://www.tensorflow.org/install) 。

#### 下载源码

```
git clone https://github.com/Ascend/tools.git
cd tools/tfdbg_ascend
```

#### 配置安装环境

```BASH
./configure
```

默认情况下，执行上述命会弹出如下的交互式会话窗口
> 您的会话可能有所不同。

```BASH
Please specify the location of python with available tensorflow v2.4/v2.6 site-packages installed. [Default is /usr/bin/python3]
(You can make this quiet by set env [ADAPTER_TARGET_PYTHON_PATH]):
```

此时，要求您输入安装了 Tensorflow v2.4或者v2.6 版本的python解释器路径，如果默认路径是正确的，直接回车，否则请输入正确的 python 解释器路径。
> 您可以通过设置 ADAPTER_TARGET_PYTHON_PATH的环境变量，来抑制交互式窗口弹出，但是要确保路径是有效的，否则，仍然会要求您输入正确的 python 解释器路径。

键入后，会耗费几秒钟以确保您的输入是有效的，配置完成后会输出如下提示信息。
```BASH
Configuration finished
```

#### 配置cmake

> 根据您的网络状况，可能需要数分钟来下载tfdbg_ascend的依赖项目以完成配置。

```
mkdir build
cd build
cmake ..
```

#### 执行编译

> 您应当根据实际编译环境，设置合适的并发编译数以提升编译速度。

```BASH
make -j8
```

编译结束后，安装包会生成在

```
./dist/tfdbg_ascend/dist/tfdbg_ascend-0.2-py3-none-any.whl
```

#### 安装

您可以继续执行

```BASH
make install
```

将tfdbg_ascend安装到配置时指定的 python 解释器包目录下，或者使用 pip3 安装 tfdbg_ascend 到您期望的位置。

```
pip3 install ./dist/tfdbg_ascend/dist/tfdbg_ascend-0.2-py3-none-any.whl --upgrade --force-reinstall
```

#### 接口函数

接口函数用于dump过程的配置，如下：

| 函数                      | 描述                                       |
| ------------------------  | ---------------------------------------- |
|enable                     | 打开dump功能，无参数.                                                            |
|disable                    | 关闭dump功能，无参数.                                                            |
|get_dump_switch            | 获取dump使能开关的状态，无参数.                                                  |
|set_dump_path              | 用于设置dump文件的存放路径，函数参数为配置的路径名称，例如“/var/log/dump”.        |
|get_dump_path              | 获取当前配置的dump文件存放路径，返回值为该路径名称字符串.                         |

#### 使用示例

以训练场景为例，在你需要dump数据的step启动之前，设置使能开关和dump路径。
```
import tfdbg_ascend as tfdbg

tfdbg.enable()
tfdbg.set_dump_path('/var/log/dump/')
```

## 贡献

psuh代码前，请务必保证已经完成了基础功能测试和网络测试！

## Release Notes

Release Notes请参考[RELEASE](RELEASE.md).

## License

[Apache License 2.0](LICENSE)
