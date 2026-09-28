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

import glob
import os
import shutil
import subprocess
import sys
from multiprocessing import Process

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler, default_meta_format
from cascade.lines import ModelLine
from cascade.models import BasicModel
from cascade.repos import Repo


def run_as_subprocess(f):
    p = Process(target=f)
    p.start()
    p.join()


def run_as_script(script: str, name: str, cwd: str):
    script_path = os.path.join(cwd, f"{name}.py")
    with open(script_path, "w") as f:
        f.write(script)

    result = subprocess.Popen([sys.executable, script_path], cwd=cwd)
    result.wait()

    assert result.returncode == 0


def test_save_load(model_line, dummy_model):
    dummy_model.a = 0
    dummy_model.params.update({"b": "test"})

    model_line.save(dummy_model)
    model = model_line[0]

    assert len(model_line) == 1
    assert model.a == 0
    assert model.params["b"] == "test"


def test_meta(model_line, dummy_model):
    model_line.save(dummy_model)
    meta = model_line.get_meta()

    assert meta[0]["item_cls"] == "DummyModel"
    assert meta[0]["len"] == 1


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_change_of_format(tmp_path_str, ext):
    ModelLine(tmp_path_str, meta_fmt=ext)

    assert os.path.exists(os.path.join(tmp_path_str, "meta" + ext))

    ModelLine(tmp_path_str)

    # Check that no other meta is created
    assert len(glob.glob(os.path.join(tmp_path_str, "meta.*"))) == 1


def test_external_remove_first(model_line):
    for _ in range(5):
        model_line.save(BasicModel())

    shutil.rmtree(os.path.join(model_line.get_root(), "00000"))

    model_line = ModelLine(model_line.get_root())
    model_line.save(BasicModel())

    assert os.path.exists(os.path.join(model_line.get_root(), "00005"))


def test_external_remove_middle(model_line):
    for _ in range(5):
        model_line.save(BasicModel())

    shutil.rmtree(os.path.join(model_line.get_root(), "00002"))

    model_line = ModelLine(model_line.get_root())
    model_line.save(BasicModel())

    assert os.path.exists(os.path.join(model_line.get_root(), "00005"))


def test_external_remove_last(model_line):
    for _ in range(5):
        model_line.save(BasicModel())

    shutil.rmtree(os.path.join(model_line.get_root(), "00004"))

    model_line = ModelLine(model_line.get_root())
    model_line.save(BasicModel())

    assert os.path.exists(os.path.join(model_line.get_root(), "00004"))


# TODO: write tests for exceptions
def test_load_model_meta_slug(model_line, dummy_model):
    dummy_model.evaluate()
    model_line.save(dummy_model)

    with open(os.path.join(model_line.get_root(), "00000", "SLUG"), "r") as f:
        slug = f.read()
    meta = model_line.load_model_meta(slug)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert slug == meta[0]["slug"]


def test_load_model_meta_num(model_line, dummy_model):
    dummy_model.evaluate()
    model_line.save(dummy_model)

    meta = model_line.load_model_meta(0)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert meta[0]["metrics"][0]["value"] == dummy_model.metrics[0].value


def test_load_artifact_paths(tmp_path_str, model_line, dummy_model):
    filename = os.path.join(tmp_path_str, "file.txt")
    with open(filename, "w") as f:
        f.write("hello")

    dummy_model.add_file(filename)

    model_line.save(dummy_model)

    res = model_line.load_artifact_paths(0)

    assert "artifacts" in res
    assert "files" in res
    assert len(res["artifacts"]) == 1
    assert len(res["files"]) == 1
    assert res["artifacts"][0] == os.path.join(
        model_line.get_root(), "00000", "artifacts", "model"
    )
    assert res["files"][0] == os.path.join(
        model_line.get_root(), "00000", "files", "file.txt"
    )


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

    meta = MetaHandler.read(
        os.path.join(tmp_path_str, "00000", "meta" + default_meta_format)
    )
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

    meta = MetaHandler.read(
        os.path.join(tmp_path_str, "00000", "meta" + default_meta_format)
    )
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


def test_line_comment(tmp_path_str):
    line_dir = os.path.join(tmp_path_str, "line")
    os.makedirs(line_dir, exist_ok=True)

    line = ModelLine(line_dir)
    line.comment("This comment should stay")

    # Recreate
    line = ModelLine(line_dir)
    meta = MetaHandler.read_dir(line_dir)
    assert len(meta[0]["comments"]) > 0

    # Recreate alternative
    line = Repo(tmp_path_str).add_line("line")
    meta = MetaHandler.read_dir(line_dir)
    assert len(meta[0]["comments"]) > 0


def test_simple_save_load_import_handling(tmp_path_str):

    def isolated_save():
        from cascade.tests.conftest import DummyModel

        line = ModelLine(tmp_path_str)
        model = DummyModel()

        line.save(model)

    run_as_subprocess(isolated_save)

    line = ModelLine(tmp_path_str)
    model = line.load(0)

    from cascade.tests.conftest import DummyModel

    assert isinstance(model, DummyModel)
    slug = line.load_model_meta(0)[0]["slug"]
    assert isinstance(line.load(slug), DummyModel)

    meta = line.load_obj_meta(0)

    assert meta[0]["module_file"].endswith("cascade/tests/conftest.py")
    assert meta[0]["class"] == "DummyModel"


@pytest.mark.parametrize("missing_key", ["module_file", "class"])
def test_autoimport_requires_class_metadata(tmp_path_str, missing_key):
    from cascade.tests.conftest import DummyModel

    line = ModelLine(tmp_path_str)
    line.save(DummyModel())
    meta_path = os.path.join(tmp_path_str, "00000", "meta" + default_meta_format)
    meta = MetaHandler.read(meta_path)
    meta[0].pop(missing_key)
    MetaHandler.write(meta_path, meta)

    with pytest.raises(KeyError, match="module_file.*class"):
        line.load(0)


def test_autoimport_rejects_missing_module_file(tmp_path_str):
    from cascade.tests.conftest import DummyModel

    line = ModelLine(tmp_path_str)
    line.save(DummyModel())
    meta_path = os.path.join(tmp_path_str, "00000", "meta" + default_meta_format)
    meta = MetaHandler.read(meta_path)
    meta[0]["module_file"] = None
    MetaHandler.write(meta_path, meta)

    with pytest.raises(ValueError, match="module_file.*None"):
        line.load(0)


def test_autoimport_rejects_missing_class_in_module(tmp_path_str):
    from cascade.tests.conftest import DummyModel

    line = ModelLine(tmp_path_str)
    line.save(DummyModel())
    meta_path = os.path.join(tmp_path_str, "00000", "meta" + default_meta_format)
    meta = MetaHandler.read(meta_path)
    meta[0]["class"] = "MissingModel"
    MetaHandler.write(meta_path, meta)

    with pytest.raises(AttributeError, match="MissingModel"):
        line.load(0)


def test_class_defined_at_main(tmp_path_str):
    script = "\n".join(
        (
            "from cascade.models import Model",
            "from cascade.lines import ModelLine",
            "class MainModel(Model):",
            "    def save(self, *args, **kwargs):",
            "        ...",
            "    def save_artifact(self, *args, **kwargs):",
            "        ...",
            "    @classmethod",
            "    def load(cls, *args, **kwargs):",
            "        return cls()",
            "    @classmethod",
            "    def load_artifact(self, *args, **kwargs):",
            "        ...",
            "if __name__ == '__main__':",
            "    line = ModelLine('line')",
            "    line.save(MainModel())",
        )
    )

    save_location = os.path.join(tmp_path_str, "saved")
    os.makedirs(save_location)

    run_as_script(script, "save", save_location)

    assert os.path.exists(os.path.join(tmp_path_str, "saved", "line", "00000"))

    load_location = os.path.join(tmp_path_str, "loaded")
    os.makedirs(load_location)

    script = "\n".join(
        (
            "from cascade.lines import ModelLine",
            "line = ModelLine('../saved/line')",
            "model = line.load(0)",
            "assert model.__class__.__name__ == 'MainModel'",
        )
    )

    run_as_script(script, "load", load_location)


def test_run_with_no_source_code(tmp_path_str):
    script = "\n".join(
        (
            "from cascade.models import Model",
            "from cascade.lines import ModelLine",
            "class MainModel(Model):",
            "    def save(self, *args, **kwargs):",
            "        ...",
            "    def save_artifact(self, *args, **kwargs):",
            "        ...",
            "    @classmethod",
            "    def load(cls, *args, **kwargs):",
            "        return cls()",
            "    @classmethod",
            "    def load_artifact(self, *args, **kwargs):",
            "        ...",
            "if __name__ == '__main__':",
            "    line = ModelLine('line')",
            "    line.save(MainModel())",
        )
    )

    save_location = os.path.join(tmp_path_str, "saved")
    os.makedirs(save_location)

    result = subprocess.Popen([sys.executable, "-c", script], cwd=save_location)
    result.wait()

    line = ModelLine(os.path.join(save_location, "line"))
    assert len(line) == 1

    meta = line.load_obj_meta(0)
    assert (
        meta[0]["module_file"] is None
    )  # could not get module file since there was no file
    assert meta[0]["class"] == "MainModel"


def test_class_imported_from_file(tmp_path_str):
    script = (
        "from cascade.models import Model",
        "from cascade.lines import ModelLine",
        "class MainModel(Model):",
        "    def save(self, *args, **kwargs):",
        "        ...",
        "    def save_artifact(self, *args, **kwargs):",
        "        ...",
        "    @classmethod",
        "    def load(cls, *args, **kwargs):",
        "        return cls()",
        "    @classmethod",
        "    def load_artifact(self, *args, **kwargs):",
        "        ...",
    )
    script = "\n".join(script)

    save_location = os.path.join(tmp_path_str, "saved")
    os.makedirs(save_location)
    script_path = os.path.join(save_location, "model.py")
    with open(script_path, "w") as f:
        f.write(script)

    script = (
        "from model import MainModel",
        "from cascade.lines import ModelLine",
        "if __name__ == '__main__':",
        "   line = ModelLine('../saved/line')",
        "   model = line.save(MainModel())",
    )
    script = "\n".join(script)

    run_as_script(script, "save", save_location)

    load_location = os.path.join(tmp_path_str, "loaded")
    os.makedirs(load_location)

    script = (
        "from cascade.lines import ModelLine",
        "line = ModelLine('../saved/line')",
        "model = line.load(0)",
        "assert model.__class__.__name__ == 'MainModel'",
    )
    script = "\n".join(script)

    run_as_script(script, "load", load_location)

    line = ModelLine(os.path.join(tmp_path_str, "saved", "line"))
    assert len(line) == 1

    model = line.load(0)
    assert model.__class__.__name__ == "MainModel"
