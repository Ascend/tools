EN|[CH](Readme_cn.md)

# tools

#### introduce

Ascend tools   
**Please go to the corresponding folder to get the tool according to your needs, or click the link below to select the tool you need to use.**

#### explain

1.  [msame](https://github.com/Ascend/tools/tree/master/msame)

    **Model reasoning tool**:Input. Om model and model required input bin file, output model output data file.

2.  [img2bin](https://github.com/Ascend/tools/tree/master/img2bin)

    **Bin file generation tool** : Generates input data required for model reasoning, saved in.bin format.

3.  [makesd](https://github.com/Ascend/tools/tree/master/makesd)
    
    **makesd tool**：makesd tools package，Provide card making function under ubuntu.  

4.  [faster_install](https://github.com/Ascend/tools/tree/master/faster_install)
    
    **faster_install**：environment fast install script.  

5.  [configure_usb_ethernet](https://github.com/Ascend/tools/tree/master/configure_usb_ethernet)  
     **configure_usb_ethernet**：configuring the IP address of the USB NIC 。
    
6. [pt2pb](https://github.com/Ascend/tools/tree/master/pt2pb)  

   **pytorch model transform to tensorflow pb model tool**：input pytorch weights parameters model，transform to onnx file，then transform to pb model

7. [dnmetis](https://github.com/Ascend/tools/tree/master/dnmetis)  

   **Test tool for NPU inference precision and performance**：Using Python to encapsulate the C++ interface of ACL, inputting om model and original dataset images and tags, we can execute model inference and give out precision and performance of the om model   

8. [msquickcmp](https://github.com/Ascend/tools/tree/master/msquickcmp)    

   **One-button precision comparison tool for the whole process**：The tool works with TensorFlow and OnNX models, input the original model and the corresponding offline OM model and output precision comparison results。    

9. [dockerimages](./dockerimages)    
   **docker images**：docker images for developing/catenation on Atlas products (Atlas200DK/Atlas300)。  

10. [dockerimages](./precision_tool)    
   **precision problem analysis tools**：The toolkit provides common features of precision comparison. Currently, the tool is mainly suitable for TensorFlow training scenarios and provides interactive query and operation entry for Dump data/graph information。

