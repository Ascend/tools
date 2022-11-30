
import os
import sys
import json
import argparse
import numpy as np

def get_topk_list(K, origin_list):
    temp = sorted(origin_list)[-K:]
    temp.reverse()
    res = []
    print("temp:", temp)
    for ele in temp:
        res.append((origin_list.index(ele), ele))
    return res

def get_file_info(file):
    info = None
    with open(file, 'rb') as f:
        info = json.load(f)
    return info

def analyse_plog(args):
    info = get_file_info(args.summary_path)
    


def analyse_topk_times(args):
    info = get_file_info(args.summary_path)

    #print("npu_compute_time_list:{}".format(npu_compute_time_list))
    #print("npu_compute_time_list:{}".format(info["npu_compute_time_list"]))

    times = info["npu_compute_time_list"]
    K = 5
    topk_list = get_topk_list(K, times)
    print("K Maximum with indices : " + str(topk_list))
    print("infer count:{} mean:{} max:{} min:{}".format(len(times), np.mean(times), np.max(times), np.min(times)))
    print("max-min  rate:{}% ".format((np.max(times) - np.min(times)) * 100.0 / np.min(times)))
    print("max-mean rate:{}%".format((np.max(times) - np.mean(times)) * 100.0 / np.mean(times)))

    topk_index = [ i[0] for i in topk_list ]
    print(topk_index)
    if args.output != None:
        with open("{}/topk_index.json".format(args.output), "w") as f:
            f.write(json.dumps(topk_index))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary_path", help="the sumary path")
    parser.add_argument("--plog", help="plog path")
    parser.add_argument("--output", default=None, help="the output path")
    parser.add_argument("--mode", default="times", choices=["times", "plog"], help="mode (times or plog)")
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    if args.mode == "times":
        analyse_topk_times(args)
    elif args.mode == "plog":
        analyse_plog(args)
    else:
        print("error mode:{}".format(args.mode))
        sys.exit(-1)