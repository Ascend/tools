#1 建立虚拟环境
$ virtualenv .venv

#2 激活虚拟环境
$ source .venv/bin/activate

#3 安装依赖包
$ pip install -r requirements.txt
$ pip install -e onnx-tensorflow

#4 生成onnx模型
$ python pt2onnx.py

#5 生成pb模型
$ onnx-tf convert -i efficientnet-b3.onnx -o efficientnet-b3.pb
