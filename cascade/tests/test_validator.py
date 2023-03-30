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
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.meta import DataValidationException, Validator, AggregateValidator, PredicateValidator


def test_modifier_interface(number_dataset):
    ds = Validator(number_dataset, lambda x: True)
    assert number_dataset._data == [item for item in ds]


def test_aggregate_positive(number_dataset):
    ds = AggregateValidator(number_dataset, lambda d: len(d) == len(number_dataset))


def test_aggregate_negative(number_dataset):
    with pytest.raises(DataValidationException):
        ds = AggregateValidator(number_dataset, lambda d: len(d) != len(number_dataset))


def test_predicate_positive(number_dataset):
    ds = PredicateValidator(number_dataset, lambda x: x < float('inf'))


def test_predicate_negative(number_dataset):
    with pytest.raises(DataValidationException):
        ds = PredicateValidator(number_dataset, lambda x: x > float('inf'))


def test_predicate_list_positive(number_dataset):
    ds = PredicateValidator(number_dataset, [
        lambda x: x < float('inf'),
        lambda x: x < float('inf'),
        lambda x: x < float('inf')])


def test_predicate_list_negative(number_dataset):
    with pytest.raises(DataValidationException):
        ds = PredicateValidator(number_dataset, [
            lambda x: x > float('inf'),
            lambda x: x > float('inf'),
            lambda x: x > float('inf')])
