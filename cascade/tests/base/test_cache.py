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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import Cache, Traceable


@pytest.mark.parametrize("backend", ["pickle"])
def test(tmp_path_str, backend):
    cache = Cache(tmp_path_str, backend=backend)

    assert cache.exists() is False

    cache.save(Traceable(description="Hello"))

    assert cache.exists() is True

    obj = cache.load()

    assert obj.description == "Hello"
