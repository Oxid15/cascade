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

import builtins
import io
import pickle
from typing import Any

safe_builtins = {
    'range',
    'complex',
    'set',
    'frozenset',
    'slice',
}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module == "builtins" and name in safe_builtins:
            return getattr(builtins, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))


class Serializer:
    @staticmethod
    def deserialize(obj: str):
        RestrictedUnpickler(io.BytesIO(bytes.fromhex(obj))).load()

    @staticmethod
    def serialize(obj: Any) -> str:
        return pickle.dumps(obj).hex()
