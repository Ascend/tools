EN|[CH](README.md)

## 1.Install requirements：
```
pip3.7.5 install opencv-python
cd backend_C++/dnmetis_backend
python3.7.5 setup.py install
```
Details of dnmetis_backend installation can be found in backend_C++/dnmetis_backend/README.md. Notice that, you just need to install requirements once for a brand new Ai1-Inference environment。

## 2.Download model(.om)

Here is an example of how to run npu inference of efficientnet-b8:\
1.download  efficientnet-b8 model(.om): \
URL：[baidu pan](https://pan.baidu.com/s/1N-kpQoDe3NRxvjFKjAT9AA) \
Extracted code：tvg0  

Original tensorflow model of efficientnet-b8(.pb):\
URL：[baidu pan](https://pan.baidu.com/s/1CajdSlNTh6k35RoyOn-3Ug)\
Extracted code：slqm 

If you want to acknowledge how to generate om from pb，pls download efficientnet-b8.pb and execute ATC cmd：\
atc --model=efficientnet-b8.pb --framework=3 --input_shape="images:1,672,672,3" --output=efficientnet --mode=0 --out_nodes="Softmax:0" --soc_version=Ascend310 --input_fp16_nodes=images --output_type=FP16

2.Imagenet-val dataset and labels in val_map.txt:

Here is an example of 10 pictures of Imagenet-val dataset：

![输入图片说明](https://images.gitee.com/uploads/images/2020/0918/234302_a572d632_5418572.jpeg "无标题.jpg")



## 3.Start execute the inference:

bash run_inference.sh

Log:
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
As you seen, "139.47 ms" is the npu inference time，"0.8" is the top1 Accuracy of 10 pictures。

## 4.Top1 Accuracy of entire Imagenet2012-val Datasets(5w pictures):

![输入图片说明](https://images.gitee.com/uploads/images/2020/0919/010210_5cf496fc_5418572.png "屏幕截图.png")


## 5.modify main.py for your own model:

Only need to concern about the dataset，pre-process，post-process：

### pre-process:
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

### inference and post-process:
```
        predictions = backend.predict(args.feed[i])
        #print(args.feed[i].shape)
        print('img_orig:',args.image_list[i],'label:',args.label_list[i],'predictions:',np.argmax(predictions),'\n')
```


