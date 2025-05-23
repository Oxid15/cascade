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
from click.testing import CliRunner

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.base import MetaHandler
from cascade.data import BaseDataset, Modifier
from cascade.cli.cli import cli
from cascade.repos import Repo
from cascade.lines import ModelLine, DataLine
from cascade.workspaces import Workspace


class DummyDataset(BaseDataset):
    def __len__(self):
        return 0

    def __getitem__(self, index) -> None:
        return None


def create_entity(entity_type: str, root: str) -> str:
    if entity_type == "workspace":
        Workspace(root)
        return root
    if entity_type == "repo":
        Repo(root)
        return root
    elif entity_type == "model_line":
        ModelLine(root)
        return root
    elif entity_type == "data_line":
        DataLine(root)
        return root
    elif entity_type == "model":
        line = ModelLine(root)
        model = line.create_model()
        line.save(model, only_meta=True)
        return os.path.join(root, "00000")
    elif entity_type == "dataset":
        line = DataLine(root)
        ds = DummyDataset()
        ds = Modifier(ds)
        line.save(ds, only_meta=True)
        return os.path.join(root, "0.1")

@pytest.mark.parametrize(
    "entity_type",
    [
        "workspace",
        "repo",
        "model_line",
        "data_line",
        "model",
        "dataset",
    ],
)
def test_add(tmp_path_str, entity_type):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        td = create_entity(entity_type, td)

        init_meta = MetaHandler.read_dir(td)

        result = runner.invoke(cli, args=["comment", "add"], input="Hello")

        assert result.exit_code == 0

        meta = MetaHandler.read_dir(td)

        assert "comments" in meta[0]
        assert len(meta[0]["comments"]) == 1
        assert meta[0]["comments"][0]["message"] == "Hello"

        meta[0]["comments"] = []

        # Those will obviously be different
        del meta[0]["updated_at"]
        del init_meta[0]["updated_at"]

        assert meta == init_meta


# TODO: will need to make this work inside pytest
@pytest.mark.skip
def test_ls(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        mh = MetaHandler()
        Repo(td)

        mh.read_dir(td)

        result = runner.invoke(cli, args=["comment", "add"], input="Hello")
        assert result.exit_code == 0

        result = runner.invoke(cli, args=["comment", "ls"])
        assert result.exit_code == 0

        assert "Hello" in result.output


def test_rm(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        mh = MetaHandler()
        Repo(td)

        init_meta = mh.read_dir(td)

        result = runner.invoke(cli, args=["comment", "add"], input="Hello")
        assert result.exit_code == 0

        result = runner.invoke(cli, args=["comment", "rm", "1"])
        assert result.exit_code == 0

        meta = mh.read_dir(td)

        assert "comments" in meta[0]
        assert len(meta[0]["comments"]) == 0

        del meta[0]["updated_at"]
        del init_meta[0]["updated_at"]
        assert meta == init_meta

        # Test of removing nonexisting comment
        result = runner.invoke(cli, args=["comment", "rm", "1"])
        assert result.exit_code == 1
