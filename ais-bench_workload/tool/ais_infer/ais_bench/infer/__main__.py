import argparse
import logging
import os
import sys
import time
import shutil

from tqdm import tqdm

from ais_bench.infer.interface import InferSession, MemorySummary
from ais_bench.infer.io_oprations import (create_infileslist_from_inputs_list,
                                    create_intensors_from_infileslist,
                                    get_narray_from_files_list,
                                    get_tensor_from_files_list,
                                    convert_real_files,
                                    pure_infer_fake_file, save_tensors_to_file)
from ais_bench.infer.summary import summary
from ais_bench.infer.utils import logger
from ais_bench.infer.miscellaneous import dymshape_range_run, get_acl_json_path, version_check

def set_session_options(session, args):
    # 增加校验
    if args.dymBatch != 0:
        session.set_dynamic_batchsize(args.dymBatch)
    elif args.dymHW !=None:
        hwstr = args.dymHW.split(",")
        session.set_dynamic_hw((int)(hwstr[0]), (int)(hwstr[1]))
    elif args.dymDims !=None:
        session.set_dynamic_dims(args.dymDims)
    elif args.dymShape !=None:
        session.set_dynamic_shape(args.dymShape)
    else:
        session.set_staticbatch()

    # 设置custom out tensors size
    if args.outputSize != None:
        customsizes = [int(n) for n in args.outputSize.split(',')]
        logger.debug("set customsize:{}".format(customsizes))
        session.set_custom_outsize(customsizes)

def init_inference_session(args):
    acl_json_path = get_acl_json_path(args)
    session = InferSession(args.device, args.model, acl_json_path, args.debug, args.loop)

    set_session_options(session, args)
    logger.debug("session info:{}".format(session.session))
    return session

def set_dymshape_shape(session, inputs):
    l = []
    intensors_desc = session.get_inputs()
    for i, input in enumerate(inputs):
        str_shape = [ str(shape) for shape in input.shape ]
        dyshape = "{}:{}".format(intensors_desc[i].name, ",".join(str_shape))
        l.append(dyshape)
    dyshapes = ';'.join(l)
    logger.debug("set dymshape shape:{}".format(dyshapes))
    session.set_dynamic_shape(dyshapes)

def set_dymdims_shape(session, inputs):
    l = []
    intensors_desc = session.get_inputs()
    for i, input in enumerate(inputs):
        str_shape = [ str(shape) for shape in input.shape ]
        dydim = "{}:{}".format(intensors_desc[i].name, ",".join(str_shape))
        l.append(dydim)
    dydims = ';'.join(l)
    logger.debug("set dymdims shape:{}".format(dydims))
    session.set_dynamic_dims(dydims)

def warmup(session, args, intensors_desc, infiles):
    # prepare input data
    infeeds = []
    for j, files in enumerate(infiles):
        if args.run_mode == "tensor":
            tensor = get_tensor_from_files_list(files, session, intensors_desc[j].realsize, args.pure_data_type, args.no_combine_tensor_mode)
            infeeds.append(tensor)
        else:
            narray = get_narray_from_files_list(files, intensors_desc[j].realsize, args.pure_data_type, args.no_combine_tensor_mode)
            infeeds.append(narray)
    session.set_loop_count(1)
    # warmup
    for i in range(args.warmup_count):
        outputs = run_inference(session, infeeds, out_array=True)

    session.set_loop_count(args.loop)

    # reset summary info
    summary.reset()
    session.reset_sumaryinfo()
    MemorySummary.reset()
    logger.info("warm up {} done".format(args.warmup_count))

def run_inference(session, inputs, out_array=False):
    if args.auto_set_dymshape_mode == True:
        set_dymshape_shape(session, inputs)
    elif args.auto_set_dymdims_mode == True:
        set_dymdims_shape(session, inputs)
    outputs = session.run(inputs, out_array)
    return outputs

# tensor to loop infer
def infer_loop_tensor_run(session, args, intensors_desc, infileslist, output_prefix):
    for i, infiles in enumerate(tqdm(infileslist, file=sys.stdout, desc='Inference tensor Processing')):
        intensors = []
        for j, files in enumerate(infiles):
            tensor = get_tensor_from_files_list(files, session, intensors_desc[j].realsize, args.pure_data_type, args.no_combine_tensor_mode)
            intensors.append(tensor)
        outputs = run_inference(session, intensors)
        session.convert_tensors_to_host(outputs)
        if output_prefix != None:
            save_tensors_to_file(outputs, output_prefix, infiles, args.outfmt, i, args.output_batchsize_axis)

# files to loop iner
def infer_loop_files_run(session, args, intensors_desc, infileslist, output_prefix):
    for i, infiles in enumerate(tqdm(infileslist, file=sys.stdout, desc='Inference files Processing')):
        intensors = []
        for j, files in enumerate(infiles):
            real_files = convert_real_files(files)  
            tensor = session.create_tensor_from_fileslist(intensors_desc[j], real_files)
            intensors.append(tensor)
        outputs = run_inference(session, intensors)
        session.convert_tensors_to_host(outputs)
        if output_prefix != None:
            save_tensors_to_file(outputs, output_prefix, infiles, args.outfmt, i, args.output_batchsize_axis)

# First prepare the data, then execute the reference, and then write the file uniformly
def infer_fulltensors_run(session, args, intensors_desc, infileslist, output_prefix):
    outtensors = []
    intensorslist = create_intensors_from_infileslist(infileslist, intensors_desc, session, args.pure_data_type, args.no_combine_tensor_mode)

    #for inputs in intensorslist:
    for inputs in tqdm(intensorslist, file=sys.stdout, desc='Inference Processing full'):
        outputs = run_inference(session, inputs)
        outtensors.append(outputs)

    for i, outputs in enumerate(outtensors):
        session.convert_tensors_to_host(outputs)
        if output_prefix != None:
            save_tensors_to_file(outputs, output_prefix, infileslist[i], args.outfmt, i, args.output_batchsize_axis)

# loop numpy array to infer
def infer_loop_array_run(session, args, intensors_desc, infileslist, output_prefix):
    for i, infiles in enumerate(tqdm(infileslist, file=sys.stdout, desc='Inference array Processing')):
        innarrays = []
        for j, files in enumerate(infiles):
            narray = get_narray_from_files_list(files, intensors_desc[j].realsize, args.pure_data_type)
            innarrays.append(narray)
        outputs = run_inference(session, innarrays)
        session.convert_tensors_to_host(outputs)
        if args.output != None:
            save_tensors_to_file(outputs, output_prefix, infiles, args.outfmt, i, args.output_batchsize_axis)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected true, 1, false, 0 with case insensitive.')

def check_positive_integer(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def check_nonnegative_integer(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid nonnegative int value" % value)
    return ivalue

def check_device_range_valid(value):
    ivalue = int(value)
    if ivalue < 0 and ivalue > 255:
        raise argparse.ArgumentTypeError("%s is invalid. valid value range is [0, 255]" % value)
    return ivalue

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", "--om", required=True, help="the path of the om model")
    parser.add_argument("--input", "-i", default=None, help="input file or dir")
    parser.add_argument("--output", "-o", default=None, help="Inference data output path. The inference results are output to the subdirectory named current date under given output path")
    parser.add_argument("--output_dirname", type=str, default=None, help="actual output directory name. Used with parameter output, cannot be used alone. The inference result is output to  subdirectory named by output_dirname under  output path. such as --output_dirname 'tmp', the final inference results are output to the folder of  {$output}/tmp")
    parser.add_argument("--outfmt", default="BIN", choices=["NPY", "BIN", "TXT"], help="Output file format (NPY or BIN or TXT)")
    parser.add_argument("--loop", "-r", type=check_positive_integer, default=1, help="the round of the PrueInfer.")
    parser.add_argument("--debug", type=str2bool, default=False, help="Debug switch,print model information")
    parser.add_argument("--device", "--device", type=check_device_range_valid, default=0, help="the NPU device ID to use.valid value range is [0, 255]")
    parser.add_argument("--dymBatch", type=int, default=0, help="dynamic batch size param，such as --dymBatch 2")
    parser.add_argument("--dymHW", type=str, default=None, help="dynamic image size param, such as --dymHW \"300,500\"")
    parser.add_argument("--dymDims", type=str, default=None, help="dynamic dims param, such as --dymDims \"data:1,600;img_info:1,600\"")
    parser.add_argument("--dymShape", type=str, default=None, help="dynamic shape param, such as --dymShape \"data:1,600;img_info:1,600\"")
    parser.add_argument("--outputSize", type=str, default=None, help="output size for dynamic shape mode")
    parser.add_argument("--auto_set_dymshape_mode", type=str2bool, default=False, help="auto_set_dymshape_mode")
    parser.add_argument("--auto_set_dymdims_mode", type=str2bool, default=False, help="auto_set_dymdims_mode")
    parser.add_argument("--batchsize", type=check_positive_integer, default=1, help="batch size of input tensor")
    parser.add_argument("--pure_data_type", type=str, default="zero", choices=["zero", "random"], help="null data type for pure inference(zero or random)")
    parser.add_argument("--profiler", type=str2bool, default=False, help="profiler switch")
    parser.add_argument("--dump", type=str2bool, default=False, help="dump switch")
    parser.add_argument("--acl_json_path", type=str, default=None, help="acl json path for profiling or dump")
    parser.add_argument("--output_batchsize_axis",  type=check_nonnegative_integer, default=0, help="splitting axis number when outputing tensor results, such as --output_batchsize_axis 12")
    parser.add_argument("--run_mode", type=str, default="array", choices=["array", "files", "tensor", "full"], help="run mode")
    parser.add_argument("--display_all_summary", type=str2bool, default=False, help="display all summary include h2d d2h info")
    parser.add_argument("--warmup_count",  type=check_nonnegative_integer, default=1, help="warmup count before inference")
    parser.add_argument("--dymShape_range", type=str, default=None, help="dynamic shape range, such as --dymShape_range \"data:1,600~700;img_info:1,600-700\"")
    args = parser.parse_args()

    if args.profiler is True and args.dump is True:
        logger.error("parameter --profiler cannot be true at the same time as parameter --dump, please check them!\n")
        raise RuntimeError('error bad parameters --profiler and --dump')

    if (args.profiler is True or args.dump is True) and (args.output is None):
        logger.error("when dump or profiler, miss output path, please check them!")
        raise RuntimeError('miss output parameter!')

    if args.auto_set_dymshape_mode == False and args.auto_set_dymdims_mode == False:
        args.no_combine_tensor_mode = False
    else:
        args.no_combine_tensor_mode = True

    if args.profiler is True and args.warmup_count != 0 and args.input != None:
        logger.info("profiler mode with input change warmup_count to 0")
        args.warmup_count = 0
    return args

def msprof_run_profiling(args):
    cmd = sys.executable + " " + ' '.join(sys.argv) + " --profiler=0 --warmup_count=0"
    msprof_cmd="{} --output={}/profiler --application=\"{}\" --sys-hardware-mem=on --sys-cpu-profiling=on --sys-profiling=on --sys-pid-profiling=on --dvpp-profiling=on --runtime-api=on --task-time=on --aicpu=on".format(
        msprof_bin, args.output, cmd)
    logger.info("msprof cmd:{} begin run".format(msprof_cmd))
    ret = os.system(msprof_cmd)
    logger.info("msprof cmd:{} end run ret:{}".format(msprof_cmd, ret))

def main(args):
    if args.debug == True:
        logger.setLevel(logging.DEBUG)

    session = init_inference_session(args)

    intensors_desc = session.get_inputs()

    if args.output != None:
        if args.output_dirname is None:
            timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
            output_prefix = os.path.join(args.output, timestr)
        else:
            output_prefix = os.path.join(args.output, args.output_dirname)
        if not os.path.exists(output_prefix):
            os.makedirs(output_prefix, 0o755)
        logger.info("output path:{}".format(output_prefix))
    else:
        output_prefix = None

    inputs_list = [] if args.input == None else args.input.split(',')

    # create infiles list accord inputs list
    if len(inputs_list) == 0:
        # Pure reference scenario. Create input zero data
        infileslist = [[ [ pure_infer_fake_file ] for index in intensors_desc ]]
    else:
        infileslist = create_infileslist_from_inputs_list(inputs_list, intensors_desc, args.no_combine_tensor_mode)

    warmup(session, args, intensors_desc, infileslist[0])

    if args.run_mode == "array":
        infer_loop_array_run(session, args, intensors_desc, infileslist, output_prefix)
    elif args.run_mode == "files":
        infer_loop_files_run(session, args, intensors_desc, infileslist, output_prefix)
    elif args.run_mode == "full":
        infer_fulltensors_run(session, args, intensors_desc, infileslist, output_prefix)
    elif args.run_mode == "tensor":
        infer_loop_tensor_run(session, args, intensors_desc, infileslist, output_prefix)
    else:
        raise RuntimeError('wrong run_mode:{}'.format(args.run_mode))

    summary.add_args(sys.argv)
    s = session.sumary()
    summary.npu_compute_time_list = s.exec_time_list
    summary.h2d_latency_list = MemorySummary.get_H2D_time_list()
    summary.d2h_latency_list = MemorySummary.get_D2H_time_list()
    summary.report(args.batchsize, output_prefix, args.display_all_summary)

    session.finalize()

if __name__ == "__main__":
    args = get_args()

    version_check(args)

    if args.profiler == True:
        # try use msprof to run
        msprof_bin = shutil.which('msprof')
        if msprof_bin == None:
            logger.info("find no msprof continue use acl.json mode")
        else:
            msprof_run_profiling(args)
            exit(0)

    if args.dymShape_range != None and args.dymShape == None:
        # dymshape range run,according range to run each shape infer get best shape
        dymshape_range_run(args)
        exit(0)

    main(args)