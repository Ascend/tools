# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################

import os
import torch
import argparse

def parse_args():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--model_path', default=None, 
                        help="""the pytorch model pth file path""")
    parser.add_argument('--input_shape', nargs='+', type=int,
                        help="""the model input shape, e.g. 1 3 224 224""")
   
    args, unknown_args = parser.parse_known_args()
    if len(unknown_args) > 0:
        for bad_arg in unknown_args:
            print("ERROR: Unknown command line arg: %s" % bad_arg)
        raise ValueError("Invalid command line arg(s)")

    return args

def load_model(model_path, input_shape):
    if not os.path.exists(model_path):
        print("The pytorch model is not exist")
        return None

    #修改点1:放开导入模型的注释,并导入自己的模型实现接口.
    #例如:模型实现代码目录为./resnet50,网络实现在resnet.py的class ResNet50类
    #from resnet50.resnet import ResNet50
    
    
    #修改点2:放开创建模型对象注释,并根据自己的模型接口创建模型对象
    #model = ResNet50()
    
    #修改点3:放开加载模型的注释
    #model.load_state_dict(torch.load(model_path))
    
    return model

    
def main():
    args = parse_args()
    print("model path ", args.model_path, ", shape ", args.input_shape)
    #加载模型
    model = load_model(args.model_path, args.input_shape)
    if model is None:
        print("Load model failed")
        return 
 
    #将模型切换到推理状态
    model.eval()
    #创建输入张量
    input = torch.randn(tuple(args.input_shape)) 
    #生成的onnx文件存放在pytorch模型同级目录下,文件名相同,后缀为onnx
    export_onnx_file = os.path.splitext(args.model_path)[0] + '.onnx'

    # Export with ONNX
    torch.onnx.export(model, input, export_onnx_file, verbose=True)
    
if __name__== "__main__":
    main()
