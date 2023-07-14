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

import os
import sys

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import FolderDataset


def test(tmp_path):
    tmp_path = str(tmp_path)
    with open(os.path.join(tmp_path, "a.txt"), "w") as w:
        w.write("hello")

    with open(os.path.join(tmp_path, "b.txt"), "w") as w:
        w.write("hello")

    ds = FolderDataset(tmp_path)
    meta = ds.get_meta()[0]

    assert len(ds) == 2
    assert "name" in meta
    assert "len" in meta


def test_names(tmp_path):
    tmp_path = str(tmp_path)
    with open(os.path.join(tmp_path, "a.txt"), "w") as w:
        w.write("hello")

    with open(os.path.join(tmp_path, "b.txt"), "w") as w:
        w.write("hello")

    ds = FolderDataset(tmp_path)
    names = ds.get_names()
    assert os.path.split(names[0])[-1] == "a.txt"
    assert os.path.split(names[1])[-1] == "b.txt"
