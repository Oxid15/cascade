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
import sys
from unittest.mock import patch

from click.testing import CliRunner

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.base import MetaHandler
from cascade.cli.cli import cli
from cascade.data import Wrapper
from cascade.lines import DataLine, ModelLine
from cascade.models import BasicModel
from cascade.repos import Repo
from cascade.workspaces import Workspace


class TestModel(BasicModel):
    def save_artifact(self, path: str):
        with open(os.path.join(path, "artifact.txt"), "w") as f:
            f.write("Hello")


def test_rm_workspace(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        Workspace(td)
        for repo_n in range(2):
            repo = Repo(str(repo_n))
            for line_n in range(2):
                line = repo.add_line(str(line_n))
                for i in range(5):
                    model = TestModel()
                    line.save(model)
                    assert os.path.exists(
                        os.path.join(
                            td,
                            str(repo_n),
                            str(line_n),
                            f"{i:0>5d}",
                            "artifacts",
                            "artifact.txt",
                        )
                    )

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0

        for repo_n in range(2):
            for line_n in range(2):
                for i in range(5):
                    assert not os.path.exists(
                        os.path.join(
                            td,
                            str(repo_n),
                            str(line_n),
                            "00000",
                            f"{i:0>5d}",
                            "artifacts",
                            "artifact.txt",
                        )
                    )


def test_rm_repo(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        repo = Repo(td)
        for line_n in range(5):
            line = repo.add_line(str(line_n))
            for i in range(5):
                model = TestModel()
                line.save(model)
                assert os.path.exists(
                    os.path.join(
                        td, str(line_n), f"{i:0>5d}", "artifacts", "artifact.txt"
                    )
                )

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0

        for line_n in range(5):
            for i in range(5):
                assert not os.path.exists(
                    os.path.join(
                        td,
                        str(line_n),
                        "00000",
                        f"{i:0>5d}",
                        "artifacts",
                        "artifact.txt",
                    )
                )


def test_rm_line(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        line = ModelLine(td)
        for i in range(5):
            model = TestModel()
            line.save(model)
            assert os.path.exists(
                os.path.join(td, f"{i:0>5d}", "artifacts", "artifact.txt")
            )

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0

        for i in range(5):
            assert not os.path.exists(
                os.path.join(td, f"{i:0>5d}", "artifacts", "artifact.txt")
            )


def test_rm_model(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        artifact_path = os.path.join(td, "artifacts")
        os.makedirs(artifact_path)
        model = TestModel()
        model.save_artifact(artifact_path)
        MetaHandler.write_dir(td, model.get_meta())

        assert os.path.exists(os.path.join(td, "artifacts", "artifact.txt"))

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0

        assert not os.path.exists(os.path.join(td, "artifacts", "artifact.txt"))


def test_rm_model_error(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        artifact_path = os.path.join(td, "artifacts")
        os.makedirs(artifact_path)
        model = TestModel()
        model.save_artifact(artifact_path)
        MetaHandler.write_dir(td, model.get_meta())

        assert os.path.exists(os.path.join(td, "artifacts", "artifact.txt"))

        with patch("os.remove") as mocked_remove:
            mocked_remove.side_effect = OSError()

            result = runner.invoke(cli, args=["artifact", "rm", "-y"])
            assert result.exit_code == 0

            mocked_remove.assert_called_once_with(
                os.path.join(td, "artifacts", "artifact.txt")
            )

            assert os.path.exists(os.path.join(td, "artifacts", "artifact.txt"))


def test_rm_does_not_change_line_type(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        repo = Repo(td)

        model_line = repo.add_line("model_line", line_type="model")
        for _ in range(2):
            model_line.save(TestModel())

        data_line = repo.add_line("data_line", line_type="data")
        data_line.save(Wrapper([0, 1, 2]))

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0

        for name, line_type, item_cls in (
            ("model_line", "model_line", "Model"),
            ("data_line", "data_line", "Dataset"),
        ):
            meta = MetaHandler.read_dir(os.path.join(td, name))
            assert meta[0]["type"] == line_type
            assert meta[0]["item_cls"] == item_cls


def test_rm_exits_correctly_on_data_line(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        line = DataLine(td)
        line.save(Wrapper([0, 1, 2]))
        line.save(Wrapper([0, 1, 2, 3]))

        version_names = line.get_item_names()
        assert len(version_names) == 2

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0
        assert "Found 0 files inside" in result.output
        assert "Failed: 0" in result.output

        meta = MetaHandler.read_dir(td)
        assert meta[0]["type"] == "data_line"
        assert meta[0]["item_cls"] == "Dataset"

        for name in version_names:
            assert os.path.exists(os.path.join(td, name, "object.pkl"))


def test_idempotency(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        line = ModelLine(td)
        for i in range(5):
            model = TestModel()
            line.save(model)
            assert os.path.exists(
                os.path.join(td, f"{i:0>5d}", "artifacts", "artifact.txt")
            )

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0
        assert "Removed: 5" in result.output
        assert "Failed: 0" in result.output

        result = runner.invoke(cli, args=["artifact", "rm", "-y"])
        assert result.exit_code == 0
        assert "Found 0 files inside" in result.output
        assert "Missing files: 0" in result.output
        assert "Failed: 0" in result.output

        for i in range(5):
            assert not os.path.exists(
                os.path.join(td, f"{i:0>5d}", "artifacts", "artifact.txt")
            )
