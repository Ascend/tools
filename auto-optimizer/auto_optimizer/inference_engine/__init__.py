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

from .pre_process.pre_process_base import PreProcessBase
from .post_process.post_process_base import PostProcessBase
from .evaluate.evaluate_base import EvaluateBase
from .inference.inference_base import InferenceBase


__all__ = ["PreProcessBase", "PostProcessBase", "EvaluateBase", "InferenceBase"]
