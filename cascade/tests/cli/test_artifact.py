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
from unittest.mock import patch

from click.testing import CliRunner

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.base import MetaHandler
from cascade.cli.cli import cli
from cascade.models import BasicModel


class TestModel(BasicModel):
    def save_artifact(self, path: str):
        with open(os.path.join(path, "artifact.txt"), "w") as f:
            f.write("Hello")


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

            mocked_remove.assert_called_once_with(os.path.join(td, "artifacts", "artifact.txt"))

            assert os.path.exists(os.path.join(td, "artifacts", "artifact.txt"))
