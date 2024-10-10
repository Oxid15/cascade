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

from click.testing import CliRunner

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.base import MetaHandler
from cascade.cli.cli import cli
from cascade.models import BasicModel
from cascade.repos import Repo


def test(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        repo = Repo(td)
        line = repo.add_line(model_cls=BasicModel)
        model = line.create_model()
        line.save(model)

        meta = MetaHandler.read_dir(os.path.join(line.get_root(), "00000"))

        result = runner.invoke(cli, args=["cat", "-p", meta[0]["slug"]])
        assert result.exit_code == 0

        assert meta[0]["slug"] in result.output
