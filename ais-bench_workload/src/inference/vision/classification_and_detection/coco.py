import logging
import os
import json
import time

import numpy as np

import core.utils as utils
import core.dataset as dataset

from pycocotools.cocoeval import COCOeval
from pycocotools.coco import COCO

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("coco")

class Coco(dataset.DataSet):
    def __init__(self, dataset_path, image_list=None, name=None, image_size=None,
                 data_format="NHWC", pre_process=None, count=None, cache_path=None,use_label_map=False):
        super().__init__()
        self.image_size = image_size
        self.image_list = []
        self.label_list = []
        self.image_ids = []
        self.image_sizes = []
        self.count = count
        self.dataset_path = dataset_path
        self.pre_process = pre_process
        self.use_label_map=use_label_map
        if not cache_path:
            cache_path = os.getcwd()
        print("lcm debug cache_path:{} name:{} format:{} image_list:{}".format(cache_path, name, data_format, image_list))
        self.cache_path = os.path.join(cache_path, "preprocessed", name, data_format)
        # input images are in HWC
        self.need_transpose = True if data_format == "NCHW" else False
        not_found = 0 
        empty_80catageories = 0
        if image_list is None:
            raise ValueError("image_list is Null not set")
        self.annotation_file = image_list
        if self.use_label_map:
            # for pytorch
            label_map = {}
            with open(self.annotation_file) as fin:
                annotations = json.load(fin)
            for cnt, cat in enumerate(annotations["categories"]):
                label_map[cat["id"]] = cnt + 1
            print("label map:{}".format(label_map))

        os.makedirs(self.cache_path, exist_ok=True)
        images = {}
        with open(image_list, "r") as f:
            coco = json.load(f)
        for i in coco["images"]:
            images[i["id"]] = {"file_name": i["file_name"],
                               "height": i["height"],
                               "width": i["width"],
                               "bbox": [],
                               "category": []}
        for a in coco["annotations"]:
            i = images.get(a["image_id"])
            if i is None:
                continue
            catagory_ids = label_map[a.get("category_id")] if self.use_label_map else a.get("category_id")
            i["category"].append(catagory_ids)
            i["bbox"].append(a.get("bbox"))

        for image_id, img in images.items():
            image_name = os.path.join(img["file_name"])
            src = os.path.join(self.dataset_path, image_name)
            if not os.path.exists(src):
                # if the image does not exists ignore it
                not_found += 1
                continue
            if len(img["category"])==0 and self.use_label_map: 
                #if an image doesn't have any of the 81 categories in it    
                empty_80catageories += 1 #should be 48 images - thus the validation sert has 4952 images
                continue 

            self.image_ids.append(image_id)
            self.image_list.append(image_name)
            self.image_sizes.append((img["height"], img["width"]))
            self.label_list.append((img["category"], img["bbox"]))

            # limit the dataset if requested
            if self.count and len(self.image_list) >= self.count:
                break

        if not self.image_list:
            log.error("no images in image list found list:{} ilist:{}".format(image_list, self.image_list))
            raise ValueError("no images in image list found")
        if not_found > 0:
            log.info("reduced image list, %d images not found", not_found)
        if empty_80catageories > 0:
            log.info("reduced image list, %d images without any of the 80 categories", empty_80catageories)

        log.info("loaded {} images".format(
            len(self.image_list)))

        self.label_list = np.array(self.label_list)
        # print("lcm debug image ids:{}".format(self.image_ids))
        # print("lcm debug image_list:{}".format(self.image_list))
        # print("lcm debug image_sizes:{}".format(self.image_sizes))
        # print("lcm debug label_list:{} labelmap:{}".format(self.label_list, self.use_label_map))

    def get_processeddata_item(self, nr):
        """Get image by number in the list."""
        dst = os.path.join(self.cache_path, self.image_list[nr])
        img = np.load(dst + ".npy")
        return img

    def get_sample_path(self, nr):
        src = os.path.join(self.dataset_path, self.image_list[nr])
        return src

    def pre_proc_func(self, sample_list):
        for index in sample_list:
            image_name = self.image_list[index]
            src = os.path.join(self.dataset_path, image_name)
            dst = os.path.join(self.cache_path, image_name)
            if not os.path.exists(dst + ".npy"):
                processed = self.pre_process(src, need_transpose=self.need_transpose, dims=self.image_size)
                np.save(dst, processed)
        return 0

class PostProcessCoco:
    """
    Post processing for tensorflow yolov3
    """
    def __init__(self):
        self.results = []
        self.good = 0
        self.total = 0
        self.content_ids = []
        # args
        self.num_class = 80
        self.max_boxes = 100
        self.score_thresh = 0.5
        self.nms_thresh = 0.55
        self.anchors = np.array([[116, 90, 156, 198, 373, 326], [30, 61, 62, 45, 59, 119], [10., 13, 16, 30, 33, 23]]).reshape(3, 3, 2)

    def set_datasets(self, datasets):
        self.datasets = datasets

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        #for predict_item in DataCenter.predict_list:
        for predict_item in self.datasets.prediction_items:
            lables = self.datasets.label_list[predict_item.idx_list]
            pred = predict_item.predictdata
            self.post_proc(pred, predict_item.idx_list, expected=lables)

        # 获取准确率信息并返回
        self.coco_eval_get_mAP()
        return 0.7

    def decode_feature_map(self, img_size, inputs):
        res_boxes = []
        res_scores = []
        for i, feature_map in enumerate(inputs):      # 一次只能对一个特征层的输出进行解码操作
            # NOTE: size in [h, w] format! don't get messed up!
            grid_size = feature_map.shape[1:3]
            # the downscale ratio in height and weight
            ratio = np.array([img_size[0] / grid_size[0], img_size[1] / grid_size[1]], np.float)

            rescaled_anchors = [(anchor[0] / ratio[1], anchor[1] / ratio[0]) for anchor in self.anchors[i]]
            
            feature_map.reshape(-1, grid_size[0], grid_size[1], 3, 5+self.num_class)

            box_centers = feature_map[..., :2]
            box_sizes = feature_map[..., 2:4]
            confidence = utils.sigmoid(feature_map[..., 4:5])
            prob = utils.sigmoid(feature_map[..., 5:])

            box_centers = utils.sigmoid(box_centers)

            x_y_offset = utils._make_grid(grid_size[0], grid_size[1])
            #print("xy offset is ", x_y_offset)
            # get the absolute box coordinates on the feature_map 
            box_centers = box_centers + x_y_offset
            # rescale to the original image scale
            box_centers = box_centers * ratio[::-1]

            # avoid getting possible nan value with tf.clip_by_value
            box_sizes = np.exp(box_sizes) * rescaled_anchors
            # box_sizes = tf.clip_by_value(tf.exp(box_sizes), 1e-9, 100) * rescaled_anchors
            # rescale to the original image scale
            box_sizes = box_sizes * ratio[::-1]

            # print("lcm debug box_centers:", box_centers.shape, box_centers)
            # print("lcm debug box_sizes:", box_sizes.shape, box_sizes)

            bb = np.concatenate((box_centers, box_sizes, confidence), axis=-1)
            #print("lcm debug bb:{}", bb)

            boxes = np.zeros_like(feature_map[..., 0:4])
            #print("lcm debug bc:", box_centers.shape, box_sizes.shape, boxes.shape)

            # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
            boxes[..., 0:1] = box_centers[..., 0:1] - box_sizes[..., 0:1] / 2  # top left x
            boxes[..., 1:2] = box_centers[..., 1:2] - box_sizes[..., 1:2] / 2  # top left y
            boxes[..., 2:3] = box_centers[..., 0:1] + box_sizes[..., 0:1] / 2  # bottom right x
            boxes[..., 3:4] = box_centers[..., 1:2] + box_sizes[..., 1:2] / 2  # bottom right y
            #bounds[..., 4:5] = confidence

            scores = confidence * prob
            boxes = boxes.reshape(-1, 4)
            scores = scores.reshape(-1, self.num_class)

            res_boxes.append(boxes)
            res_scores.append(scores)
            # print("lcm debug bc: re", i, box_centers.shape, box_sizes.shape, boxes.shape, scores.shape, boxes.shape)

        return np.concatenate(res_boxes, 0), np.concatenate(res_scores, 0)

    def append_result_info(self, idx, ids, expected, detection_boxes, scores, detection_classes):
            height, width = self.datasets.image_sizes[ids[idx]]

            resize_ratio_w = 416.0 / width
            resize_ratio_h = 416.0 / height
            # print("lcm debug ratio w:{} h:{} oriw:{} orih:{}".format(
            #     resize_ratio_w, resize_ratio_h, width, height))

            # print("lcm debug nms out and scale detection_boxes:{}", detection_boxes)

            expected_classes = expected[idx][0]

            for detection in range(0, len(scores)):
                if scores[detection] < 0.05:
                    break
                detection_class = int(detection_classes[detection]) + 1

                if detection_class in expected_classes:
                    self.good += 1
                x0, y0, x1, y1 = detection_boxes[detection]
                x0 = x0 / resize_ratio_w
                x1 = x1 / resize_ratio_w
                y0 = y0 / resize_ratio_h
                y1 = y1 / resize_ratio_h

                bw = x1 - x0
                bh = y1 - y0
    
                # comes from model as:  0=xmax 1=ymax 2=xmin 3=ymin
                image_id = self.datasets.image_ids[ids[idx]]

                # pycoco wants {imageID,x1,y1,w,h,score,class}
                t_dict = {"image_id": -1, "category_id": -1, "bbox": [], "score": 0}
                t_dict['image_id'] = int(image_id)
                t_dict['category_id'] = detection_class
                t_dict['bbox'] = [int(i) for i in [x0, y0, bw, bh]]
                t_dict['score'] = float(scores[detection])
                print("detection_class:{} expected:{} result:{}".format(detection_class, expected_classes, t_dict))
                self.results.append(t_dict)

                self.total += 1

    def coco_eval_get_mAP(self):
        image_ids = list(set([r["image_id"] for r in self.results]))
        cocoGt = COCO(self.datasets.annotation_file)
        cocoDt = cocoGt.loadRes(self.results)
        cocoEval = COCOeval(cocoGt, cocoDt, iouType='bbox')
        cocoEval.params.imgIds = image_ids
        print("lcm debug get accuray afile:{} results:{} image_ids:{}".format(self.datasets.annotation_file, self.results, image_ids))
        cocoEval.evaluate()
        cocoEval.accumulate()
        cocoEval.summarize()
        print("lcm debug mAP:", cocoEval.stats[0])
        print("lcm debug status:", cocoEval.stats)
        return cocoEval.stats[0]

class PostProcessCocoTf(PostProcessCoco):
    """
    Post processing for yolo
    """
    def __init__(self):
        super().__init__()

    def post_proc(self, results, ids, expected=None, result_dict=None):
        # results come as:
        #   detection_scores, detection_boxes

        # batch size
        bs = len(results[0])
        for idx in range(0, bs):

            scores_ = results[0][idx]
            boxes_ = results[1][idx]
            detection_boxes, scores, detection_classes = utils.cpu_nms(boxes_, scores_, self.num_class, self.max_boxes, self.score_thresh, self.nms_thresh)
            print("lcm debug nms out detection_boxes:{}", detection_boxes)
            print("lcm debug nms out scores:{}", scores)
            print("lcm debug nms out detection_classes:{}", detection_classes)

            self.append_result_info(idx, ids, expected, detection_boxes, scores, detection_classes)

class PostProcessCocoTf_featuremap(PostProcessCoco):
    """
    Post processing required by ssd-resnet34 / pytorch
    """
    def __init__(self):
        super().__init__()

    def post_proc(self, results, ids, expected=None, result_dict=None):
        # results come as:
        # batch size
        bs = len(results[0])
        for idx in range(0, bs):
            res = []
            print("lcm debug shape", results[0][idx].shape, results[1][idx].shape, results[2][idx].shape, self.datasets.image_sizes[ids[idx]])
            res.append(results[0][idx].reshape(-1, 13, 13, 3, 85))
            res.append(results[1][idx].reshape(-1, 26, 26, 3, 85))
            res.append(results[2][idx].reshape(-1, 52, 52, 3, 85))

            boxes_ , scores_ = self.decode_feature_map((416, 416), res)

            detection_boxes, scores, detection_classes = utils.cpu_nms(boxes_, scores_, self.num_class, self.max_boxes, self.score_thresh, self.nms_thresh)
            print("lcm debug nms out detection_boxes:{}", detection_boxes)
            print("lcm debug nms out scores:{}", scores)
            print("lcm debug nms out detection_classes:{}", detection_classes)

            self.append_result_info(idx, ids, expected, detection_boxes, scores, detection_classes)
