"""
Copyright 2022-2024 Ilia Moiseev

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

from typing import Callable, List


class Config:
    def _get_fields(self) -> List[str]:
        fields = []
        for name in dir(self):
            if not name.startswith("_"):
                attr = getattr(self, name)
                if isinstance(attr, Callable):
                    continue
                fields.append(f"{name}={str(attr)}")
        return fields

    def __repr__(self):
        prefix = "Config"
        fields = self._get_fields()
        fields_str = ", ".join(fields)
        return f"{prefix}({fields_str})"

    def to_dict(self):
        fields = self._get_fields()
        d = {}
        for f in fields:
            d[f] = getattr(self, f)

        return d
