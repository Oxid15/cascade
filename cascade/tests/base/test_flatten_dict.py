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
