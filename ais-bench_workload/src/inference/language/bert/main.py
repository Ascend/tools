import argparse
import logging
import os
import sys

from backendbase import create_backend_instance
from loadgen_interface import run_loadgen

import masked_lm
import squad

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")

# the datasets we support
SUPPORTED_DATASETS = {
    "squad": (squad.Squad, None, squad.PostProcessSquad()),
    "masked_lm": (masked_lm.MaskedLM, None, masked_lm.PostProcessMaskedLM())
}

SUPPORTED_PROFILES = {
    "defaults": {
        "dataset_name": "squad",
        "backend": "acl",
        "inputs": None,
        "outputs": None,
    },

    # bert squad
    "bert_large_squad": {
        "dataset_name": "squad",
        "backend": "acl",
    },
    # bert mask lm
    "bert_large_masked_lm": {
        "dataset_name": "masked_lm",
        "backend": "acl",
    },
}


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=SUPPORTED_PROFILES.keys(), help="standard profiles")
    parser.add_argument("--backend", help="runtime to use")
    parser.add_argument("--model", required=True, help="model file")
    parser.add_argument("--dataset_path", required=True, help="path to the dataset")
    parser.add_argument("--cache_path", default=os.getcwd(), help="cache path")
    parser.add_argument("--debug", action="store_true", help="debug, turn traces on")
    parser.add_argument("--device_id", type=int, default=0, help="specify the device_id to use for infering")
    parser.add_argument("--query_arrival_mode",
        choices=["continuous", "periodic", "poison_distribute", "offline", "mixed"],
        default="offline", help="query_arrival_mode")
    parser.add_argument("--maxloadsamples_count", type=check_positive, default=None, help="dataset items to use")
    parser.add_argument('--count', type=check_positive, default=None,  help="positive integer, select dataset items count, default full data.")
    parser.add_argument("--vocab_path", required=True, help="vocab file")

    parser.add_argument("--batchsize", default=1, type=int, help="max batch size in a single inference")
    parser.add_argument("--dymBatch", type=int, default=0, help="dynamic batch size param, such as --dymBatch 2")
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
        if hasattr(args, k) == False or getattr(args, k) is None:
            setattr(args, k, v)
    return args

if __name__ == "__main__":
    args = get_args()

    print("begin args:", args)

    # dataset to use
    wanted_dataset, preproc, postproc = SUPPORTED_DATASETS[args.dataset_name]
    datasets = wanted_dataset(args.dataset_path, args.vocab_path, args.cache_path, args.count)

    # find backend
    backend = create_backend_instance(args.backend, args)
    backend.set_datasets(datasets)

    if hasattr(postproc, "set_datasets"):
        postproc.set_datasets(datasets)
    if hasattr(postproc, "set_backend"):
        postproc.set_backend(backend)

    log.debug("backend:{} model_path:{} input:{} output:{}".format(backend, args.model, args.inputs, args.outputs))

    run_loadgen(datasets, backend, postproc, args)
