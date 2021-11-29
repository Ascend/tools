<!--
 * @Author: your name
 * @Date: 2021-07-05 20:26:55
 * @LastEditTime: 2021-07-08 10:14:20
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: \tools\README_EN.md
-->
EN|[CH](Readme_cn.md)

# tools

#### Introduction

Ascend tools   
**Please go to the corresponding folders to get the tools according to your needs, or click the link below to select the tool you want.**

#### Description

1.  [msame](https://github.com/Ascend/tools/tree/master/msame)

    **Model inference tool**: Input the OM model and the input BIN file required by the model to output the model output data file.

2.  [img2bin](https://github.com/Ascend/tools/tree/master/img2bin)

    **BIN file generation tool**: Generate input data required for model inference, saved in .bin format.

3.  [makesd](https://github.com/Ascend/tools/tree/master/makesd)
    
    **makesd tool**：card making tool package. Provide the card making function under Ubuntu.  

4.  [configure_usb_ethernet](https://github.com/Ascend/tools/tree/master/configure_usb_ethernet)  
     **USB virtual NIC connection script**：Configure the IP address of the USB NIC.
    
5. [pt2pb](https://github.com/Ascend/tools/tree/master/pt2pb)  

   **Tool for converting PyTorch models to TensorFlow PB models**：Input the PyTorch weight parameters model and convert the model to the ONNX format and then to the PB format.

6. [dnmetis](https://github.com/Ascend/tools/tree/master/dnmetis)  

   **Test tool for NPU inference accuracy and performance**：Use Python to encapsulate AscendCL C++ APIs. Input the OM model, dataset images, and labels to perform model inference and output accuracy and performance data.   

7. [msquickcmp](https://github.com/Ascend/tools/tree/master/msquickcmp)    

   **One-click full-process accuracy comparison tool**：This tool applies to TensorFlow and ONNX models. Input the original model and the corresponding offline OM model to output the accuracy comparison result.    

8. [dockerimages](./precision_tool)    
   **Accuracy analysis tool**：The toolkit provides common accuracy comparison functions. Currently, this tool is mainly used in TensorFlow training scenarios and provides interactive query and operation entries for dump data and graph information.

9. [cann-benchmark_infer_scripts](./cann-benchmark_infer_scripts)     
    **Model pre-processing and post-processing scripts corresponding to the cann-benchmark inference software**：This tool contains the model processing scripts of the cann-benchmark inference tool, including the result parsing script and pre-processing and post-processing scripts. These scripts need to be used according to the cann-benchmark guide.

10. [tfdbg_ascend](./tfdbg_ascend)    
   **Tensorflow2.x dump tool**：This tool provides the data dump capability when Tensorflow2.x is running on the CPU/GPU platform.