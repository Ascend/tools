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

import glob
import os
import sys
import argparse
import collections
"""
    0,0 ------> x (width)
     |
     |  (Left,Top)
     |      *_________
     |      |         |
            |         |
     y      |_________|
  (height)            *
                (Right,Bottom)
"""


MINOVERLAP = 0.5  # default value (defined in the PASCAL VOC2012 challenge)
top_margin = 0.15  # in percentage of the figure height
bottom_margin = 0.05  # in percentage of the figure height


def file_lines_to_list(path):
    """
    Convert the lines of a file to a list
    """
    # open txt file lines to a list
    with open(path) as f:
        content = f.readlines()
    # remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content


def voc_ap(recall, precision):
    """
    Calculate the AP given the recall and precision array
    1) We calculate a version of the measured
    precision/recall curve with precision monotonically decreasing
    2) We calculate the AP as the area
    under this curve by numerical integration.
    """
    """
    --- Official matlab code VOC2012---
    m_recall=[0 ; recall ; 1];
    m_precision=[0 ; precision ; 0];
    for j=numel(m_precision)-1:-1:1
            m_precision(i)=max(m_precision(j),m_precision(j+1));
    end
    i=find(m_recall(2:end)~=m_recall(1:end-1))+1;
    ap=sum((m_recall(i)-m_recall(i-1)).*m_precision(i));
    """
    recall.insert(0, 0.0)  # insert 0.0 at beginning of list
    recall.append(1.0)  # insert 1.0 at end of list
    m_recall = recall[:]
    precision.insert(0, 0.0)  # insert 0.0 at beginning of list
    precision.append(0.0)  # insert 0.0 at end of list
    m_precision = precision[:]
    """
    This part makes the precision monotonically decreasing
        (goes from the end to the beginning)
        matlab: for i=numel(m_precision)-1:-1:1
                    m_precision(i)=max(m_precision(i),m_precision(i+1));
    """

    for i in range(len(m_precision) - 2, -1, -1):
        m_precision[i] = max(m_precision[i], m_precision[i + 1])
    """
     This part creates a list of indexes where the recall changes
        matlab: i=find(m_recall(2:end)~=m_recall(1:end-1))+1;
    """
    i_list = []
    for i in range(1, len(m_recall)):
        if m_recall[i] != m_recall[i - 1]:
            i_list.append(i)  # if it was matlab would be i + 1
    """
     The Average Precision (AP) is the area under the curve
        (numerical integration)
        matlab: ap=sum((m_recall(i)-m_recall(i-1)).*m_precision(i));
    """
    ap = 0.0
    for i in i_list:
        ap += ((m_recall[i] - m_recall[i - 1]) * m_precision[i])
    return ap, m_recall, m_precision


def is_float_between_0_and_1(value):
    """
    check if the number is a float between 0.0 and 1.0
    """
    try:
        val = float(value)
        if val > 0.0 and val < 1.0:
            return True
        else:
            return False
    except ValueError:
        return False


def error(msg):
    """
    throw error and exit
    """
    print(msg)
    sys.exit(0)


def check_args(args):
    """
    check arguments
    """
    if not (os.path.exists(args.label_path)):
        error("annotation file:{} does not exist.".format(args.label_path))
    
    if not (os.path.exists(args.npu_txt_path)):
        error("txt path:{} does not exist.".format(args.npu_txt_path))
    
    if args.ignore is None:
        args.ignore = []
    return args


def parse_line(txt_file, lines_list, bounding_boxes, counter_per_class, already_seen_classes):
    """ parse line
        :param txt_file:
        :param lines_list:
        :param bounding_boxes:
        :param counter_per_class:
        :param already_seen_classes:
        :return: bounding_boxes, counter_per_class
    """
    for line in lines_list:
        try:
            class_name, left, top, right, bottom = line.split()
        except ValueError:
            error_msg = "Error: File " + txt_file + " in the wrong format.\n"
            error_msg += " Expected: <class_name> <l> <t> <r> <b>\n"
            error_msg += " Received: " + line
            error(error_msg)
        if class_name in args.ignore:
            continue
        bbox = left + " " + top + " " + right + " " + bottom
        bounding_boxes.append({"class_name": class_name, "bbox": bbox, "used": False})
        counter_per_class[class_name] += 1

        if class_name not in already_seen_classes:
            already_seen_classes.append(class_name)
    return bounding_boxes, counter_per_class


def get_label_list(file_path):
    """ get label list via file paths
        :param file_path: label  file path
        :return: ret
                 map , include file_bbox, classes, n_classes, counter_per_class
    """
    files_list = glob.glob(file_path + '/*.txt')
    if len(files_list) == 0:
        error("Error: No ground-truth files found!")
    files_list.sort()
    # dictionary with counter per class
    counter_per_class = collections.defaultdict(int)
    file_bbox = {}

    for txt_file in files_list:
        file_id = txt_file.split(".txt", 1)[0]
        file_id = os.path.basename(os.path.normpath(file_id))
        # check if there is a correspondent detection-results file
        temp_path = os.path.join(file_path, (file_id + ".txt"))
        if not os.path.exists(temp_path):
            error_msg = "Error. File not found: {}\n".format(temp_path)
            error(error_msg)
        lines_list = file_lines_to_list(txt_file)
        # create ground-truth dictionary
        bounding_boxes = []
        already_seen_classes = []
        boxes, counter_per_class = parse_line(txt_file, lines_list, bounding_boxes, counter_per_class,
                                              already_seen_classes)
        file_bbox[file_id] = boxes
    
    classes = list(counter_per_class.keys())
    # let's sort the classes alphabetically
    classes = sorted(classes)
    n_classes = len(classes)
    ret = dict()
    ret['file_bbox'] = file_bbox
    ret['classes'] = classes
    ret['n_classes'] = n_classes
    ret['counter_per_class'] = counter_per_class
    return ret


def get_predict_list(file_path, gt_classes):
    """ get predict list with file paths and class names
        :param file_path: predict txt file path
        :param gt_classes: class information
        :return: class_bbox bbox of every class
    """
    dr_files_list = glob.glob(file_path + '/*.txt')
    dr_files_list.sort()
    class_bbox = {}
    for class_index, class_name in enumerate(gt_classes):
        bounding_boxes = []
        for txt_file in dr_files_list:
            # the first time it checks
            # if all the corresponding ground-truth files exist
            file_id = txt_file.split(".txt", 1)[0]
            file_id = os.path.basename(os.path.normpath(file_id))
            lines = file_lines_to_list(txt_file)
            for line in lines:
                try:
                    sl = line.split()
                    tmp_class_name, confidence, left, top, right, bottom = sl
                    if float(confidence) < float(args.threshold):
                        continue
                except ValueError:
                    error_msg = "Error: File " + txt_file + " wrong format.\n"
                    error_msg += " Expected: <classname> <conf> <l> <t> <r> <b>\n"
                    error_msg += " Received: " + line
                    error(error_msg)
                if tmp_class_name == class_name:
                    bbox = left + " " + top + " " + right + " " + bottom
                    bounding_boxes.append({"confidence": confidence, "file_id": file_id, "bbox": bbox})
        # sort detection-results by decreasing confidence
        bounding_boxes.sort(key=lambda x: float(x['confidence']), reverse=True)
        class_bbox[class_name] = bounding_boxes
    return class_bbox


def calculate_PR(sum_AP, fp, tp, counter_per_class, class_name):
    """
       @description: calculate PR
       @param sum_AP
       @param fp
       @param tp
       @param counter_per_class
       @param class_name
       @return ret
                map, include sum_AP, text, prec, rec
    """
    cumsum = 0
    for idx, val in enumerate(fp):
        fp[idx] += cumsum
        cumsum += val
    cumsum = 0
    for idx, val in enumerate(tp):
        tp[idx] += cumsum
        cumsum += val
    rec = tp[:]
    for idx, val in enumerate(tp):
        rec[idx] = float(tp[idx]) / counter_per_class[class_name]
    prec = tp[:]
    for idx, val in enumerate(tp):
        prec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])
    
    ap, mrec, mprec = voc_ap(rec[:], prec[:])
    sum_AP += ap
    # class_name + " AP = {0:.2f}%".format(ap * 100)
    text = "{0:.2f}%".format(ap * 100) + " = " + class_name + " AP "
    ret = dict()
    ret['sum_AP'] = sum_AP
    ret['text'] = text
    ret['prec'] = prec
    ret['rec'] = rec
    return ret


def calculate_AP(output_file, gt_classes, labels, class_bbox, counter_per_class):
    """
    Calculate the AP for each class
    :param output_file:
    :param gt_classes: [80]
    :param labels: {file_index:[{"class_name": class_name, "bbox": bbox, "used": False}]}
    :param class_bbox: {class_name:[{"confidence": confidence,
                        "file_id": file_id, "bbox": bbox}]}
    :return:
    """
    sum_AP = 0.0
    writer = open(output_file, 'w')
    writer.write("# AP and precision/recall per class\n")
    count_true_positives = {}
    n_classes = len(gt_classes)
    for class_index, class_name in enumerate(gt_classes):
        count_true_positives[class_name] = 0
        """
         Load detection-results of that class
        Assign detection-results to ground-truth objects
        """
        dr_data = class_bbox[class_name]
        nd = len(dr_data)
        tp = [0] * nd  # creates an array of zeros of size nd
        fp = [0] * nd
        for idx, detection in enumerate(dr_data):
            file_id = detection["file_id"]
            ground_truth_data = labels[file_id]

            ovmax = -1
            gt_match = -1
            # load detected object bounding-box
            bb = [float(x) for x in detection["bbox"].split()]
            for obj in ground_truth_data:
                # look for a class_name match
                if obj["class_name"] == class_name:
                    bbgt = [float(x) for x in obj["bbox"].split()]
                    bi = [max(bb[0], bbgt[0]), max(bb[1], bbgt[1]),
                          min(bb[2], bbgt[2]), min(bb[3], bbgt[3])]
                    iw = bi[2] - bi[0] + 1
                    ih = bi[3] - bi[1] + 1
                    if iw > 0 and ih > 0:
                        # compute overlap (IoU)
                        ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + \
                             (bbgt[2] - bbgt[0] + 1) * \
                             (bbgt[3] - bbgt[1] + 1) - iw * ih
                        ov = iw * ih / ua
                        if ov > ovmax:
                            ovmax = ov
                            gt_match = obj

            # set minimum overlap
            min_overlap = MINOVERLAP
            if ovmax >= min_overlap:
                if "difficult" not in gt_match:
                    if not bool(gt_match["used"]):
                        # true positive
                        tp[idx] = 1
                        gt_match["used"] = True
                        count_true_positives[class_name] += 1
                    else:
                        # false positive (multiple detection)
                        fp[idx] = 1
            else:
                # false positive
                fp[idx] = 1
        # compute precision / recall
        ret = calculate_PR(sum_AP, fp, tp, counter_per_class, class_name)
        sum_AP = ret['sum_AP']
        text = ret['text']
        prec = ret['prec']
        rec = ret['rec']
        print(text)
        rounded_prec = ['%.2f' % elem for elem in prec]
        rounded_rec = ['%.2f' % elem for elem in rec]
        writer.write(text + "\n Precision: " + str(rounded_prec) +
                     "\n Recall :" + str(rounded_rec) + "\n\n")
    writer.write("\n# mAP of all classes\n")
    mAP = sum_AP / n_classes
    text = "mAP = {0:.2f}%".format(mAP * 100)
    writer.write(text + "\n")
    print(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('mAP calculate')
    parser.add_argument('-i', '--ignore', nargs='+', type=str,
                        help="ignore a list of classes.")
    parser.add_argument('--label_path', default="./ground-truth", help='the path of the label files')
    parser.add_argument('--npu_txt_path', default="./detection-results", help='the path of the predict result')
    parser.add_argument('--output_file', default="./output.txt", help='save result file')
    parser.add_argument('--threshold', default=0, help='threshold of the object score')
    args = parser.parse_args()
    args = check_args(args)

    ret = get_label_list(args.label_path)
    gt_file_bbox = ret['file_bbox']
    gt_classes = ret['classes']
    gt_n_classes = ret['n_classes']
    counter_per_class = ret['counter_per_class']
    class_bbox = get_predict_list(args.npu_txt_path, gt_classes)
    calculate_AP(args.output_file, gt_classes, gt_file_bbox, class_bbox, counter_per_class)

