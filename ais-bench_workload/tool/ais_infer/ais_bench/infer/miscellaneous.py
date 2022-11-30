import os
import sys
import json
import numpy as np
import itertools

from ais_bench.infer.utils import logger

def get_modules_version(name):
    try:
        import pkg_resources
        pkg = pkg_resources.get_distribution(name)
        return pkg.version
    except:
        return None

def version_check(args):
    aclruntime_version = get_modules_version('aclruntime')
    if aclruntime_version == None or aclruntime_version == "0.0.1":
        logger.warning("aclruntime version:{} is lower please update aclruntime follow any one method".format(aclruntime_version))
        logger.warning("1. visit https://github.com/Ascend/tools/tree/master/ais-bench_workload/tool/ais_infer to install")
        logger.warning("2. or run cmd: pip3  install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_infer/backend' to install")
        # set old run mode to run ok
        args.run_mode = "tensor"

def get_acl_json_path(args):
    """
    get acl json path. when args.profiler is true or args.dump is True, create relative acl.json , default current folder
    """
    if args.acl_json_path is not None:
        return args.acl_json_path
    if not args.profiler and not args.dump:
        return None

    output_json_dict = {}
    if args.profiler:
        output_json_dict = {"profiler": {"switch": "on", "aicpu": "on", "output": "", "aic_metrics": ""}}
        out_profiler_path = os.path.join(args.output, "profiler")

        if not os.path.exists(out_profiler_path):
            os.mkdir(out_profiler_path)
        output_json_dict["profiler"]["output"] = out_profiler_path
    elif args.dump:
        output_json_dict = {"dump": {"dump_path": "", "dump_mode": "output", "dump_list": [{"model_name": ""}]}}
        out_dump_path = os.path.join(args.output, "dump")

        if not os.path.exists(out_dump_path):
            os.mkdir(out_dump_path)

        model_name = args.model.split("/")[-1]
        output_json_dict["dump"]["dump_path"] = out_dump_path
        output_json_dict["dump"]["dump_list"][0]["model_name"] = model_name.split('.')[0]

    out_json_file_path = os.path.join(args.output, "acl.json")
    with open(out_json_file_path, "w") as f:
        json.dump(output_json_dict, f, indent=4, separators=(", ", ": "), sort_keys=True)
    return out_json_file_path

def get_range_list(ranges):
    elems = ranges.split(';')
    info_list = []
    for elem in elems:
        shapes = []
        name, shapestr = elem.split(':')
        for content in shapestr.split(','):
            step = 1
            if '~' in content:
                start = int(content.split('~')[0])
                end = int(content.split('~')[1])
                step = int(content.split('~')[2]) if len(content.split('~')) == 3 else 1
                ranges = [ str(i) for i in range(start, end+1, step)]
            elif '-' in content :
                ranges = content.split('-')
            else:
                start = int(content)
                ranges = [ str(start) ]
            shapes.append(ranges)
            logger.debug("content:{} get range{}".format(content, ranges))
        shape_list = [ ','.join(s) for s in list(itertools.product(*shapes)) ]
        info = [ "{}:{}".format(name, s) for s in shape_list ]
        info_list.append(info)
        logger.debug("name:{} shapes:{} info:{}".format(name, shapes, info))
    
    res = [ ';'.join(s) for s in list(itertools.product(*info_list)) ]
    logger.debug("range list:{}".format(res))
    return res

# get dymshape list from input_ranges
# input_ranges can be a string like "name1:1,3,224,224;name2:1,600" or file
def get_dymshape_list(input_ranges):
    ranges_list = []
    if os.path.isfile(input_ranges):
        with open(input_ranges, 'rt', encoding='utf-8') as finfo:
            line = finfo.readline()
            while line:
                line = line.rstrip('\n')
                ranges_list.append(line)
                line = finfo.readline()
    else:
        ranges_list.append(input_ranges)

    dymshape_list = []
    for ranges in ranges_list:
        dymshape_list.extend(get_range_list(ranges))
    return dymshape_list

# get throughput from out log
def get_throughtput_from_log(log_path):
    if os.path.exists(log_path) == False:
        return "Failed", 0
    try:
        cmd = "cat {} | grep throughput".format(log_path)
        cmd = cmd + " | awk '{print $NF}'"
        outval = os.popen(cmd).read()
        if outval == "":
            return "Failed", 0
        throughtput = float(outval)
        return "OK", throughtput
    except Exception as e:
        logger.warning("get throughtput failed e:{}".format(e))
        return "Failed", 0

def dymshape_range_run(args):
    dymshape_list = get_dymshape_list(args.dymShape_range)
    results = []
    log_path = "./dym.log" if args.output == None else args.output + "/dym.log"
    for dymshape in dymshape_list:
        # get first inargs shape[0] as batchsize
        batchsize = int(dymshape.split(':')[1].split(",")[0])
        cmd = "rm -rf {};{} {} {}".format(log_path, sys.executable, ' '.join(sys.argv),
            "--dymShape={} --batchsize={} | tee {}".format(dymshape, batchsize, log_path))
        result = { "dymshape" : dymshape, "batchsize": batchsize, "cmd": cmd, "result": "Failed", "throughput" : 0 }
        logger.debug("cmd:{}".format(cmd))
        os.system(cmd)
        result["result"], result["throughput"] = get_throughtput_from_log(log_path)
        logger.info("dymshape:{} end run result:{}".format(dymshape, result["result"]))
        results.append(result)
    
    tlist = [ result["throughput"] for result in results if result["result"] == "OK" ]
    logger.info("-----------------dyshape_range Performance Summary------------------")
    logger.info("run_count:{} success_count:{} avg_throughput:{}".format(
        len(results), len(tlist), np.mean(tlist)))
    results.sort(key=lambda x: x['throughput'], reverse=True)
    for i, result in enumerate(results):
        logger.info("{} dymshape:{} bs:{} result:{} throughput:{}".format(
            i, result["dymshape"],result["batchsize"], result["result"], result["throughput"]))
    logger.info("------------------------------------------------------")
