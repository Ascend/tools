def set_value(value):
    global _npu_id
    _npu_id = value
    print('set device id %s success'%_npu_id)

def get_value():
    return _npu_id