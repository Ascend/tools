import os
import numpy as np
import argparse

def read_class_names(class_file_name):
    """
    loads class name from a file
    """
    names = {}
    with open(class_file_name, 'r') as data:
        for id, name in enumerate(data):
            names[id] = name.strip('\n')
    return names

def parse_line(line):
    temp = line.split(" ")
    index = temp[1].split("/")[-1].split(".")[0]
    return index, (int(temp[3]), int(temp[2]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin_data_path", default="./pic_1024/")
    parser.add_argument("--test_annotation", default="./ImageNet.info")
    parser.add_argument("--det_results_path", default="./input/detection-results/")
    parser.add_argument("--coco_class_names", default="./input/coco.names")
    parser.add_argument("--voc_class_names", default="./input/voc.names")
    parser.add_argument("--net_input_width", default=416)
    parser.add_argument("--net_input_height", default=416)
    flags = parser.parse_args()

    # load the test image info
    img_size_dict = dict()
    with open(flags.test_annotation)as f:
        for line in f.readlines():
            temp = parse_line(line)
            img_size_dict[temp[0]] = temp[1]

    # load label class name
    coco_class_map = read_class_names(flags.coco_class_names)
    coco_set = set(coco_class_map.values())
    voc_class_map = read_class_names(flags.voc_class_names)
    voc_set = set(voc_class_map.values())

    # load the output files
    # "_1.bin" for detinfo
    # "_2.bin" for numbox
    bin_path = flags.bin_data_path
    net_input_width = flags.net_input_width
    net_input_height = flags.net_input_height
    det_results_path = flags.det_results_path
    if not os.path.exists(det_results_path):
        os.makedirs(det_results_path)

    for img_name in img_size_dict:
        boxbuf = []
        boxnum = []
        det_results_str = ""
        path_det_output1 = os.path.join(bin_path, img_name + "_1.bin")
        if os.path.exists(path_det_output1):
            boxbuf = np.fromfile(path_det_output1, dtype="float32")
        else:
            print("[ERROR] file not exist", path_det_output1)
            break
        path_det_output2 = os.path.join(bin_path, img_name + "_2.bin")
        if os.path.exists(path_det_output2):
            boxnum = np.fromfile(path_det_output2, dtype="float32")
        else:
            print("[ERROR] file not exist", path_det_output2)
            break
        boxcnt = boxnum[0].astype(int)
        if(boxcnt == 0):
            det_results_str = ""
        else:
            j = 0
            expect_data_list = []
            pre_box_list = []
            for i in boxbuf[0:boxcnt * 6]:
                expect_data_list.append(round(float(i), 3))
            for i in range(6):
                pre_box_list.append(list(expect_data_list[j:j + boxcnt]))
                j += boxcnt
            current_img_size = img_size_dict[img_name]
            for i in range(int(boxcnt)):
                class_ind = int(pre_box_list[5][i])
                if class_ind < 0:
                    print("[ERROR] predicted object class error:", class_ind)
                    continue
                else:
                    class_name = coco_class_map[class_ind]
                    #print("[INFO] predicted object typeID: ", class_ind, " typeName:", class_name)
                    if class_name in voc_set:
                        hscale = current_img_size[0] / float(flags.net_input_height)
                        wscale = current_img_size[1] / float(flags.net_input_width)
                        det_results_str += "{} {} {} {} {} {}\n".format(
                            class_name, str(pre_box_list[4][i]), str(pre_box_list[0][i]),
                            str(pre_box_list[1][i]), str(pre_box_list[2][i]),
                            str(pre_box_list[3][i]))
        det_results_file = os.path.join(det_results_path, img_name + ".txt")
        with open(det_results_file, "w") as detf:
            detf.write(det_results_str)
