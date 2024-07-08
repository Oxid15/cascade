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

from typing import Any


def create_container(type: str, cwd: str) -> Any:
    if type == "line":
        from cascade.models import ModelLine

        return ModelLine(cwd)
    elif type == "repo":
        from cascade.models import ModelRepo

        return ModelRepo(cwd)
    elif type == "workspace":
        from cascade.models import Workspace

        return Workspace(cwd)
    else:
        return