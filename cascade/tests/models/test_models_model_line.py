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

import glob
import os
import shutil
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler, default_meta_format
from cascade.models import BasicModel, ModelLine
from cascade.tests.conftest import DummyModel


def test_save_load(old_model_line, dummy_model):
    dummy_model.a = 0
    dummy_model.params.update({"b": "test"})

    old_model_line.save(dummy_model)
    model = old_model_line[0]

    assert len(old_model_line) == 1
    assert model.a == 0
    assert model.params["b"] == "test"


def test_meta(old_model_line, dummy_model):
    old_model_line.save(dummy_model)
    meta = old_model_line.get_meta()

    assert meta[0]["model_cls"] == repr(DummyModel)
    assert meta[0]["len"] == 1


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_change_of_format(tmp_path_str, ext):
    ModelLine(tmp_path_str, meta_fmt=ext)

    assert os.path.exists(os.path.join(tmp_path_str, "meta" + ext))

    ModelLine(tmp_path_str)

    # Check that no other meta is created
    assert len(glob.glob(os.path.join(tmp_path_str, "meta.*"))) == 1


def test_same_index_check(old_model_line):
    for _ in range(5):
        old_model_line.save(BasicModel())

    shutil.rmtree(os.path.join(old_model_line.get_root(), "00001"))
    shutil.rmtree(os.path.join(old_model_line.get_root(), "00002"))
    shutil.rmtree(os.path.join(old_model_line.get_root(), "00003"))

    old_model_line.save(BasicModel())

    assert os.path.exists(os.path.join(old_model_line.get_root(), "00005"))


# TODO: write tests for exceptions
def test_load_model_meta_slug(old_model_line, dummy_model):
    dummy_model.evaluate()
    old_model_line.save(dummy_model)

    with open(os.path.join(old_model_line.get_root(), "00000", "SLUG"), "r") as f:
        slug = f.read()
    meta = old_model_line.load_model_meta(slug)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert slug == meta[0]["slug"]


def test_load_model_meta_num(old_model_line, dummy_model):
    dummy_model.evaluate()
    old_model_line.save(dummy_model)

    meta = old_model_line.load_model_meta(0)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert meta[0]["metrics"][0]["value"] == dummy_model.metrics[0].value


def test_load_artifact_paths(tmp_path_str, old_model_line, dummy_model):
    filename = os.path.join(tmp_path_str, "file.txt")
    with open(filename, "w") as f:
        f.write("hello")

    dummy_model.add_file(filename)

    old_model_line.save(dummy_model)

    res = old_model_line.load_artifact_paths(0)

    assert "artifacts" in res
    assert "files" in res
    assert len(res["artifacts"]) == 1
    assert len(res["files"]) == 1
    assert res["artifacts"][0] == os.path.join(old_model_line.get_root(), "artifacts", "model")
    assert res["files"][0] == os.path.join(old_model_line.get_root(), "files", "file.txt")


def test_create_model(tmp_path_str):

    line = ModelLine(tmp_path_str, model_cls=BasicModel)
    model = line.create_model(a=0)
    model.add_metric("b", 1)
    model.log()

    assert model.params["a"] == 0
    assert model.metrics[0].name == "b"
    assert model.metrics[0].value == 1
    assert len(line) == 1  # Model is saved only on log()


def test_handle_save_error(tmp_path_str):

    class Fail2SaveModel(BasicModel):
        def save(self, path: str) -> None:
            raise RuntimeError()

    line = ModelLine(tmp_path_str, Fail2SaveModel)

    model = Fail2SaveModel()
    line.save(model)

    meta = MetaHandler.read(os.path.join(tmp_path_str, "00000", "meta" + default_meta_format))
    assert "errors" in meta[0]
    assert "save" in meta[0]["errors"]


def test_handle_save_artifact_error(tmp_path_str):

    class Fail2SaveArtModel(BasicModel):
        def save_artifact(self, path: str) -> None:
            raise RuntimeError()

        def save(self, path: str) -> None:
            pass

    line = ModelLine(tmp_path_str, Fail2SaveArtModel)

    model = Fail2SaveArtModel()
    line.save(model)

    meta = MetaHandler.read(os.path.join(tmp_path_str, "00000", "meta" + default_meta_format))
    assert "errors" in meta[0]
    assert "save_artifact" in meta[0]["errors"]


def test_model_names(tmp_path_str):

    line = ModelLine(tmp_path_str)
    model = line.create_model()

    line.save(model)
    line.save(model)
    line.save(model)

    assert line.get_model_names() == ["00000", "00001", "00002"]

    line = ModelLine(tmp_path_str)
    assert line.get_model_names() == ["00000", "00001", "00002"]

# TODO: write test for restoring line from repo
