import os
import sys
from pickle import NONE
import numpy as np

import logging
logging.basicConfig(stream=sys.stdout, level = logging.INFO,format = '[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Split a List Into Even Chunks of N Elements
def list_split(listA, n):
    for x in range(0, len(listA), n):
        every_chunk = listA[x: n+x]

        if len(every_chunk) < n:
            every_chunk = every_chunk + \
                [None for y in range(n-len(every_chunk))]
        yield every_chunk

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
    return files_list

def get_files_datasize(file_path):
    if file_path.endswith(".NPY") or file_path.endswith(".npy"):
        ndata = np.load(file_path)
        return ndata.nbytes
    else:
        return os.path.getsize(file_path)

def save_data_to_files(file_path, ndata):
    if file_path.endswith(".NPY") or file_path.endswith(".npy"):
        np.save(file_path, ndata)
    else:
        ndata.tofile(file_path)