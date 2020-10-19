import tensorflow as tf
import numpy as np
import os
import sys
import ast

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../config')))
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../../../../utils'))
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../../../../utils/atlasboost'))


import data_loader as dl
import model as ml
import hyper_param as hp
import layers as ly
import logger as lg
import trainer as tr
import create_session as cs

print(os.getcwd())

import argparse

#import hwlog
from benchmark_log import hwlog
from benchmark_log.basic_utils import get_environment_info
from benchmark_log.basic_utils import get_model_parameter


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    

    parser.add_argument('--rank_size', default=1,type=int,
                        help="""number of NPUs  to use.""")

    # mode and parameters related 
    parser.add_argument('--mode', default='train_and_evaluate',
                        help="""mode to run the program  e.g. train, evaluate, and
                        train_and_evaluate""")
    parser.add_argument('--max_train_steps', default=100,type=int,
                        help="""max steps to train""")
    parser.add_argument('--iterations_per_loop', default=10, type=int,
                        help="""the number of steps in devices for each iteration""")
    parser.add_argument('--max_epochs', default=None, type=int,
                        help="""total epochs for training""")
    parser.add_argument('--epochs_between_evals', default=5, type=int,
                        help="""the interval between train and evaluation , only meaningful
                        when the mode is train_and_evaluate""")

    # dataset
    parser.add_argument('--data_dir', default='path/data',
                        help="""directory of dataset.""")

    # path for evaluation
    parser.add_argument('--eval_dir', default='path/eval',
                        help="""directory to evaluate.""")

    parser.add_argument('--dtype', default=tf.float32,
                        help="""data type of inputs.""")
    parser.add_argument('--use_nesterov', default=True, type=ast.literal_eval,
                        help="""whether to use Nesterov in optimizer""")
    parser.add_argument('--label_smoothing', default=0.1, type=float,
                        help="""label smoothing factor""")
    parser.add_argument('--weight_decay', default=0.0001,
                        help="""weight decay for regularization""")
    parser.add_argument('--batch_size', default=32, type=int,
                        help="""batch size for one NPU""")

    # learning rate and momentum
    parser.add_argument('--lr', default=0.01, type=float,
                        help="""initial learning rate""")
    parser.add_argument('--T_max', default=150, type=int,
                        help="""T_max for cosing_annealing learning rate""")
    parser.add_argument('--momentum', default=0.9, type=float,
                        help="""momentum used in optimizer.""")

    # display frequency
    parser.add_argument('--display_every', default=1, type=int,
                        help="""the frequency to display info""")

    # log file
    parser.add_argument('--log_name', default='vgg16.log',
                        help="""name of log file""")
    parser.add_argument('--log_dir', default='./model_1p',
                        help="""log directory""")
 
    args, unknown_args = parser.parse_known_args()
    if len(unknown_args) > 0:
        for bad_arg in unknown_args:
            print("ERROR: Unknown command line arg: %s" % bad_arg)
        raise ValueError("Invalid command line arg(s)")

    return args


def main():

    args = parse_args()
    args.global_batch_size = args.batch_size * args.rank_size

    session = cs.CreateSession()
    data = dl.DataLoader(args)    
    hyper_param = hp.HyperParams(args)
    layers = ly.Layers() 
    logger = lg.LogSessionRunHook(args)
    model = ml.Model(args, data, hyper_param, layers, logger)
   
    trainer = tr.Trainer(session, args, data, model, logger)

    if args.mode == 'train':
        trainer.train()
    elif args.mode == 'evaluate':
        trainer.evaluate()
    elif args.mode == 'train_and_evaluate':
        trainer.train_and_evaluate()
    else:
        raise ValueError("Invalid mode.")


if __name__ == '__main__':

    hwlog.ROOT_DIR = os.path.split(os.path.abspath(__file__))[0]
    cpu_info, npu_info, framework_info, os_info, benchmark_version = get_environment_info("tensorflow")
    config_info = get_model_parameter("tensorflow_config")
    initinal_data = {"base_lr": 0.01, "dataset": "imagenet1024", "optimizer": "SGD", "loss_scale": 512,
                     "batchsize": 32}
    hwlog.remark_print(key=hwlog.CPU_INFO, value=cpu_info)
    hwlog.remark_print(key=hwlog.NPU_INFO, value=npu_info)
    hwlog.remark_print(key=hwlog.OS_INFO, value=os_info)
    hwlog.remark_print(key=hwlog.FRAMEWORK_INFO, value=framework_info)
    hwlog.remark_print(key=hwlog.BENCHMARK_VERSION, value=benchmark_version)
    hwlog.remark_print(key=hwlog.CONFIG_INFO, value=config_info)
    hwlog.remark_print(key=hwlog.BASE_LR, value=initinal_data.get("base_lr"))
    hwlog.remark_print(key=hwlog.DATASET, value=initinal_data.get("dataset"))
    hwlog.remark_print(key=hwlog.OPT_NAME, value=initinal_data.get("optimizer"))
    hwlog.remark_print(key=hwlog.LOSS_SCALE, value=initinal_data.get("loss_scale"))
    hwlog.remark_print(key=hwlog.INPUT_BATCH_SIZE, value=initinal_data.get("batchsize"))

    tf.logging.set_verbosity(tf.logging.INFO)
    main()

