# coding=utf-8

class FileDesc(object):
    file_name = ''
    op_name = ''
    op_type = ''
    task_id = -1
    anchor_type = ''
    idx = -1
    dir_path = ''
    path = ''
    timestamp = 0

    def __init__(self, file_name='', op_name='', op_type='', task_id=-1, anchor_type='',
                 idx=-1, dir_path='', path='', timestamp=0):
        self.file_name = file_name
        self.op_name = op_name
        self.op_type = op_type
        self.task_id = task_id
        self.anchor_type = anchor_type
        self.idx = idx
        self.dir_path = dir_path
        self.path = path
        self.timestamp = timestamp
