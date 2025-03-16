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

from argparse import Namespace
from typing import Any, Callable, Dict, List, Union


class Config:
    def __init__(self, cfg: Union[Dict[str, Any], Namespace, None] = None):
        if isinstance(cfg, Namespace):
            cfg = vars(cfg)
        elif cfg is None:
            cfg = {}
        elif not isinstance(cfg, dict):
            raise TypeError(
                f"Argument of type {type(cfg)} passed."
                " You can initialize the Config only with dict or argparse.Namespace"
            )

        self.__dict__.update(cfg)

    def _get_fields(self) -> List[str]:
        d = self.to_dict()
        fields = []
        for name in d:
            fields.append(f"{name}={str(d[name])}")
        return fields

    def __repr__(self):
        prefix = "Config"
        fields = self._get_fields()
        fields_str = ", ".join(fields)
        return f"{prefix}({fields_str})"

    def to_dict(self):
        d = {}
        for name in dir(self):
            if not name.startswith("_"):
                attr = getattr(self, name)
                if isinstance(attr, Callable):
                    continue
                d[name] = attr
        return d
