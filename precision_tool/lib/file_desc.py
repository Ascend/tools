# coding=utf-8
import os


class FileDesc(object):
    def __init__(self, file_name, dir_path, timestamp=-1):
        self.file_name = file_name
        self.dir_path = dir_path
        self.path = os.path.join(dir_path, file_name)
        self.timestamp = timestamp
        if self.timestamp == -1:
            self.timestamp = os.path.getmtime(self.path)


class BuildGraphFileDesc(FileDesc):
    def __init__(self, file_name, dir_path, timestamp, graph_id, graph_name):
        super(BuildGraphFileDesc, self).__init__(file_name, dir_path, timestamp)
        self.graph_id = graph_id
        self.graph_name = graph_name


class NpuDumpFileDesc(FileDesc):
    def __init__(self, file_name, dir_path, timestamp, op_name, op_type, task_id, stream_id=0):
        super(NpuDumpFileDesc, self).__init__(file_name, dir_path, timestamp)
        self.op_name = op_name
        self.op_type = op_type
        self.task_id = task_id
        stream_id = 0 if stream_id is None else int(stream_id)
        self.stream_id = stream_id


class DumpDecodeFileDesc(NpuDumpFileDesc):
    def __init__(self, file_name, dir_path, timestamp, op_name, op_type, task_id, anchor_type, anchor_idx):
        super(DumpDecodeFileDesc, self).__init__(file_name, dir_path, timestamp, op_name, op_type, task_id)
        self.type = anchor_type
        self.idx = anchor_idx
