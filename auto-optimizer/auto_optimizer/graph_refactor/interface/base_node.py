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

import warnings
from abc import ABC, abstractmethod
from typing import List, Dict, Union

import numpy as np

class BaseNode(ABC):

    @classmethod
    @abstractmethod
    def parse(self, node):
        pass
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name:str):
        self._name = name

    @property
    def op_type(self):
        return self._op_type


class Node(BaseNode):
    def __init__(
        self,
        name: str = None,
        op_type: str = None,
        inputs: List[str] = None,
        outputs: List[str] = None,
        attrs: Dict[str, object] = None,
        domain: str = None
    ):
        """
        A node represents a computation operator in a graph.

        Args:
            name(str): The name of this node.
            op_type(str): The operaton type of this node.
            attrs (Dict[str, object]): A dictionary that maps attribute names to their values.
            inputs (List[Tensor]): A list of zero or more input names.
            outputs (List[Tensor]): A list of zero or more output names.
        """
        self._name = name
        self._op_type = op_type
        self._inputs = inputs or []
        self._outputs = outputs or []
        self._attrs = attrs or {}
        self._domain = domain
    
    @classmethod
    def parse(cls, node):
        pass

    @property
    def inputs(self) -> List[str]:
        return self._inputs
    
    @inputs.setter
    def inputs(self, inputs:List[str]):
        self._inputs = inputs
    
    def get_input_id(self, node_input:str) -> str:
        if node_input not in self._inputs:
            raise RuntimeError(
                f'Name of input should be one of {self._inputs}')
        else:
            return self._inputs.index(node_input)

    @property
    def outputs(self) -> List[str]:
        return self._outputs
    
    @outputs.setter
    def outputs(self, outputs:List[str]):
        self._outputs = outputs
    
    def get_output_id(self, output:str) -> str:
        if output not in self._outputs:
            raise RuntimeError(
                f'Name of output should be one of {self._outputs}')
        else:
            return self._outputs.index(output)
    
    @property
    def attrs(self) -> Dict[str, object]:
        return self._attrs
    
    def __getitem__(self, key) -> object:
        if key not in self._attrs:
            raise KeyError(
                f'Node({self.name}) do not have {key} attribute.')
        return self._attrs[key]

    def __setitem__(self, key, value):
        if key not in self._attrs:
            warnings.warn(
                f'Node({self.name}) do not have {key} attribute.')
        self._attrs[key] = value

    @property
    def domain(self):
        return self._domain

    def __str__(self) -> str:
        return f'Node({self.name}): \n\tinputs={self.inputs}\n\toutputs={self.outputs}\n\tattrs = {self.attrs}\n'

    def __repr__(self) -> str:
        return self.__str__()


class Initializer(BaseNode):
    def __init__(
        self,
        name: str = None,
        value: np.ndarray = None
    ):
        """
        An initializer represents a tensor which specifies for a graph input or a constant node.

        Args:
            name(str): The name of this initializer.
            value(np.ndarray): The constant value of this initializer.
        """
        self._name = name
        self._op_type = 'Initializer'
        self._value = value

    @classmethod
    def parse(cls, node):
        pass

    @property
    def value(self) -> np.ndarray:
        return self._value
    
    @value.setter
    def value(self, value:np.ndarray):
        self._value = value
    
    def __str__(self) -> str:
        return f'{self.op_type}({self.name}): (shape={self._value.shape}, dtype={self._value.dtype})\n'

    def __repr__(self) -> str:
        return self.__str__()


class PlaceHolder(BaseNode):
    def __init__(
        self,
        name: str = None,
        dtype: np.dtype = None,
        shape: List[int] = None
    ):
        """
        A placeholder used to store the type and shape information.

        Args:
            name(str): The name of this placeHolder.
            dtype(np.dtype): The data type of this placeHolder.
            shape(List[int]): The shape of this placeHolder.
        """
        self._name = name
        self._op_type = 'PlaceHolder'
        self._dtype = dtype
        self._shape = shape

    @classmethod
    def parse(cls, node):
        pass

    @property
    def dtype(self) -> np.dtype:
        return self._dtype
    
    @dtype.setter
    def dtype(self, dtype:np.dtype):
        self._dtype = dtype

    @property
    def shape(self) -> List[Union[str,int]]:
        return self._shape
    
    @shape.setter
    def shape(self, shape:List[Union[str,int]]):
        if -1 in shape:
            warnings.warn('To represent the dynamic dimension int -1 is converted to str "-1".')
        self._shape = ['-1' if dim == -1 else dim for dim in shape]
    
    def __str__(self) -> str:
        return f'{self.op_type}({self.name}): (shape={self.shape}, dtype={self.dtype})\n'

    def __repr__(self) -> str:
        return self.__str__()