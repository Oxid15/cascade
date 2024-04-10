"""
Copyright 2022-2023 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
from typing import Dict, List

import pydantic
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import ValidationError, validate_in


def test_no_annot():
    def add(a, b):
        return a + b

    validate_in(add)(1, 2)
    validate_in(add)("a", "b")


def test_default_types():
    def add_int(a: int, b: int):
        return a + b

    validate_in(add_int)(1, 2)

    with pytest.raises(ValidationError):
        validate_in(add_int)("a", 2)

    with pytest.raises(ValidationError):
        validate_in(add_int)(1, "b")

    with pytest.raises(ValidationError):
        validate_in(add_int)("a", "b")

    with pytest.raises(ValidationError):
        validate_in(add_int)(1.2, 3.4)


def test_lists():
    def sum_list(a: List[float]):
        return sum(a)

    validate_in(sum_list)([1.2, 3.4, 5.])

    with pytest.raises(ValidationError):
        validate_in(sum_list)(None)

    with pytest.raises(ValidationError):
        validate_in(sum_list)(["a", "b"])


def test_dicts():
    def sum_dict(a: Dict[str, int]):
        return sum(a.values())

    sum_dict({"a": 2, "b": 1})

    with pytest.raises(ValidationError):
        validate_in(sum_dict)([1, 2, 3])

    with pytest.raises(ValidationError):
        validate_in(sum_dict)(3)

    with pytest.raises(ValidationError):
        validate_in(sum_dict)({1: 2, 3: 4})

    with pytest.raises(ValidationError):
        validate_in(sum_dict)({"a": "b", "c": "d"})


def test_pydantic_model():
    class LargeModel(pydantic.BaseModel):
        int_: int
        float_: float
        str_: str
        dict_: dict
        list_: list
        li: List[int]
        ds: Dict[str, float]

    def identity(a: LargeModel):
        return a

    validate_in(
        identity)(dict(
            int_=0, float_=0., str_="a", dict_=dict(), list_=list(), li=[0, 1], ds={"a": 1.}
        )
    )

    with pytest.raises(ValidationError):
        validate_in(identity)(
            dict(
                int_="err", float_=0., str_="a", dict_=dict(), list_=list(), li=[0, 1], ds={"a": 1.}
            )
        )


def test_pydantic_field():
    def identity(a: int = pydantic.Field(le=0)):
        return a

    validate_in(identity)(0)

    with pytest.raises(ValidationError):
        validate_in(identity)(10000)
