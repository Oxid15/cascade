"""
Copyright 2022-2026 Ilia Moiseev

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
from typing import Any, Dict, List

import pytest

from cascade.data import Wrapper
from cascade.models import BasicModel
from cascade.repos import Repo
from cascade.lines import DataLine, ModelLine
from cascade.workspaces import Workspace


def init_workspace(path: str, params_list: List[Dict[str, Any]]):
    Workspace(path)
    init_repo(os.path.join(path, "repo"), params_list)


def init_repo(
    path: str, params_list: List[Dict[str, Any]], with_data_line: bool = True
):
    Repo(path)
    init_model_line(os.path.join(path, "model_line"), params_list)
    if with_data_line:
        init_data_line(os.path.join(path, "data_line"))


def init_model_line(path: str, params_list: List[Dict[str, Any]]):
    line = ModelLine(path)

    for p in params_list:
        model = BasicModel()
        model.params.update(p)
        line.save(model)


def init_data_line(path: str):
    line = DataLine(path)
    line.save(Wrapper([]))


@pytest.mark.parametrize("container_type", ["workspace", "repo", "model_line"])
def init_container(
    temp_dir: str, params_list: List[Dict[str, Any]], container_type: str
):
    if container_type == "workspace":
        init_workspace(temp_dir, params_list)
    elif container_type == "repo":
        init_repo(temp_dir, params_list)
    elif container_type == "model_line":
        init_model_line(temp_dir, params_list)
    else:
        raise ValueError(f"Cannot init {container_type} container")
