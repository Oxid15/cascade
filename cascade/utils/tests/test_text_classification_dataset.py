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

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.utils.nlp import TextClassificationFolder


def test_create(tmp_path):
    tmp_path = str(tmp_path)
    paths = [f"class_{i}" for i in range(3)]

    for path in paths:
        path = os.path.join(tmp_path, path)
        os.mkdir(path)

        with open(os.path.join(path, "text_1.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(path, "text_2.txt"), "w") as f:
            f.write("hello")

    ds = TextClassificationFolder(tmp_path)
    meta = ds.get_meta()[0]

    assert meta["size"] == 6
    assert len(meta["labels"]) == 3
