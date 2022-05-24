import sys
import time
import set_result as old_set_result

def calc_throughput_rate(nums, start_time, end_time):
    if start_time == end_time:
        return 0
    else:
        return nums/(end_time - start_time)

def calc_lantency(elapsedtime, count):
    latency = 0 if count == 0 else elapsedtime/count
    return latency

def get_datatime():
    return time.time()

def set_result(mode, key, value):
    old_set_result.set_result(mode, key, value)

if __name__ == '__main__':
    fun_name = sys.argv[1]

    if fun_name == "set_result":
        mode = sys.argv[2]
        key = sys.argv[3]
        value = sys.argv[4]
        set_result(mode, key, value)
