from cascade.base.utils import flatten_dict


def test_flatten_dict():

    nested_json = {
        "name": "John",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        },
        "contacts": [
            {
                "type": "email",
                "value": "john@example.com"
             },
            {
                "type": "phone",
                "value": "123-456-7890"
             }
        ]
    }

    expected_flattened_json = {
        'name': 'John',
        'age': 30,
        'address_street': '123 Main St',
        'address_city': 'Anytown',
        'address_state': 'CA',
        'address_zip': '12345',
        'contacts_0_type': 'email',
        'contacts_0_value': 'john@example.com',
        'contacts_1_type': 'phone',
        'contacts_1_value': '123-456-7890'
    }

    flattened_json = flatten_dict(nested_json)

    assert flattened_json == expected_flattened_json