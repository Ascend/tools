"""
    Copyright 2020 Huawei Technologies Co., Ltd

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    Typical usage example:
"""

import os
import sys
import codecs
import glob
import numpy as np

"""
The script transfer all the npy file in the bin_dir into one target_file,
according to the vocab of vocab.translate_ende_wmt32k.32768.subwords
"""

bin_dir = sys.argv[1]  # benchmark output bin file path: ./result/dumpOutput/
vocab_file = sys.argv[2]  # dict path: ./vocab.translate_ende_wmt32k.32768.subwords
target_file = sys.argv[3]  # generate result file: ./translation.de
bin_dir = os.path.realpath(bin_dir)
vocab_file = os.path.realpath(vocab_file)
target_file = os.path.realpath(target_file)
bin_list = os.listdir(bin_dir)


def PrintInfo(s):
    """
    packaging print function
    """
    print("[INFO] " + s)


PrintInfo("{} files need to be transfered".format(len(bin_list)))


def readFromBin(f):
    """
    read information from bin file
    """
    return np.fromfile(f, "int32")


def LoadVocab(s):
    """
    load vocab
    """
    with codecs.open(s, 'r', encoding='UTF-8') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content


vocab = LoadVocab(vocab_file)

with codecs.open(target_file, "w", "utf-8") as target:
    for k in range(len(bin_list)):
        name = '*_' + str(k) + '.bin'

        file_path_name = (glob.glob(bin_dir + '/' + name))[0]
        print(file_path_name)
        val = readFromBin(file_path_name)

        sentence = ""
        for i in val:
            if i == 1:
                break
            sentence += vocab[i].split("'")[1].replace("_", " ")
        target.write(sentence + "\n")
print("[Hit the end successfully]")
