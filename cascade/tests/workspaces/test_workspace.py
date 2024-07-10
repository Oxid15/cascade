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

import os
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))
from cascade.models import ModelRepo, Workspace


def test(tmp_path_str):
    for i in range(10):
        ModelRepo(os.path.join(tmp_path_str, f"repo-{i}"))

    wp = Workspace(tmp_path_str, default_repo="repo-1")

    assert len(wp) == 10
    assert wp.get_repo_names() == [f"repo-{i}" for i in range(10)]
    assert wp.get_default().get_root() == os.path.join(tmp_path_str, "repo-1")
    wp.set_default("repo-2")
    assert wp.get_default().get_root() == os.path.join(tmp_path_str, "repo-2")


def test_meta(tmp_path_str):

    for i in range(10):
        ModelRepo(os.path.join(tmp_path_str, f"repo-{i}"))

    wp = Workspace(tmp_path_str)

    meta = wp.get_meta()
    assert meta[0]["root"] == tmp_path_str
    assert meta[0]["len"] == 10
    assert meta[0]["type"] == "workspace"


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_load_model_meta(tmp_path_str, dummy_model, ext):

    for i in range(2):
        ModelRepo(os.path.join(tmp_path_str, f"repo-{i}"))

    repo = ModelRepo(os.path.join(tmp_path_str, "repo"), meta_fmt=ext)
    repo.add_line()
    repo.add_line()
    line = repo.add_line()

    wp = Workspace(tmp_path_str)

    dummy_model.evaluate()
    line.save(dummy_model)

    with open(os.path.join(line.get_root(), "00000", "SLUG"), "r") as f:
        slug = f.read()

    meta = wp.load_model_meta(slug)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert slug == meta[0]["slug"]


def test_repo_names(tmp_path_str):

    wp = Workspace(tmp_path_str)

    wp.add_repo("0")
    wp.add_repo("1")
    wp.add_repo("2")

    assert wp.get_repo_names() == ["0", "1", "2"]

    wp = Workspace(tmp_path_str)
    assert wp.get_repo_names() == ["0", "1", "2"]
