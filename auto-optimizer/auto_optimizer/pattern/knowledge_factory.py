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


from typing import Dict, Optional, Type
from .knowledges.knowledge_base import KnowledgeBase


class KnowledgeFactory(object):
    _knowledge_pool: Dict[str, KnowledgeBase] = {}

    @classmethod
    def add_knowledge(cls, name, knowledge: KnowledgeBase):
        cls._knowledge_pool[name] = knowledge

    @classmethod
    def get_knowledge(cls, name) -> Optional[KnowledgeBase]:
        return cls._knowledge_pool.get(name)

    @classmethod
    def get_knowledge_pool(cls) -> Dict[str, KnowledgeBase]:
        return cls._knowledge_pool

    @classmethod
    def register(cls, name: str = ''):
        def _deco(knowledge_cls: Type[KnowledgeBase]):
            registered_name = name if name else knowledge_cls.__name__
            cls.add_knowledge(registered_name, knowledge_cls())
            return knowledge_cls
        return _deco
