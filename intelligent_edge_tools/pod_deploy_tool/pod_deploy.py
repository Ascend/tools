# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################

import argparse
import json
import logging
import os
import queue
import re
import shlex
import ssl
import subprocess
import threading
import time
import uuid
from enum import Enum
from typing import Optional, Tuple

import paho.mqtt.client as mqtt_client
import yaml
from edge_cbb.service.mqtt_proxy.config import init_client_tls_config

run_log_format = f"[%(asctime)s] [%(levelname)s] [%(funcName)s] [%(filename)s:%(lineno)d] [%(message)s]"
logging.basicConfig(filemode="a", format=run_log_format, datefmt="%H:%M:%S", level=logging.INFO)
logger = logging.getLogger(__name__)


class Result:
    def __init__(self, result: bool = False, data=None, error_msg: str = ""):
        self._result = result
        self._data = data
        self._error_msg = error_msg

    def __bool__(self):
        return self._result

    def __str__(self):
        return f"result={self._result}; error_mg={self._error_msg}"

    @property
    def data(self):
        return self._data

    @property
    def error(self) -> str:
        return self._error_msg


class ExecCmd:
    @staticmethod
    def change_cmd_format(cmds: str):
        cmds_list = []
        result = []

        if "|" in cmds:
            cmds_list = cmds.split("|")
        else:
            cmds_list.append(cmds)

        for cmd in cmds_list:
            cmd = shlex.split(cmd)
            result.append(cmd)

        return result

    @staticmethod
    def exec_cmd_get_output(cmds: str, wait=60):
        process_list = []
        try:
            cmds_tuple = tuple(ExecCmd.change_cmd_format(cmds.strip()))
            for index, cmd in enumerate(cmds_tuple):
                if index == 0:
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False)
                else:
                    p = subprocess.Popen(cmd,
                                         stdin=process_list[index - 1].stdout,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL,
                                         shell=False)
                process_list.append(p)

            output = process_list[-1].communicate(timeout=wait)[0]
            return Result(True, data=output.decode().strip())
        except Exception as abn:
            error_info = "call linux command error because {}".format(abn)
            return Result(False, error_msg=error_info)


class FileCheck:
    @staticmethod
    def check_path_valid(path) -> Result:
        if not path or not isinstance(path, str):
            return Result(result=False, error_msg="check path failed: path is null or not string")

        if len(path) > 1024:
            return Result(result=False, error_msg="path length > 1024")

        pattern_name = re.compile(r"[^0-9a-zA-Z_./-]")
        match_name = pattern_name.findall(path)
        if match_name or ".." in path:
            return Result(False, error_msg="illegal path, there are illegal characters")

        return Result(result=True)


class YamlOperator:
    def __init__(self, file_path: str):
        self.file_path: str = file_path

    def read_data(self) -> Result:
        if not FileCheck.check_path_valid(self.file_path):
            error_msg = f"check yaml file [{self.file_path}] valid failed"
            logger.error(error_msg)
            return Result(False, error_msg=error_msg)

        try:
            with open(self.file_path, "r") as stream:
                return Result(True, data=yaml.safe_load(stream))
        except Exception as abn:
            error_msg = f"load yaml file [{self.file_path}] failed:{abn}"
            logger.error(error_msg)
            return Result(False, error_msg=error_msg)


msg_queue = queue.Queue(maxsize=256)


class MqttConfig:
    def __init__(self, **kwargs):
        self.host: str = kwargs.get("host", "127.0.0.1")
        self.port: int = kwargs.get("port", 8886)
        self.keep_alive: int = kwargs.get("keep_alive", 60)
        self.bind_address: str = kwargs.get("bind_address", "")
        self.ca_certs_file_path: Optional[str] = kwargs.get("ca_certs_file_path")
        self.certs_file_path: Optional[str] = kwargs.get("certs_file_path")
        self.key_file_path: Optional[str] = kwargs.get("key_file_path")
        self.pwd_file_path: Optional[str] = kwargs.get("pwd_file_path")
        self.cert_reqs: Optional[int] = kwargs.get("cert_reqs", ssl.CERT_REQUIRED)
        self.tls_version: Optional[int] = kwargs.get("tls_version", ssl.PROTOCOL_TLS)
        self.ciphers: Optional[str] = kwargs.get("ciphers")
        self.mqtt_client_topics: Tuple[str] = tuple("")
        self.mqtt_subscribe_qos: int = kwargs.get("mqtt_subscribe_qos", 1)
        self.mqtt_publish_qos: int = kwargs.get("mqtt_publish_qos", 1)
        self.connect_time_out: int = kwargs.get("connect_time_out", 3)
        self.send_thread_pool_size: int = kwargs.get("send_thread_pool_size", 15)
        self.connect_retry_interval: int = kwargs.get("connect_retry_interval", 5)
        self.using_tls_config: bool = kwargs.get("using_tls_config", True)
        self.module_name: str = kwargs.get("module_name", "edge_om")

    def init_edge_mqtt_config(self, work_dir):
        edge_om_path = os.path.join(os.path.realpath(work_dir), "edge_work_dir/edge_om")
        ca_certs = os.path.join(edge_om_path, "config/certs/rootCA.crt")
        cert_file = os.path.join(edge_om_path, "config/certs/edgeom.crt")
        key_file = os.path.join(edge_om_path, "config/certs/edgeom.key")
        pwd_file = os.path.join(edge_om_path, "config/certs/edgeom.pwd")

        if os.path.exists(ca_certs) and os.path.exists(cert_file) and os.path.exists(key_file) and os.path.exists(
                pwd_file):
            self.ca_certs_file_path = ca_certs
            self.certs_file_path = cert_file
            self.key_file_path = key_file
            self.pwd_file_path = pwd_file


class ClientAdapter:
    def __init__(self, configure: MqttConfig):
        self.configure = configure
        self._service_name = "pod_deploy_tool"
        self._client_id = "{}-{}".format(self._service_name, time.strftime("%Y-%m-%d %H:%M:%S"))
        self.client = mqtt_client.Client(client_id=self._client_id)
        self._init_recall_function()
        init_client_tls_config(self.client, self.configure)
        self.connect_status = False
        self._connected_event = threading.Event()

    def _init_recall_function(self):
        self.client._on_connect = self._on_connect
        self.client._on_disconnect = self._on_disconnect
        self.client._on_message = self._on_message
        self.client._on_publish = self._on_publish
        self.client._on_subscribe = self._on_subscribe
        self.client._on_log = self._on_log

    def connect(self):
        try:
            logger.info("begin mqtt client connect")
            self.client.disable_logger()
            self.client.connect(
                self.configure.host,
                self.configure.port,
                self.configure.keep_alive,
                self.configure.bind_address,
            )
            logger.info("end mqtt client connect")

            logger.info("begin mqtt client loop_start")
            self.client.loop_start()
            logger.info("end mqtt client loop_start")
        except Exception as err:
            logger.error(f"mqtt connect exception:{err}")
            time.sleep(5)
            threading.Timer(self.configure.connect_retry_interval, self.connect).start()

    def connected(self):
        return self.connect_status

    def _subscribe(self):
        logger.info("subscribe wait for connected")
        self._connected_event.wait(timeout=self.configure.connect_time_out)
        if self.connect_status:
            subscribe_data = [("$hw/edge/v1/apps/pod/+/+/result", self.configure.mqtt_subscribe_qos),
                              ("$hw/edge/v1/apps/nodestatus/query/result", self.configure.mqtt_subscribe_qos)]
            logger.info("start subscribe")
            self.client.subscribe(subscribe_data)
            logger.info("end subscribe")

    def _on_connect(self, client, userdata, flags, return_code):
        logger.info(f"client:{self._client_id} connected with result code:{return_code}")
        self.connect_status = True
        self._connected_event.set()
        self._subscribe()

    def _on_disconnect(self, client, userdata, return_code):
        logger.info(f"client:{self._client_id} connected with result code:{return_code}")
        self.connect_status = False

    def _on_message(self, client, obj, msg):
        topic_name = msg.topic
        logger.info(f"receive topic={topic_name}")
        if msg_queue.full():
            msg_queue.queue.clear()

        msg_queue.put(msg, False, 2)

    def _on_publish(self, client, obj, mid):
        logger.info(f"{self._client_id},{obj},{mid}")

    def _on_subscribe(self, client, obj, mid, granted_qos):
        logger.info(f"client:{self._client_id}, obj:{obj} subscribed:{mid} {granted_qos}")

    def _on_log(self, client, obj, level, string):
        logger.log(mqtt_client.LOGGING_LEVEL.get(level), f"client:{self._client_id}, obj:{obj}")

    def wait_response(self, topic, timeout=10):
        time_start = time.time()
        try:
            while True:
                if not msg_queue.empty():
                    ret = msg_queue.get(timeout=2)
                    if ret.topic == topic:
                        return Result(result=True, data=ret)

                    continue

                time.sleep(0.2)
                time_end = time.time()
                time_start = min(time_start, time_end)
                if time_end - time_start > timeout:
                    logger.error("Failed to get [{}] response, wait timeout.". format(topic))
                    return Result(result=False, error_msg="Failed to get [{}] response, wait timeout.". format(topic))
        except Exception as abn:
            logger.error("Failed to get {} response, because {}.".format(topic, abn))
            return Result(result=False, error_msg="Failed to get {} response, because {}.".format(topic, abn))

    def mqtt_publish(self, topic, payload, qos=1, sync=False):
        if not self.connect_status:
            return Result(result=False, error_msg="mqtt is not connected")

        try:
            info = self.client.publish(topic, payload, qos)
            info.wait_for_publish()
        except Exception as err:
            logger.error(f"mqtt publish exception:{err}")
            return Result(result=False, error_msg=f"mqtt publish exception:{err}")

        if not sync:
            return Result(result=True)

        return self.wait_response(topic+"/result")

    def connect_mqtt_sever(self):
        count = 0
        self.connect()
        while count < 12:
            time.sleep(5)
            if self.connected():
                break
            count += 1

        return self.connected()


class PodOperator:
    UUID_LEN = 36
    DEFAULT_NPU_NAME = "huawei.com/davinci-mini"
    NPU_NAME_PREFIX = "huawei.com"

    def __init__(self, client_adapter, pod_file):
        self.client_adapter = client_adapter
        self.pod_file = pod_file

    @staticmethod
    def check_image(image):
        ret = ExecCmd.exec_cmd_get_output(f"docker images {image}")
        if not ret:
            return False

        if len(ret.data.split('\n')) < 2:
            return False

        return True

    def check_pod_name(self, pod_name):
        if len(pod_name) <= self.UUID_LEN:
            logger.error(f"check pod name:{pod_name} failed, pod name should be name-uuid4, "
                         "eg: nginx-a0875298-da97-4870-8503-dd3bff923479")
            return False

        uid = pod_name[-self.UUID_LEN:]

        if not self.is_valid_uuid(uid):
            logger.error(f"check pod name:{pod_name} failed, pod name should be name-uuid4, "
                         "eg: nginx-a0875298-da97-4870-8503-dd3bff923479")
            return False

        return True

    def query_npu_resource_name(self):
        ret = self.client_adapter.mqtt_publish(r"$hw/edge/v1/apps/nodestatus/query", json.dumps({}), sync=True)
        if not ret:
            logger.warning("query node status error")
            return Result(result=True, data=self.DEFAULT_NPU_NAME)

        payload_dict = json.loads(ret.data.payload)
        if payload_dict.get("result") != "success":
            logger.warning("query node status error")
            return Result(result=True, data=self.DEFAULT_NPU_NAME)

        keys = payload_dict.get("content", [])[0].get("Status", {}).get("capacity", {}).keys()
        for key in keys:
            if key.startswith(self.NPU_NAME_PREFIX):
                logger.warning(f"replace {self.DEFAULT_NPU_NAME} to {key}")
                return Result(result=True, data=key)

        return Result(result=True, data=self.DEFAULT_NPU_NAME)

    def create_pod(self):
        ret = YamlOperator(self.pod_file).read_data()
        if not ret:
            logger.error(f"read pod file failed:{ret.error}, create pod failed")
            return False

        data = ret.data
        for container in data["spec"]["containers"]:
            if not self.check_image(container["image"]):
                logger.error(f"container image {container['image']} not exist on device")
                return False

        pod_name = data["metadata"]["name"]

        if not self.check_pod_name(pod_name):
            return False

        uid = pod_name[-self.UUID_LEN:]
        npu_name = self.query_npu_resource_name().data
        for i in range(len(data["spec"]["containers"])):
            if data["spec"]["containers"][i]["resources"]["limits"].get(self.DEFAULT_NPU_NAME, "") != "":
                count = data["spec"]["containers"][i]["resources"]["limits"].get(self.DEFAULT_NPU_NAME, "")
                del data["spec"]["containers"][i]["resources"]["limits"][self.DEFAULT_NPU_NAME]
                data["spec"]["containers"][i]["resources"]["limits"][npu_name] = count

            if data["spec"]["containers"][i]["resources"]["requests"].get(self.DEFAULT_NPU_NAME, "") != "":
                count = data["spec"]["containers"][i]["resources"]["requests"].get(self.DEFAULT_NPU_NAME, "")
                del data["spec"]["containers"][i]["resources"]["requests"][self.DEFAULT_NPU_NAME]
                data["spec"]["containers"][i]["resources"]["requests"][npu_name] = count

        data["metadata"]["creationTimestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())
        data["metadata"]["name"] = pod_name
        data["metadata"]["namespace"] = "websocket"
        data["metadata"]["resourceVersion"] = "1.0"
        data["metadata"]["selfLink"] = "/api/v1/namespaces/websocket/pods/" + pod_name
        data["metadata"]["uid"] = str(uid)
        logger.info("-------------------------create pod -------------------------")
        ret = self.client_adapter.mqtt_publish(r"$hw/edge/v1/apps/pod/{}/update".format(pod_name),
                                               json.dumps(data), sync=True)
        if not ret:
            logger.error("publish [$hw/edge/v1/apps/pod/{}/update] failed".format(pod_name))
            return False

        payload_dict = json.loads(ret.data.payload)
        if payload_dict.get("result") != "success":
            logger.error(f'execute create container command failed: {payload_dict.get("content")}')
            return False

        logger.info("execute create container command success, please execute 'docker ps' check the container status "
                    "by few moments")

        return True

    @staticmethod
    def is_valid_uuid(uid, version=4):
        try:
            uuid_obj = uuid.UUID(uid, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uid

    @staticmethod
    def is_pod_exist(container_name):
        ret = ExecCmd.exec_cmd_get_output(f"docker ps | grep {container_name}")
        if not ret or not ret.data:
            return False

        return True

    def delete_pod(self):
        ret = YamlOperator(self.pod_file).read_data()
        if not ret:
            logger.error(f"read pod file failed:{ret.error}")
            return False

        data = ret.data
        pod_name = data["metadata"]["name"]
        if not self.check_pod_name(pod_name):
            return False

        uid = pod_name[-self.UUID_LEN:]

        if not self.is_pod_exist(f"k8s_POD_{pod_name}"):
            logger.error(f"delete pod failed, pod:{pod_name} not exist")
            return False

        data["metadata"]["creationTimestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())
        data["metadata"]["namespace"] = "websocket"
        data["metadata"]["resourceVersion"] = "1.0"
        data["metadata"]["selfLink"] = "/api/v1/namespaces/websocket/pods/{}".format(pod_name)
        data["metadata"]["uid"] = uid
        logger.info("-------------------------delete pod -------------------------")
        ret = self.client_adapter.mqtt_publish(r"$hw/edge/v1/apps/pod/{}/delete".format(pod_name),
                                               json.dumps(data), sync=True)
        if not ret:
            logger.error("publish [$hw/edge/v1/apps/pod/{}/delete] failed".format(pod_name))
            return False

        payload_dict = json.loads(ret.data.payload)
        if payload_dict.get("result") != "success":
            logger.error(f'execute delete container command failed: {payload_dict.get("content")}')
            return False

        logger.info("execute delete container command success, please execute 'docker ps' check the container status "
                    "by few moments")
        return True


class OperateType(Enum):
    CREATE = "create"
    DELETE = "delete"


class ArgOperator:
    MAX_FILE_SIZE = 1.5 * 1024 * 1024

    def __init__(self):
        self.argument = None

    def parse_arg(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--work_dir', help='atlas edge work dir, eg: --work_dir=/usr/local/AtlasEdge', type=str)
        parser.add_argument('--operate',  help='must be create or delete, eg: --operate=create', type=str)
        parser.add_argument('--pod_file', help='it must be absolute path of pod yaml file, '
                                               'eg: --pod_file=/root/pod.yaml', type=str)
        self.argument = parser.parse_args()

    @property
    def work_dir(self):
        return self.argument.work_dir

    @property
    def operate(self):
        return self.argument.operate

    @property
    def pod_file(self):
        return self.argument.pod_file

    def check_work_dir(self):
        ret = FileCheck.check_path_valid(self.work_dir)
        if not ret:
            logger.error("check work dir failed")
            return False

        return True

    def check_operate(self):
        if self.operate != OperateType.CREATE.value and self.operate != OperateType.DELETE.value:
            logger.error("operate para not support")
            return False
        return True

    def check_pod_file(self):
        if not FileCheck.check_path_valid(self.pod_file):
            logger.error("pod file path invalid, operate pod failed")
            return False

        if not os.path.splitext(self.pod_file)[0] != ".yaml":
            logger.error("pod file type is not yaml")
            return False

        if os.path.getsize(self.pod_file) > self.MAX_FILE_SIZE:
            logger.error("pod file size up to limit, operate pod failed")
            return False

        return True

    def check_para(self):
        if not self.check_work_dir() or not self.check_operate() or not self.check_pod_file():
            return False

        return True


def main():
    arg_operator = ArgOperator()
    arg_operator.parse_arg()
    if not arg_operator.check_operate():
        logger.error("para check failed")
        return False

    mqtt_config = MqttConfig()
    mqtt_config.init_edge_mqtt_config(arg_operator.work_dir)
    client_adapter = ClientAdapter(mqtt_config)
    if not client_adapter.connect_mqtt_sever():
        logger.error("connect mqtt server failed")
        return False

    ret = False
    if arg_operator.operate == OperateType.CREATE.value:
        ret = PodOperator(client_adapter, arg_operator.pod_file).create_pod()
    elif arg_operator.operate == OperateType.DELETE.value:
        ret = PodOperator(client_adapter, arg_operator.pod_file).delete_pod()

    time.sleep(5)
    return ret


if __name__ == "__main__":
    try:
        if main():
            exit(0)
        else:
            exit(1)
    except Exception as exp:
        logger.error(f"operate pod exception:{exp}")
        exit(1)
