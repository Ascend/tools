import os
import sys
import re
from pickle import NONE
import numpy as np

import logging
logging.basicConfig(stream=sys.stdout, level = logging.INFO,format = '[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Split a List Into Even Chunks of N Elements
def list_split(listA, n, padding_file):
    for x in range(0, len(listA), n):
        every_chunk = listA[x: n+x]

        if len(every_chunk) < n:
            every_chunk = every_chunk + \
                [padding_file for y in range(n-len(every_chunk))]
        yield every_chunk

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def get_fileslist_from_dir(dir):
    files_list = []

    if os.path.exists(dir) == False:
        logger.error('dir:{} not exist'.format(dir))
        raise RuntimeError()

    for f in os.listdir(dir):
        if f.endswith(".npy") or f.endswith(".NPY") or f.endswith(".bin") or f.endswith(".BIN"):
            files_list.append(os.path.join(dir, f))

    if len(files_list) == 0:
        logger.error('not find valid [*.npy *.NPY *.bin *.BIN] files:{}'.format(files_list))
        raise RuntimeError()
    files_list.sort()
    return natural_sort(files_list)

def get_file_datasize(file_path):
    if file_path.endswith(".NPY") or file_path.endswith(".npy"):
        ndata = np.load(file_path)
        return ndata.nbytes
    else:
        return os.path.getsize(file_path)

def get_file_content(file_path):
    if file_path.endswith(".NPY") or file_path.endswith(".npy"):
        return np.load(file_path)
    else:
        with open(file_path, 'rb') as fd:
            barray = fd.read()
            return np.frombuffer(barray, dtype=np.int8)

def get_ndata_fmt(ndata):
    if ndata.dtype == np.float32 or ndata.dtype == np.float16 or ndata.dtype == np.float64:
        fmt = "%f"
    else:
        fmt = "%d"
    return fmt

def save_data_to_files(file_path, ndata):
    if file_path.endswith(".NPY") or file_path.endswith(".npy"):
        np.save(file_path, ndata)
    elif file_path.endswith(".TXT") or file_path.endswith(".txt"):
        outdata=ndata.reshape(-1, ndata.shape[-1])
        fmt = get_ndata_fmt(outdata)
        with open(file_path, "ab") as f:
            for i in range(outdata.shape[0]):
                np.savetxt(f, np.c_[outdata[i]], fmt=fmt, newline=" ")
                f.write(b"\n")
    else:
        ndata.tofile(file_path)