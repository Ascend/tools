"""
    Copyright 2020 Huawei Technologies Co., Ltd

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    Typical usage example:
"""

import os
import argparse
import numpy as np


def read_class_names(class_file_name):
    """
    loads class name from a file
    """
    names = {}
    with open(class_file_name, 'r') as data:
        for id, name in enumerate(data):
            names[id] = name.strip('\n')
    return names


def _iou(box1, box2, precision=1e-5):
    """
    Calculate the Intersection over Union value for 2 bounding boxes

    :param box1: array of 4 values
    (top left and bottom right coords): [x0, y0, x1, x2]
    :param box2: same as box1
    :param precision: calculate precision for calculating
    :return: IoU
    """
    box1_x0, box1_y0, box1_x1, box1_y1 = box1
    box2_x0, box2_y0, box2_x1, box2_y1 = box2

    int_x0 = max(box1_x0, box2_x0)
    int_y0 = max(box1_y0, box2_y0)
    int_x1 = min(box1_x1, box2_x1)
    int_y1 = min(box1_y1, box2_y1)

    int_area = max(int_x1 - int_x0, 0) * max(int_y1 - int_y0, 0)

    b1_area = (box1_x1 - box1_x0) * (box1_y1 - box1_y0)
    b2_area = (box2_x1 - box2_x0) * (box2_y1 - box2_y0)

    # we add small epsilon of 1e-05 to avoid division by 0
    ret_iou = int_area / (b1_area + b2_area - int_area + precision)
    return ret_iou


def parse_line(line):
    """
    parse input info file, file lines format as: seqno filename width height
    """
    temp = line.split(" ")
    index = temp[1].split("/")[-1].split(".")[0]
    # height width(not width height)
    return index, (int(temp[2]), int(temp[3]))


def postprocessing(bbox: np.ndarray,
                   image_size,
                   side=416,
                   threshold=0.3):
    """
    This function is postprocessing for YOLOv3 output.

    Before calling this function, reshape the raw output of YOLOv3 to
    following form
        numpy.ndarray:
            [x, y, width, height, confidence, probability of 80 classes]
        shape: (85,)
    The postprocessing restore the bounding rectangles of YOLOv3 output
    to origin scale and filter with non-maximum suppression.

    :param bbox: a numpy array of the YOLOv3 output
    :param image_path: a string of image path
    :param side: the side length of YOLOv3's input
    :param threshold: the threshold of non-maximum suppression
    :return: three list for best bound, class and score
    """
    xywh = bbox[:, 0: 4]
    confidence = bbox[:, 4]
    probability = bbox[:, 5:]
    xmin = (xywh[:, 0] - xywh[:, 2] / 2)[:, np.newaxis]
    xmax = (xywh[:, 0] + xywh[:, 2] / 2)[:, np.newaxis]
    ymin = (xywh[:, 1] - xywh[:, 3] / 2)[:, np.newaxis]
    ymax = (xywh[:, 1] + xywh[:, 3] / 2)[:, np.newaxis]
    bounds = np.concatenate((xmin, ymin, xmax, ymax), axis=1)

    width, height = image_size
    scale = side / max([width, height])
    width_scaled = int(width * scale)
    height_scaled = int(height * scale)
    width_offset = (side - width_scaled) // 2
    height_offset = (side - height_scaled) // 2
    bounds[:, (0, 2)] = (bounds[:, (0, 2)] - width_offset) / scale
    bounds[:, [1, 3]] = (bounds[:, [1, 3]] - height_offset) / scale
    bounds = bounds.astype(np.int32)

    bounds[np.where(bounds < 0)] = 0
    bounds[np.where(bounds[:, 2] > width), 2] = width - 1
    bounds[np.where(bounds[:, 3] > height), 3] = height - 1
    mask = np.ones(bounds.shape, dtype=bool)
    mask[:, 2] = (bounds[:, 2] - bounds[:, 0]) > 0
    mask[:, 3] = (bounds[:, 3] - bounds[:, 1]) > 0
    mask = np.logical_and.reduce(mask, axis=1)
    classes = np.argmax(probability, axis=1)
    scores = confidence * probability[np.arange(classes.size), classes]
    mask = mask & (scores > threshold)
    bounds = bounds[mask]
    classes = classes[mask]
    scores = scores[mask]
    return nms(bounds, classes, scores)


def nms(bounds, classes, scores):
    """
    The non-maximum suppression algorithm.

    :param bounds: the bounding vertices
    :param classes: class of bounding
    :param scores: confidence of bounding
    :return: the best bounding, class and confidence
    """
    best_bounds = []
    best_scores = []
    best_classes = []
    for i in list(np.unique(classes)):
        mask_class = classes == i
        bounds_class = bounds[mask_class, :]
        scores_class = scores[mask_class]
        while bounds_class.size > 0:
            max_index = np.argmax(scores_class)
            best_bound = bounds_class[max_index]
            best_bounds.append(best_bound)
            best_scores.append(scores_class[max_index])
            best_classes.append(i)
            bounds_class = np.delete(bounds_class, max_index, axis=0)
            scores_class = np.delete(scores_class, max_index)
            if bounds_class.size == 0:
                break
            best_area = (best_bound[2] - best_bound[0]) * \
                        (best_bound[3] - best_bound[1])
            areas = (bounds_class[:, 2] - bounds_class[:, 0]) * \
                    (bounds_class[:, 3] - bounds_class[:, 1])
            xmax = np.maximum(best_bound[0], bounds_class[:, 0])
            xmin = np.minimum(best_bound[2], bounds_class[:, 2])
            ymax = np.maximum(best_bound[1], bounds_class[:, 1])
            ymin = np.minimum(best_bound[3], bounds_class[:, 3])
            width = np.maximum(0, xmin - xmax + 1)
            height = np.maximum(0, ymin - ymax + 1)
            areas_intersection = width * height
            iou = areas_intersection / (best_area + areas - areas_intersection)
            mask_iou = iou < 0.45
            bounds_class = bounds_class[mask_iou, :]
            scores_class = scores_class[mask_iou]
    return best_bounds, best_classes, best_scores


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin_data_path", default="./result/dumpOutput")
    parser.add_argument("--test_annotation",
                        default="./yolo_tf.info")
    parser.add_argument("--det_results_path",
                        default="./detection-results/")
    parser.add_argument("--coco_class_names", default="./coco2014.names")
    parser.add_argument("--net_input_size", default=416)
    parser.add_argument("--net_out_num", default=3)
    flags = parser.parse_args()

    # generate dict according to annotation file for query resolution
    # load width and height of input images
    img_size_dict = dict()
    with open(flags.test_annotation)as f:
        for line in f.readlines():
            temp = parse_line(line)
            img_size_dict[temp[0]] = temp[1]

    # load map between index and class of coco and voc
    coco_class_map = read_class_names(flags.coco_class_names)
    coco_set = set(coco_class_map.values())

    # read bin file for generate predict result
    bin_path = flags.bin_data_path
    net_input_size = flags.net_input_size

    det_results_path = flags.det_results_path
    os.makedirs(det_results_path, exist_ok=True)
    total_img = set([name[:name.rfind('_')]
                     for name in os.listdir(bin_path) if "bin" in name])
    for bin_file in sorted(total_img):
        path_base = os.path.join(bin_path, bin_file)
        # load all detected output tensor
        res_buff = []
        for num in range(flags.net_out_num):
            if os.path.exists(path_base + "_" + str(num + 1) + ".bin"):
                buf = np.fromfile(path_base + "_" +
                                  str(num + 1) + ".bin", dtype="float32")
                buf = np.reshape(buf, [-1, 85])
                res_buff.append(buf)
            else:
                print("[ERROR] file not exist", path_base +
                      "_" + str(num + 1) + ".bin")

        res_tensor = np.concatenate(res_buff, axis=0)
        img_index_str = bin_file
        current_img_size = img_size_dict[img_index_str]
        bounds, classes, scores = postprocessing(res_tensor, current_img_size)
        det_results_str = ''
        for idx, class_ind in enumerate(classes):
            class_name = coco_class_map[class_ind]
            det_results_str += "{} {} {} {} {} {}\n".format(class_name, str(scores[idx]), bounds[idx][0],
                                                            bounds[idx][1], bounds[idx][2], bounds[idx][3])
        det_results_file = os.path.join(
            det_results_path, img_index_str + ".txt")
        with open(det_results_file, "w") as detf:
            detf.write(det_results_str)
        print(det_results_str)
