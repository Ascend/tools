import numpy as np
import cv2

def center_crop(img, out_height, out_width):
        height, width, _ = img.shape
        left = int((width - out_width) / 2)
        right = int((width + out_width) / 2)
        top = int((height - out_height) / 2)
        bottom = int((height + out_height) / 2)
        img = img[top:bottom, left:right]
        return img

def resize_with_aspectratio(img, out_height, out_width, scale=87.5, inter_pol=cv2.INTER_LINEAR):
    height, width, _ = img.shape
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

def preprocess_img(img, output_image_size=[224, 224], target_format="NHWC", normalize=True):
    img = np.asarray(bytearray(img), dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    output_height, output_width = output_image_size
    cv2_interpol = cv2.INTER_AREA
    img = resize_with_aspectratio(img, output_height, output_width, inter_pol=cv2_interpol)
    img = center_crop(img, output_height, output_width)
    img = np.asarray(img, dtype='float32')
    # normalize image
    if normalize:
        means = np.array([123.68, 116.78, 103.94], dtype=np.float32)
        img -= means
    # transpose if needed
    if target_format == "NCHW":
        img = img.transpose([2, 0, 1])
    elif target_format == "NHWC":
        pass
    else:
        print("Wrong image format!")
    return img

# 待完善
def pre_process_coco_tf_yolov3(img, dims=None, need_transpose=False):
    import mindx.sdk as sdk
    device_id = 0
    image_path = img
    
    #image = sdk.image(img)
    #image = image.to_device(device_id)

    image = sdk.image(image_path, device_id)

    resize_img = sdk.dvpp.resize(image, height=416, width=416)
    print("resize img:{}".format(resize_img))
    tensor = resize_img.get_tensor()
    tensor.to_host()
    array = np.array(tensor)
    return array

def sigmoid(x):
    return 1.0/(1+np.exp(-x))

def _make_grid(nx=20, ny=20):
    xv, yv = np.meshgrid(np.arange(nx), np.arange(ny))
    return np.stack((xv, yv), 2).reshape((ny, nx, 1, 2)).astype(np.float)

def py_nms(boxes, scores, max_boxes=50, iou_thresh=0.5):
    """
    Pure Python NMS baseline.

    Arguments: boxes: shape of [-1, 4], the value of '-1' means that dont know the
                      exact number of boxes
               scores: shape of [-1,]
               max_boxes: representing the maximum of boxes to be selected by non_max_suppression
               iou_thresh: representing iou_threshold for deciding to keep boxes
    """
    assert boxes.shape[1] == 4 and len(scores.shape) == 1

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        #print(areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= iou_thresh)[0]
        order = order[inds + 1]

    return keep[:max_boxes]

import numpy as np 
np.set_printoptions(threshold=np.inf)
np.set_printoptions(precision=3, suppress=True)

def cpu_nms(boxes, scores, num_classes, max_boxes=50, score_thresh=0.5, iou_thresh=0.5):
    """
    Perform NMS on CPU.
    Arguments:
        boxes: shape [1, 10647, 4]
        scores: shape [1, 10647, num_classes]
    """

    boxes = boxes.reshape(-1, 4)
    scores = scores.reshape(-1, num_classes)
    # Picked bounding boxes
    picked_boxes, picked_score, picked_label = [], [], []

    #print("lcm debug boxes:{}".format(boxes))
    #print("lcm debug scores:{}".format(scores))

    for i in range(num_classes):
        indices = np.where(scores[:,i] >= score_thresh)
        filter_boxes = boxes[indices]
        filter_scores = scores[:,i][indices]
        if len(filter_boxes) == 0:
            continue
        # do non_max_suppression on the cpu
        indices = py_nms(filter_boxes, filter_scores,
                         max_boxes=max_boxes, iou_thresh=iou_thresh)
        #print("lcm debug i:{} indices:{} filer_box:{} filter_score：{} label:{}".format(
        #    i, indices, filter_boxes[indices], filter_scores[indices], np.ones(len(indices), dtype='int32')*i))
        picked_boxes.append(filter_boxes[indices])
        picked_score.append(filter_scores[indices])
        picked_label.append(np.ones(len(indices), dtype='int32')*i)
    if len(picked_boxes) == 0:
        return None, None, None

    boxes = np.concatenate(picked_boxes, axis=0)
    score = np.concatenate(picked_score, axis=0)
    label = np.concatenate(picked_label, axis=0)

    return boxes, score, label

