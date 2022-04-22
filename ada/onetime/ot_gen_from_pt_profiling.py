import json
import logging
from collections import OrderedDict


def main_npu(path):
    with open(path, 'r') as f:
        records = json.load(f)

    for rec in records:
        if not rec.get('name', '').startswith("aclopCompileAndExecute: "):
            continue
        op_type = rec['name'].replace("aclopCompileAndExecute: ", '')
        time = rec.get('dur', None)
        if time is None:
            logging.warning("Skip op {} does not contains duration time".format(op_type))
            continue
        print("{}, {}".format(op_type, time))


class GpuProfiling:
    def __init__(self):
        self.records: OrderedDict = OrderedDict()

    def merge(self, rec):
        self.records.g


def main_gpu(path):
    with open(path, 'r') as f:
        records = json.load(f)


if __name__ == "__main__":
    main_npu(r'E:\Downloads\espace\step90_batchsize512_npu -gpu-aclge.json')
