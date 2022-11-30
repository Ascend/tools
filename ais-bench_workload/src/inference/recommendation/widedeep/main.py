# -*- coding:utf-8 -*-
import argparse
import logging
import os
import sys

import core.utils as utils
from backendbase import create_backend_instance
from loadgen_interface import run_loadgen_base

import outbrain
from outbrain import Outbrain

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

SUPPORTED_PROFILES = {
    "defaults": {
    },
    "resnet50_pytorch": {
        "dataset_name": "imagenet",
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
    parser.add_argument("--batchsize", default=1, type=int, help="max batch size in a single inference")

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

    datasets = Outbrain(args.cache_path)
    datasets.args = args

    run_loadgen_base(datasets, datasets.predict_proc_func, datasets.post_proc_func, args)


