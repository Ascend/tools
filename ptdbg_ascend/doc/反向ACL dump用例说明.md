### 反向ACL dump用例说明

当前昇腾AI处理器上的PyTorch框架通过torch_npu.npu中的init_dump(),set_dump()和finalize_dump()接口来进行ACL级别的数据采集。首先init_dump()会进行初始化dump配置，然后通过set_dump()接口传入配置文件来配置dump参数，最后通过finalize_dump来结束dump。 下面将以torch.sort运算的反向过程为例，介绍反向ACL数据dump的方法。

```bash
import numpy as np
import torch
import torch_npu
torch_npu.npu.set_device("npu:0")
input = torch.tensor(np.load(input_path)).requires_grad_().npu()
grad = torch.tensor(np.load(grad_path)).requires_grad_().npu()
b, c = torch.sort(input)
torch_npu.npu.init_dump()
torch_npu.npu.set_dump("dump.json")
torch_npu.npu.synchronize()
b.backward(grad)
torch_npu.npu.synchronize()
torch_npu.npu.finalize_dump()
```

- input_path是该API前向运算的输入，可以通过ACL dump的API名称获得。如想要对Torch_sort_0_backward进行ACL dump，则该反向API对应的前向过程输入为Torch_sort_0_forward_input.0.npy。
- grad_path是该API反向运算的输入，同理可以通过期望dump的API名称获得。

- b, c是torch.sort的输出，分别表示排序后的tensor和排序后tensor中的各元素在原始tensor中的位置。对torch.sort进行反向时，需要对b进行backward。

**dump.json配置**

```bash
{
  "dump":
  {
    "dump_list": [],
    "dump_path": "/home/HwHiAiUser/dump/output",
    "dump_mode": "all",
    "dump_op_switch": "on"
  }
}
```

**查看dump数据**

采集的dump数据会在{dump_path}/{time}/{device_id}/{model_id}/{data_index}目录下生成。
