中文|[英文](README_EN.md)

## 1.安装依赖：
```
pip3.7.5 install opencv-python
cd backend_C++/dnmetis_backend
python3.7.5 setup.py install
```
安装dnmetis_backend的细节可以在backend_C++/dnmetis_backend/README.md看到，默认的toolkit安装路径为：/home/HwHiAiUser/Ascend/ascend-toolkit/20.10.0.B023/，如果不是，请修改setup.py中49~51行的路径。\
对于一个全新的Ai1推理环境，只需要安装一次依赖，不需要重复安装。

## 2.下载om模型(.om)

如下示例展示如何在NPU上运行efficientnet-b8模型:\
1.下载efficientnet-b8 model(.om): \
链接：[百度网盘](https://pan.baidu.com/s/1N-kpQoDe3NRxvjFKjAT9AA) \
提取码：tvg0  
下载的om模型放到model文件夹.

原生的TensorFlow模型efficientnet-b8(.pb):\
链接：[百度网盘](https://pan.baidu.com/s/1CajdSlNTh6k35RoyOn-3Ug)\
提取码：slqm 

如果想了解从pb模型如何转换成om模型，请下载efficientnet-b8.pb模型，使用ATC模型转换工具，或者执行转换命令：\
atc --model=efficientnet-b8.pb --framework=3 --input_shape="images:1,672,672,3" --output=efficientnet --mode=0 --out_nodes="Softmax:0" --soc_version=Ascend310 --input_fp16_nodes=images --output_type=FP16

2.Imagenet-val数据集和标签:

这里的示例仅仅展示了从Imagenet-val数据集挑选的10张图片：\
![输入图片说明](https://images.gitee.com/uploads/images/2020/0918/234302_a572d632_5418572.jpeg "无标题.jpg")



## 3.执行推理:
建议提交的PR代码统一使用run_inference.sh作为入口：\
bash run_inference.sh

执行日志:
```
[INFO]  start backend_predict is -1518493925
[INFO]  start Execute is -1518490258
[INFO]  model execute success
[INFO]  end Execute is -1518350716
[INFO]  npu compute cost 139.476000 ms
[INFO]  1.output data success
[INFO]  2.output data success
[INFO]  execute sample success
[INFO]  Pure device execute time is 0.000000 ms
[INFO]  end backend_predict is -1518346882
img_orig: ILSVRC2012_val_00000010.JPEG label: 332 predictions: 332

Predict total jpeg: 10  Accuracy:  0.8
```
如上所示, "139.476 ms"是NPU的推理时间，"0.8" 是10张图片的top1精度。

## 4.完整的5w张Imagenet2012-val数据集精度:

![输入图片说明](https://images.gitee.com/uploads/images/2020/0919/010210_5cf496fc_5418572.png "屏幕截图.png")


## 5.main.py修改点:

如果需要使用你自己的模型来推理和计算精度，请修改main.py\
只需要关心数据集、预处理和后处理代码部分：

### 预处理:
```
def resize_with_aspectratio(img, out_height, out_width, scale=87.5, inter_pol=cv2.INTER_LINEAR):
    height, width = img.shape[:2]
    new_height = int(100. * out_height / scale)
    new_width = int(100. * out_width / scale)
    if height > width:
        w = new_width
        h = int(new_height * height / width)
    else:
        h = new_height
        w = int(new_width * width / height)
    img = cv2.resize(img, (w, h), interpolation=inter_pol)
    return img

def center_crop(img, out_height, out_width):
    height, width = img.shape[:2]
    left = int((width - out_width) / 2)
    right = int((width + out_width) / 2)
    top = int((height - out_height) / 2)
    bottom = int((height + out_height) / 2)
    img = img[top:bottom, left:right]
    return img
def pre_process_noisy(img, dims=None, precision="fp32"):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    output_height, output_width, _ = dims
    cv2_interpol = cv2.INTER_CUBIC
    img = resize_with_aspectratio(img, output_height, output_width, inter_pol=cv2_interpol)
    img = center_crop(img, output_height, output_width)
    MEAN_RGB = [0.485 * 255, 0.456 * 255, 0.406 * 255]
    STDDEV_RGB = [0.229 * 255, 0.224 * 255, 0.225 * 255]

    if precision=="fp32":
        img = np.asarray(img, dtype='float32')
    if precision=="fp16":
        img = np.asarray(img, dtype='float16')

    means = np.array([0.485 * 255, 0.456 * 255, 0.406 * 255], dtype=np.float32)
    img -= means
    stddev = np.array([0.229 * 255, 0.224 * 255, 0.225 * 255], dtype=np.float32)
    img /= stddev
    return img
```

### 推理和后处理:
```
        predictions = backend.predict(args.feed[i])
        #print(args.feed[i].shape)
        print('img_orig:',args.image_list[i],'label:',args.label_list[i],'predictions:',np.argmax(predictions),'\n')
```