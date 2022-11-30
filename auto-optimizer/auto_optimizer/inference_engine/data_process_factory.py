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

import logging

from typing import Dict, Type
from .pre_process.pre_process_base import PreProcessBase
from .post_process.post_process_base import PostProcessBase
from .evaluate.evaluate_base import EvaluateBase
from .inference.inference_base import InferenceBase
from .datasets.dataset_base import DatasetBase

from ..common.utils import typeassert

logging = logging.getLogger("auto-optimizer")


class DatasetFactory(object):
    _dataset_pool: Dict[str, DatasetBase] = {}

    @classmethod
    @typeassert(name=str)
    def get_dataset(cls, name):
        return cls._dataset_pool.get(name, None)

    @classmethod
    @typeassert(name=str)
    def register(cls, name):
        def _wrapper(dataset_cls: Type[DatasetBase]):
            if cls.get_dataset(name) is not None:
                logging.warning(f"register name is the same, please check! {name}")
                raise RuntimeError(f"register name is the same, please check! {name}")
            cls._dataset_pool[name] = dataset_cls()
            return dataset_cls
        return _wrapper


class PreProcessFactory(object):
    _pre_process_pool: Dict[str, PreProcessBase] = {}

    @classmethod
    @typeassert(name=str)
    def get_pre_process(cls, name):
        return cls._pre_process_pool.get(name, None)

    @classmethod
    @typeassert(name=str)
    def register(cls, name):
        def _wrapper(preprocess_cls: Type[PreProcessBase]):
            if cls.get_pre_process(name) is not None:
                logging.warning(f"register name is the same, please check! {name}")
                raise RuntimeError(f"register name is the same, please check! {name}")
            cls._pre_process_pool[name] = preprocess_cls()
            return preprocess_cls
        return _wrapper


class InferenceFactory(object):
    _inference_pool: Dict[str, InferenceBase] = {}

    @classmethod
    @typeassert(name=str)
    def get_inference(cls, name):
        return cls._inference_pool.get(name, None)

    @classmethod
    @typeassert(name=str)
    def register(cls, name):
        def _wrapper(inference_cls: Type[InferenceBase]):
            if cls.get_inference(name) is not None:
                logging.warning(f"register name is the same, please check! {name}")
                raise RuntimeError(f"register name is the same, please check! {name}")
            cls._inference_pool[name] = inference_cls()
            return inference_cls
        return _wrapper


class PostProcessFactory(object):
    _post_process_pool: Dict[str, PostProcessBase] = {}

    @classmethod
    @typeassert(name=str)
    def get_post_process(cls, name):
        return cls._post_process_pool.get(name, None)

    @classmethod
    @typeassert(name=str)
    def register(cls, name):
        def _wrapper(post_process_cls: Type[PostProcessBase]):
            if cls.get_post_process(name) is not None:
                logging.warning(f"register name is the same, please check! {name}")
                raise RuntimeError(f"register name is the same, please check! {name}")
            cls._post_process_pool[name] = post_process_cls()
            return post_process_cls
        return _wrapper


class EvaluateFactory(object):
    _evaluate_pool: Dict[str, EvaluateBase] = {}

    @classmethod
    @typeassert(name=str)
    def get_evaluate(cls, name):
        return cls._evaluate_pool.get(name, None)

    @classmethod
    @typeassert(name=str)
    def register(cls, name):
        def _wrapper(evaluate_cls: Type[EvaluateBase]):
            if cls.get_evaluate(name) is not None:
                logging.warning(f"register name is the same, please check! {name}")
                raise RuntimeError(f"register name is the same, please check! {name}")
            cls._evaluate_pool[name] = evaluate_cls()
            return evaluate_cls
        return _wrapper
