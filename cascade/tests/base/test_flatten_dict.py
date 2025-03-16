"""
Copyright 2022-2025 Ilia Moiseev

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

from cascade.base.utils import flatten_dict


def test_flatten_dict():

    nested_dict = {
        "name": "John",
        "age": 30,
        "address": {"street": "123 Main St", "city": "Anytown", "state": "CA", "zip": "12345"},
        "contacts": [
            {"type": "email", "value": "john@example.com"},
            {"type": "phone", "value": "123-456-7890"},
        ],
    }

    expected_flattened_dict = {
        "name": "John",
        "age": 30,
        "address_street": "123 Main St",
        "address_city": "Anytown",
        "address_state": "CA",
        "address_zip": "12345",
        "contacts_0_type": "email",
        "contacts_0_value": "john@example.com",
        "contacts_1_type": "phone",
        "contacts_1_value": "123-456-7890",
    }

    flattened_dict = flatten_dict(nested_dict)

    assert flattened_dict == expected_flattened_dict


def test_different_types():
    nested_dict = {
        "set": {1, 2, 3},
        "tuple": ("a", "b", "c"),
        "none": None,
        "bool": True,
    }

    expected_flattened_dict = {
        "set_0": 1,
        "set_1": 2,
        "set_2": 3,
        "tuple_0": "a",
        "tuple_1": "b",
        "tuple_2": "c",
        "none": None,
        "bool": True,
    }

    flattened_dict = flatten_dict(nested_dict)

    assert flattened_dict == expected_flattened_dict
