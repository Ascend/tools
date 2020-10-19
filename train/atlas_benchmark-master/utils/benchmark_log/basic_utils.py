# -*- coding: utf-8 -*-

import os
import subprocess
import yaml


def get_model_parameter(config_type):
    yaml_path = os.getenv("YAML_PATH")
    with open(yaml_path, 'r') as f:
        model_parameter_dict = yaml.load(f)
    parameter_dict = model_parameter_dict.get(config_type)
    if "tensorflow" in config_type:
        parameter_dict.pop("mpirun_ip")
    parameter_dict.pop("docker_image")
    return parameter_dict


def get_environment_info(framework):
    cpu_info = subprocess.getstatusoutput('lscpu')[1]
    cpu_info = cpu_info.split("\nFlags")[0]
    cpu_info_list = cpu_info.split()
    cpu_info_keys = []
    cpu_info_values = []
    value_info = ""
    for i in cpu_info_list:
        if ":" not in i:
            value_info += i
        else:
            i = i.split(":")[0]
            cpu_info_keys.append(i)
            if value_info:
                cpu_info_values.append(value_info)
            value_info = ""
    cpu_info_dict = {}
    for k, v in zip(cpu_info_keys, cpu_info_values):
        cpu_info_dict[k] = v
    NPU_info = "Ascend910"
    framework_info = ""
    if framework.lower() == "tensorflow":
        import tensorflow as tf
        framework_info = "tensorflow {}".format(tf.__version__)
    if framework.lower() == "pytorch":
        import torch
        framework_info = "pytorch {}".format(torch.__version__)
    os_info = subprocess.getstatusoutput('cat /proc/version')[1]
    benchmark_version = "v1.0.0"
    return cpu_info_dict, NPU_info, framework_info, os_info, benchmark_version
