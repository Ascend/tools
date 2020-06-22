**此工具为模型推理工具**





功能：输入.om模型和模型所需要的输入bin文件，输出模型的输出数据文件



模型必须是通过c7x版本的atc工具转换的om模型，输入bin文件需要符合模型的输入要求



工具为命令行的运行方式，例如

*./amexec --model /home/HwHiAiUser/ljj/colorization.om --input /home/HwHiAiUser/ljj/colorization_input.bin --output /home/HwHiAiUser/ljj/AMEXEC/out/output1 --outfmt TXT --loop 2*

需要注意的是这几个参数的顺序不能颠倒，outfmt与loop为可选参数，默认值分别有BIN、1。其他参数详情可使用--help查询。



运行工具的用户在当前目录需要有创建目录以及执行工具的权限，使用前请自行检查。

dump、profiling以及动态多batch功能暂不支持。