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

import os
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from cascade.cli.common import create_container


@pytest.mark.parametrize("container_type", ["line", "model_line", "data_line", "repo", "workspace"])
def test(tmp_path_str, container_type):
    c = create_container(container_type, os.path.join(tmp_path_str, container_type))
    meta = c.get_meta()
    if container_type != "line":
        assert meta[0]["type"] == container_type
    else:
        assert meta[0]["type"] == "model_line"
