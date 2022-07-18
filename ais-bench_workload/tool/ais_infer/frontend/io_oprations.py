import os
import random
import time

import aclruntime
import numpy as np

from frontend.summary import summary
from frontend.utils import (get_files_datasize, get_fileslist_from_dir, list_split,
                   logger, save_data_to_files)

pure_infer_dump_file = "pure_infer_data"

def get_pure_infer_data(size, pure_data_type):
    lst = []
    if pure_data_type == "random":
        # random value from [0, 255]
        lst = [random.randrange(0, 256) for _ in range(size)]
    else:
        # zero value, default
        lst = [0 for _ in range(size)]

    barray = bytearray(lst)
    ndata = np.frombuffer(barray, dtype=np.uint8)
    return ndata

# get tensors from files list combile all files
def get_tensor_from_files_list(files_list, device, size, pure_data_type):
    ndatalist = []
    for i, file_path in enumerate(files_list):
        logger.debug("get tensor from filepath:{} i:{} of all:{}".format(file_path, i, len(files_list)))
        if file_path == pure_infer_dump_file:
            ndata = get_pure_infer_data(size, pure_data_type)
        elif file_path == None or os.path.exists(file_path) == False:
            logger.error('filepath:{} not valid'.format(file_path))
            raise RuntimeError()
            #ndata = get_pure_infer_data(size)
        elif file_path.endswith(".npy"):
            ndata = np.load(file_path)
        else:
            with open(file_path, 'rb') as fd:
                barray = fd.read()
                ndata = np.frombuffer(barray, dtype=np.int8)
        ndatalist.append(ndata)
    ndata = np.concatenate(ndatalist)
    if ndata.nbytes != size:
        logger.error('ndata size:{} not match {}'.format(ndata.nbytes, size))
        raise RuntimeError()

    tensor = aclruntime.Tensor(ndata)
    starttime = time.time()
    tensor.to_device(device)
    endtime = time.time()
    summary.h2d_latency_list.append(float(endtime - starttime) * 1000.0)  # millisecond
    return tensor

# 根据文件信息和输入描述信息获取filesperbatch runcount信息
# 策略如下  根据输入0的realsize和文件大小判断 如果判断失败，需要强制设置想要的值
def get_files_count_per_batch(intensors_desc, fileslist):
    # get filesperbatch
    filesize = get_files_datasize(fileslist[0][0])
    tensorsize = intensors_desc[0].realsize
    if filesize == 0 or tensorsize%filesize != 0:
        logger.error('arg0 tensorsize: {} filesize: {} not match'.format(tensorsize, filesize))
        raise RuntimeError()
    files_count_per_batch = (int)(tensorsize/filesize)

    #runcount = math.ceil(len(fileslist) / files_count_per_batch)
    runcount = len(fileslist[0]) // files_count_per_batch
    logger.info("get filesperbatch files0 size:{} tensor0size:{} filesperbatch:{} runcount:{}".format(
        filesize, tensorsize, files_count_per_batch, runcount))
    return files_count_per_batch, runcount

# out api 创建空数据
def create_intensors_zerodata(intensors_desc, device, pure_data_type):
    intensors = []
    for info in intensors_desc:
        logger.debug("info shape:{} type:{} val:{} realsize:{} size:{}".format(info.shape, info.datatype, int(info.datatype), info.realsize, info.size))
        ndata = get_pure_infer_data(info.realsize, pure_data_type)
        tensor = aclruntime.Tensor(ndata)
        starttime = time.time()
        tensor.to_device(device)
        endtime = time.time()
        summary.h2d_latency_list.append(float(endtime - starttime) * 1000.0)  # millisecond
        intensors.append(tensor)
    return intensors

# 根据输入filelist获取tensor信息和files信息 create intensor form files list
# len(files_list) should equal len(intensors_desc)
def create_infileslist_from_fileslist(fileslist, intensors_desc):
    if len(intensors_desc) != len(fileslist):
        logger.error('fileslist:{} intensor:{} not match'.format(len(fileslist), len(intensors_desc)))
        raise RuntimeError()
    files_count_per_batch, runcount = get_files_count_per_batch(intensors_desc, fileslist)

    files_perbatch_list = [ list(list_split(fileslist[j], files_count_per_batch)) for j in range(len(intensors_desc)) ]

    infileslist = []
    for i in range(runcount):
        infiles = []
        for j in range(len(intensors_desc)):
            logger.debug("create infileslist i:{} j:{} runcount:{} lists:{} filesPerPatch:{}".format(i, j, runcount, files_perbatch_list[j][i], files_count_per_batch))
            infiles.append(files_perbatch_list[j][i])
        infileslist.append(infiles)
    return infileslist

def check_and_get_fileslist(inputs_list, intensors_desc):
    return fileslist

#  outapi 根据输入filelist获取tensor信息和files信息 create intensor form files list
def create_intensors_from_infileslist(infileslist, intensors_desc, device, pure_data_type):
    intensorslist = []
    for i, infiles in enumerate(infileslist):
        intensors = []
        for j, files in enumerate(infiles):
            tensor = get_tensor_from_files_list(files, device, intensors_desc[j].realsize, pure_data_type)
            intensors.append(tensor)
        intensorslist.append(intensors)
    return intensorslist

# outapi 根据inputs_list输入列表获取 文件列表
def create_infileslist_from_inputs_list(inputs_list, intensors_desc):
    fileslist = []
    inputlistcount = len(inputs_list)
    intensorcount = len(intensors_desc)
    if os.path.isfile(inputs_list[0]) == True:
        chunks = inputlistcount // intensorcount
        fileslist = list(list_split(inputs_list, chunks))
        logger.debug("create intensors list file type inlistcount:{} intensorcont:{} chunks:{} files_size:{}".format(
            inputlistcount, intensorcount, chunks, len(fileslist)))
    elif os.path.isdir(inputs_list[0]) and inputlistcount == intensorcount:
        fileslist = [ get_fileslist_from_dir(dir) for dir in inputs_list ]
        logger.debug("create intensors list dictionary type inlistcount:{} intensorcont:{} files_size:{}".format(
            inputlistcount, intensorcount, len(fileslist)))
    else:
        logger.error('create intensors list filelists:{} intensorcont:{} error create'.format(inputlistcount, intensorcount))
        raise RuntimeError()

    infileslist = create_infileslist_from_fileslist(fileslist, intensors_desc)
    if len(infileslist) == 0:
        logger.error('create_infileslist_from_fileslist return infileslist size: {}'.format(len(infileslist)))
        raise RuntimeError()

    return infileslist

def save_tensors_to_file(outputs, output_prefix, infiles_paths, outfmt, index):
    files_count_perbatch = len(infiles_paths[0])
    infiles_perbatch = np.transpose(infiles_paths)
    logger.debug("files_count_perbatch:{} outputs count:{}".format(files_count_perbatch, len(outputs)))
    for i, out in enumerate(outputs):
        starttime = time.time()
        out.to_host()
        endtime = time.time()
        summary.d2h_latency_list.append(float(endtime - starttime) * 1000.0)  # millisecond
        ndata = np.array(out)
        if files_count_perbatch == 1 or ndata.shape[0] % files_count_perbatch == 0:
            subdata = np.array_split(ndata, files_count_perbatch)
            for j in range(files_count_perbatch):
                sample_id = index*files_count_perbatch+j
                file_path = os.path.join(output_prefix, "input{}_output_{}.{}".format(sample_id, i, outfmt.lower()))
                summary.add_sample_id_infiles(sample_id, infiles_perbatch[j])
                logger.debug("save func: sampleid:{} infiles:{} out_{} file:{} fmt:{}".format(sample_id, i, infiles_perbatch[j], file_path, outfmt))
                summary.append_sample_id_outfile(sample_id, file_path)
                save_data_to_files(file_path, subdata[j])
        else:
            logger.error('save out files error array shape:{} filesinfo:{} files_count_perbatch:{} ndata.shape0:{}'.format(
                ndata.shape, infiles_paths, files_count_perbatch, ndata.shape[0]))
            raise RuntimeError()
