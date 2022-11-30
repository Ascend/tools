
import os
import sys
import json

def get_times_list(file):
    l = []
    with open(file, 'rb') as f:
        for line in f.readlines():
            s = line[0:-3]
            value = float(s)
            l.append(value)
    return l

def get_pid(file):
    pid = None
    if not os.path.exists(file):
        print("{} file not exist".format(file))
    else:
        with open(file, 'rb') as fd:
            pid = int(fd.read())
    return pid

if __name__ == '__main__':
    times_file = sys.argv[1]
    pid_file = sys.argv[2]
    out_file = sys.argv[3]

    times = get_times_list(times_file)
    pid = get_pid(pid_file)
    info = {"pid": pid, "npu_compute_time_list": times}
    with open(os.path.join(out_file), 'w') as f:
        json.dump(info, f)

