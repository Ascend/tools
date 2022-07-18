import argparse
import logging
import os
import sys

import core.utils as utils
from backendbase import create_backend_instance
from loadgen_interface import run_loadgen

import coco
import imagenet
import imagenet_set
import voc
import voc_deeplabv3

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

# the datasets we support
SUPPORTED_DATASETS = {
    "imagenet":
        (imagenet.Imagenet, utils.preprocess_img, imagenet.PostProcessCommon(offset=-1),
        {"image_size": [224, 224]}),
    "imagenet-resnet50":
        (imagenet_set.ImagenetSet, None, imagenet_set.PostProcess(offset=0),
        {"image_size": [224, 224]}),
    "imagenet-resnet101":
        (imagenet_set.ImagenetSet, None, imagenet_set.PostProcess(offset=0),
        {"image_size": [224, 224]}),
    "imagenet-inceptionv3":
        (imagenet_set.ImagenetSet, None, imagenet_set.PostProcess(offset=0),
        {"image_size": [299, 299]}),
    "imagenet-acl-vgg16":
        (imagenet.Imagenet, utils.preprocess_img, imagenet.PostProcessArgMax(offset=0),
        {"image_size": [224, 224]}),
    "coco-416-tf-yolov3":
        (coco.Coco, utils.pre_process_coco_tf_yolov3, coco.PostProcessCocoTf(),
        {"image_size": [416, 416, 3], "use_label_map": True}),
    "coco-416-tf-yolov3-featuremap":
        (coco.Coco, utils.pre_process_coco_tf_yolov3, coco.PostProcessCocoTf_featuremap(),
        {"image_size": [416, 416, 3], "use_label_map": True}),
    "voc2012-yolov3":
        (voc.VOC, None, voc.PostProcessCommon(), {"image_size": [416, 416, 3]}),
    "voc2012-deeplabv3":
        (voc_deeplabv3.VOC, None, voc_deeplabv3.PostProcessBase(), {"image_size": [416, 416, 3]}),
}

# pre-defined command line options so simplify things. They are used as defaults and can be
# overwritten from command line

SUPPORTED_PROFILES = {
    "defaults": {
        "data_format": "NCHW",
        "normalize": True,
        "inputs": None,
        "outputs": None,
        "tag": None
    },

    "resnet50_pytorch": {
        "dataset_name": "imagenet",
        "backend": "acl",
    },
    "resnet50_onnx": {
        "dataset_name": "imagenet-resnet50",
        "tag": "resnet",
        "backend": "acl",
    },
    "resnet101_onnx": {
        "dataset_name": "imagenet-resnet101",
        "tag": "resnet",
        "backend": "acl",
    },
    "inceptionv3_onnx": {
        "dataset_name": "imagenet-inceptionv3",
        "tag": "inception",
        "backend": "acl",
    },
    "vgg16-acl": {
        "dataset_name": "imagenet_vgg16",
        "backend": "acl",
        "normalize": True,
    },
    "yolov3-acl": {
        "inputs": "image",
        "outputs": "0,1,2",
        "dataset_name": "coco-416-pt-yolov3",
        "backend": "acl",
    },
    "yolov3-tf32": {
        "inputs": "image",
        "outputs": "0,1",
        "dataset_name": "coco-416-tf-yolov3",
        "backend": "acl",
    },
    "yolov3-tf32-featuremap": {
        "inputs": "image",
        "outputs": "0,1,2",
        "dataset_name": "coco-416-tf-yolov3-featuremap",
        "backend": "acl",
        "data_format": "NCHW",
    },
    "yolov3-caffe_voc2012": {
        "dataset_name": "voc2012-yolov3",
        "backend": "acl",
    },
    "deeplabv3-tf_voc2012": {
        "dataset_name": "voc2012-deeplabv3",
        "backend": "acl",
    },

}

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def get_args():
    """Parse commandline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=SUPPORTED_PROFILES.keys(), help="standard profiles")
    parser.add_argument("--backend", help="runtime to use")
    parser.add_argument("--model", required=True, help="model file")
    parser.add_argument("--dataset_path", required=True, help="path to the data")
    parser.add_argument("--cache_path", default=os.getcwd(), help="cache path")
    parser.add_argument("--debug", action="store_true", help="debug, turn traces on")
    parser.add_argument("--device_id", type=int, default=0, help="specify the device_id to use for infering")
    parser.add_argument("--query_arrival_mode",
        choices=["continuous", "periodic", "poison_distribute", "offline", "mixed"],
        default="offline", help="query_arrival_mode")
    parser.add_argument("--maxloadsamples_count", type=check_positive, default=None, help="dataset items to use")
    parser.add_argument('--count', type=check_positive, default=None,  help="positive integer, select dataset items count, default full data.")
    parser.add_argument("--dataset_list", help="path to the dataset list")

    parser.add_argument("--batchsize", default=1, type=int, help="max batch size in a single inference")
    
    parser.add_argument("--dymBatch", type=int, default=0, help="dynamic batch size params  such as --dymBatch 2")
    
    
    parser.add_argument("--dymHW", type=str, default=None, help="dynamic image size param, such as --dymHW \"300,500\"")
    parser.add_argument("--dymDims", type=str, default=None, help="dynamic dims param, such as --dymDims \"data:1,600;img_info:1,600\"")
    parser.add_argument("--dymShape", type=str, help="dynamic hape param, such as --dymShape \"data:1,600;img_info:1,600\"")
    parser.add_argument("--outputSize", type=str, default=None, help="output size for dynamic shape mode")

    args = parser.parse_args()
    defaults = SUPPORTED_PROFILES["defaults"]

    if args.profile:
        profile = SUPPORTED_PROFILES[args.profile]
        defaults.update(profile)
    for k, v in defaults.items():
        if hasattr(args, k) is False or getattr(args, k) is None:
            setattr(args, k, v)
    return args

if __name__ == "__main__":
    args = get_args()
    print("begin args:", args)

    # dataset to use
    wanted_dataset, preproc, postproc, kwargs = SUPPORTED_DATASETS[args.dataset_name]
    datasets = wanted_dataset(dataset_path=args.dataset_path,
                        image_list=args.dataset_list,
                        data_format=args.data_format,
                        pre_process=preproc,
                        cache_path=args.cache_path,
                        count=args.count,
                        normalize=args.normalize,
                        tag=args.tag,
                        **kwargs)

    # find backend
    backend = create_backend_instance(args.backend, args)

    backend.set_datasets(datasets)
    if hasattr(postproc, "set_datasets"):
        postproc.set_datasets(datasets)
    if hasattr(postproc, "set_backend"):
        postproc.set_backend(backend)

    log.debug("backend:{} model_path:{} input:{} output:{}".format(backend, args.model, args.inputs, args.outputs))

    run_loadgen(datasets, backend, postproc, args)
