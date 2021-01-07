  **介绍**

Ascend Tools，欢迎各位开发者！

 **贡献要求**

开发者提交的工具至少包括源码、readme，并遵循以下标准。

请贡献者在提交代码之前签署CLA协议，“个人签署”，[链接](https://clasign.osinfra.cn/sign/Z2l0ZWUlMkZhc2NlbmQ=)。

 **一、源码**

1. 工具的源码需符合第五部分编码规范。

2. 工具提交样例规范请参考[sample](https://gitee.com/ascend/tools/tree/master/msame)。

3. 贡献者工程代码目录规则：目录名即为工具名，需能体现出工具的作用。   
    
4. 从其他开源迁移的代码，请增加License声明。

 **二、License规则**

所有源码文件(cpp、py、hpp文件)需要支持Apache 2.0 License，并在源码文件头部增加声明，如下所示。
```
# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```
如果源码中已有其它公司的Copyright，请在上面增加一行华为的Copyriht，如下所示。
```
# Copyright 2020 Huawei Technologies Co., Ltd
# Copyright 2018 hisillion Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

 **三、readme**

readme用于指导用户理解和使用工具，要包含如下内容：

1. 简介：

    工具的功能、运行所依赖的环境、使用方法。

2. 关键要求：

    1. 如工具只支持特定的版本请注明；   
    2. 环境变量设置，依赖的第三方软件包和库，以及安装方法；   
    3. 工程文件获取方法：下载工程文件压缩包或是git clone；      
    4. 给出工具最常见的运作命令或运行步骤；  
    5. 工具的参数说明。   
    

 **四、PR提交规范**

1. 提交PR操作可以参考[如何fork仓库并提交PR_wiki](https://gitee.com/ascend/samples/wikis/%E5%A6%82%E4%BD%95fork%E4%BB%93%E5%BA%93%E5%B9%B6%E6%8F%90%E4%BA%A4PR?sort_id=3271318)。

2. 如需上传图片、视频、模型等大文件，请提供归档OBS、网盘链接或联系管理员存放到固定的obs地址，不要将大文件上传至tools仓中。

3. 提交PR后，码云会对代码做规范扫描和缺陷扫描，如存在问题，请修改。

4. 环境和其他问题，请提交Issue跟踪。



 **五、编程规范**

- 规范标准

    1. C++代码遵循google编程规范：[Google C++ Coding Guidelines](http://google.github.io/styleguide/cppguide.html)；单元测测试遵循规范： [Googletest Primer](https://github.com/google/googletest/blob/master/googletest/docs/primer.md)  

    2. Python代码遵循PEP8规范：[Python PEP 8 Coding Style](https://pep8.org/)；单元测试遵循规范： [pytest](http://www.pytest.org/en/latest/)

- 规范备注

    1. 优先使用string类型，避免使用char*；   
    2. 禁止使用printf，一律使用cout；   
    3. 内存管理尽量使用智能指针；   
    4. 不准在函数里调用exit；   
    5. 禁止使用IDE等工具自动生成代码；   
    6. 控制第三方库依赖，如果引入第三方依赖，则需要提供第三方依赖安装和使用指导书；   
    7. 一律使用英文注释，注释率30%--40%，鼓励自注释；   
    8. 函数头必须有注释，说明函数作用，入参、出参；   
    9. 统一错误码，通过错误码可以确认那个分支返回错误；   
    10. 禁止出现打印一堆无影响的错误级别的日志；   
    11. 注释的代码如果没有特别用处，全部删掉，严禁通过注释的方式删除无用代码；
