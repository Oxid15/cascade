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

from cascade.models import Model


def test_add_file(tmp_path_str):

    message = "Hello I am artifact"
    filepath = os.path.join(tmp_path_str, "file.txt")
    with open(filepath, "w") as f:
        f.write(message)

    model = Model()
    model.add_file(filepath)
    model.save(os.path.join(tmp_path_str, "model"))

    with open(os.path.join(tmp_path_str, "model", "files", "file.txt"), "r") as f:
        read_message = f.read()

    assert read_message == message


def test_add_missing_file(tmp_path_str):

    model = Model()
    model.add_file("iammissing.jpg")

    with pytest.raises(FileNotFoundError):
        model.save(os.path.join(tmp_path_str, "model"))

    model = Model()
    model.add_file("iammissingtoobutitsok.jpg", missing_ok=True)
    model.save(os.path.join(tmp_path_str, "model"))


def test_add_callback():
    def set_a_to_1(model):
        model.a = 1

    model = Model(a=0)
    model.add_log_callback(set_a_to_1)
    model.add_metric("acc", 0.0)
    model.log()

    assert model.metrics[0].name == "acc"
    assert model.metrics[0].value == 0.0
    assert model.a == 1
