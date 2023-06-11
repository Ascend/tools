# Aicore Error分析工具

## 前置条件
1. 进行模型训练时，发现了Aicore Error问题。暂不支持推理场景。
2. 使用asys收集工具，收集aicore error时的日志信息。参考命令：
`asys launch --task="sh ../app_run.sh" [--output="path"]`
具体使用方法参见指导：http://turing-toolchain.msk.hisilicon.com/chapter-01/diagnosis_infer.html
3. 使用Aicore Error分析工具解析问题。

## 工具使用方法
1. 获取asys工具收集文件夹路径，例如：/home/root/asys_output_20230328160000000
2. 设置环境变量，参考命令：
`source /usr/local/Ascend/latest/bin/setenv.bash`
3. 下载[aicore error分析工具](https://github.com/Ascend/tools)，传输至运行环境目录下，以root为例，参考命令：
```
cd /home/root/tools/msaicerr
python3 msaicerr.py -p /home/root/asys_output_20230328160000000
```
> 可以使用命令：`python3 msaicerr.py -h`，查看具体参数的含义。
4. 针对aicore error，会生成相应的info.txt，开发者可根据info.txt进行异常分析。

## 概述
在执行训练发现AI Core error问题时，使用AI Core Error Analyzer工具可以自动快速准确地收集定位AI Core Error问题所需的关键信息，提升开发者对AI Core Error的排查效率。

## 约束
- 该工具当前不支持在容器中部署使用。
- 命令行部署该工具仅支持本地分析使用，即部署该工具的环境应该和日志所在环境为同一环境。
- 暂不支持推理场景。

## 问题分析和定位
本程序运行完毕，会打印/home/root/tools/msaicerr/info_{时间戳}/{aicore_{number}_{时间戳}/info.txt, 用户可以直接通过info.txt文件进行问题分析和定位。
关键信息说明：
```
***********************1. Basic information********************
# 本环节为aicore error的基本信息

error time   : 2022-03-05-17:30:51.327.642
device id    : 0
core id      : 0
task id      : 3
stream id    : 1
node name    : L2Loss
kernel name  : te_l2loss_0a9b2632fc2241e91c70b5a3ed5df7a95ba5024113b21f413c84e2bbb8171102_1

***********************2. AICERROR code***********************
# 本环节为aicore错误码以及代表的错误信息
code  : 0x800000
error bits : 
MTE_ERR_INFO: 0x600004a
    mte_err_type bit[26:24]=110  meaning:write bus error, 写请求时数据异常，例如安全访问请求访问了非安全的地址，非安全访问的请求访问了安全地址，访问请求收不到response、atomic运算异常(1980)
    mte_err_addr bit[22:8]=000000000000000  meaning:MTE Error Address [19:5]  approximate:0x0

***********************3. Instructions************************

# 本环节为aicore error发生的地址信息，并尽力去分析错误的cce行号与对应的算子行号

start   pc   : 0x1000120040026000
current pc   : 0x120040026968

Error occured most likely at line: 928

/home/root/tools/msaicerr/info_20220314203506/aicerror_0_20220305173051/te_l2loss_0a9b2632fc2241e91c70b5a3ed5df7a95ba5024113b21f413c84e2bbb8171102_1.o.txt:928
/home/root/tf/kernel_meta_21663_1646472642284609050/kernel_meta/te_l2loss_0a9b2632fc2241e91c70b5a3ed5df7a95ba5024113b21f413c84e2bbb8171102_1.cce:135

related instructions (error occured before the mark *):

     944: <not available>
     948: <not available>
     94c: <not available>
     950: <not available>
     954: <not available>
     958: <not available>
     95c: <not available>
     960: <not available>
     964: <not available>
*    968: <not available>

For complete instructions, please view /home/root/tools/msaicerr/info_20220314203506/aicerror_0_20220305173051/te_l2loss_0a9b2632fc2241e91c70b5a3ed5df7a95ba5024113b21f413c84e2bbb8171102_1.o.txt

****************4. Input and output of node*******************
# 本环节用于分析aicore error时用的地址是否越界。

# - 获取aicore error时input output的地址信息
# - 获取aicore error时系统分配的内存范围。
# - 检查input、output地址信息是否在地址范围内。若不在，则报错。

input[0] addr: 0x1202017a7000 end_addr:0x120202f4db00 size: 0x17a6b00
output[0] addr: 0x12004001d000 end_addr:0x12004001d004 size: 0x4
workspace_bytes:0

avaliable addrs:
start_addr            end_addr              size
0x120040010000        0x120040010200        0x200
0x120200000000        0x120340000000        0x140000000
0x120040015000        0x120040015018        0x18
0x120040016000        0x120040016018        0x18
0x12004001c000        0x12004001c200        0x200
0x12004001d000        0x12004001d200        0x200
0x120040022000        0x120040022018        0x18
0x120040023000        0x120040023018        0x18


***********************5. Op in graph*************************
# 本环节提取报错算子的图信息
op {
    name: "L2Loss"
    type: "L2Loss"
    input: "Variable:0"
    input: "atomic_addr_clean0_11_0:-1"
    attr {
      key: "INPUT_IS_VAR"
      value {
        list {
          b: true
          val_type: VT_LIST_BOOL
        }
      }
    }
    # 省略200行
    ...... 
  }


***********************6. Dump info*************************
# 本环节中可查看dump信息，并分析数据中是否存在NaN/INF信息

/home/root/tools/msaicerr/info_20220314203506/collection/dump/L2Loss.L2Loss.3.1646472651352242
input[0] NaN/INF
output[0] NaN/INF


***********************7. result of single_op_test*************************

# 为保证本环节顺利运行，需保证环境中有真实的device在线，并安装opp、runtime、compiler包为程序运行提供支持。

# 本环节用于获取单算子运行参数并运行。运行流程如下：
# - 通过日志获取异常算子的输入shape、format等编译信息。
# - 通过dump数据获取异常算子的输入数据。
# - 获取kernel_meta目录下异常算子的.o .json信息。
# - 调用rts接口调用单算子运行。

# 若运行成功，说明整网中发生的aicore error无法单算子复现，此时重点查看4.中地址是否存在异常。

# 若运行失败，抛出错误码为runtime 0x7开头错误码，则说明aicore error问题复现。此时可使用生成的单算子脚本进行分析。

# 若抛出其他异常，可具体分析。

========================================================================
run command: None
------------------------------------------------------------------------
- test soc: [Ascend910A]
- test case count: 1
- success count: 0
- failed count: 1
- error count: 0
------------------------------------------------------------------------
Soc Version: Ascend910A
    failed: [L2Loss]  L2Loss_pre-static_te_l2loss_0a9b2632fc2241e91c70b5a3ed5df7a95ba5024113b21f413c84e2bbb8171102_1_test (Ascend910A), error msg: Failed, 
      Case File "/home/root/tools/msaicerr/ms_interface/single_op_case.py", line 230
      Error trace: 
      Traceback (most recent call last):
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/ut/op_ut.py", line 856, in _run_model_run_stage
          self._run_kernel(run_soc_version, case_info, run_cfg)
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/ut/op_ut.py", line 838, in _run_kernel
          tiling=case_info.tiling_data, block_dim=case_info.block_dim)
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/common/ascend_tbe_op.py", line 567, in run
          self._execute_kernel(kernel, knl_args, block_dim)
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/common/ascend_tbe_op.py", line 537, in _execute_kernel
          _execute_kernel()
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/common/ascend_tbe_op.py", line 531, in _execute_kernel
          self.ascend_device.synchronize_with_stream(self._stream)
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/runtime/rts_api.py", line 693, in synchronize_with_stream
          self.parse_error(rt_error, "rtStreamSynchronize")
        File "/home/root/tools/msaicerr/ms_interface/single_op_test_frame/runtime/rts_api.py", line 759, in parse_error
          raise RuntimeError("Received invalid runtime error code:" + hex(rt_error) + extra_info)
      RuntimeError: Received invalid runtime error code:0x7bc87
      
------------------------------------------------------------------------
Some test case failed. Please check your code or case!
========================================================================

Running single op test "python3 /home/root/tools/msaicerr/info_20220314203506/aicerror_0_20220305173051/single_op_test/te_l2loss_0a9b2632fc2241e91c70b5a3ed5df7a95ba5024113b21f413c84e2bbb8171102_1_test.py" can reprocessing."
```