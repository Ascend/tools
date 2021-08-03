# tfdbg_ascend

## 安装

### 从源码安装

您可以从源代码构建 tfdbg_ascend 软件包并将其安装在昇腾AI处理器环境上。
> tfdbg_ascend 与 Tensorflow 有严格的匹配关系，从源码构建前，您需要确保已经正确安装了[Tensorflow v2.4 版本](https://www.tensorflow.org/install) 。


同时系统满足以下要求：

- Linux OS
- GCC >= 7.3.0
- CMake >= 3.14.0

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
Please specify the location of python with available tensorflow v2.4 installed. [Default is /usr/bin/python3]
(You can make this quiet by set env [ADAPTER_TARGET_PYTHON_PATH]):
```

此时，要求您输入安装了 Tensorflow v2.4 版本的python解释器路径，如果默认路径是正确的，直接回车，否则请输入正确的 python 解释器路径。
> 您可以通过设置 ADAPTER_TARGET_PYTHON_PATH的环境变量，来抑制交互式窗口弹出，但是要确保路径是有效的，否则，仍然会要求您输入正确的 python 解释器路径。

键入后，会耗费几秒钟以确保您的输入是有效的，接着，会弹出下面的交互式窗口

```
Please specify the location of ascend. [Default is /usr/local/Ascend]
(You can make this quiet by set env [ASCEND_INSTALLED_PATH]):
```

此时，要求您输入昇腾处理器开发套件的安装路径，如果默认路径是正确的，直接回车，否则请输入正确的昇腾处理器开发套件安装路径。

> 您可以通过设置ASCEND_INSTALLED_PATH的环境变量，来抑制交互式窗口弹出，但是要确保路径是有效的，否则，仍然会要求您输入正确的昇腾处理器开发套件安装路径。

键入后，等待配置完成。

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
./dist/tfdbg_ascend/dist/tfdbg_ascend-0.1-py3-none-any.whl
```

#### 安装

您可以继续执行

```BASH
make install
```

将tfdbg_ascend安装到配置时指定的 python 解释器包目录下，或者使用 pip3 安装 tfdbg_ascend 到您期望的位置。

```
pip3 install ./dist/tfdbg_ascend/dist/tfdbg_ascend-0.1-py3-none-any.whl --upgrade
```

## 贡献

psuh代码前，请务必保证已经完成了基础功能测试和网络测试！

## Release Notes

Release Notes请参考[RELEASE](RELEASE.md).

## License

[Apache License 2.0](LICENSE)
