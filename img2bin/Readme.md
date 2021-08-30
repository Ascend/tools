EN|[中文](Readme_cn.md)

# img2bin

The img2bin tool generates input data required for model inference in .bin format. Currently, only preprocessing of neural network whose inputs are images is supported.   
There are two types of data. The first is the image data. The second is the input data required by the model (for example, the second input of Faster R-CNN is the image shape).   
Proportional resizing and zero-padding are performed on the images.

## Prerequisites

- The script can be used in the CentOS and Ubuntu environments and supports only the x86 architecture.
- The script supports Python 2 and Python 3.
- If OpenCV-Python is not installed, the script will automatically install it in the initial use.

## Obtaining the Script

1. By downloading the package
   
   Download the script from the **tools** repository at https://github.com/Ascend/tools to any directory on the server.
   
   For example, the path can be **$HOME/AscendProjects/tools**.

2. By running the **git** command
   
   Run the following command in the **$HOME/AscendProjects** directory to download code:
   
   **git clone  https://github.com/Ascend/tools.git**

## Instructions

Go to the directory where the script is stored.

```
cd $HOME/AscendProjects/img2bin
```

### First type of data: image

- The script preprocesses all images in the directory specified by **-i** based on the parameter settings, and saves the images to the directory specified by **-o** in the name of ***file_name*****.bin**.

```
python2 img2bin.py -i ./images -w 416 -h 416 -f BGR -a NHWC -t uint8 -m [104,117,123] -c [1,1,1] -o ./out
```

```
python3 img2bin.py -i ./images -w 416 -h 416 -f BGR -a NHWC -t uint8 -m [104,117,123] -c [1,1,1] -o ./out
```

### Second type of data: text

- For the second type of data, you need to create a file. **Test.txt** is the file template, where **input_node** is the data, and shape is the image shape.
- The file name extension must be .txt.
- Only the **-i**, **-t**, and **-o** parameters are required.
- **-I** specifies the directory or file path, **-t** specifies the data type, and **-o** specifies the output directory.

```
python2 img2bin.py -i ./test.txt -t uint8 -o ./out
```

```
python3 img2bin.py -i ./test.txt -t uint8 -o ./out
```

## Parameter Description

| Parameter| Description
|----------|----------
| -i| Input directory or path. <br>**The directory cannot contain both images and .txt files. Only one type of data can be converted at a time**.
| -w| Width of the output image
| -h| Height of the output image
| -f| Color format of the output image, which can be BGR, RGB, YUV, or GRAY
| -a| Output image format, which can be NCHW or NHWC
| -t| Output data type of the image or the second data, which can be float32, uint8, int32, or uint32
| -m| Mean subtraction. Defaults to **[0,0,0]**. The sequence is consistent with the image color format.  <br>When the color format is GRAY, set this parameter to **[0]**.
| -c| Normalization. Defaults to **[1,1,1]**. The sequence is consistent with the image color format.  <br>When the color format is GRAY, set this parameter to **[1]**.
| -o| Output directory

