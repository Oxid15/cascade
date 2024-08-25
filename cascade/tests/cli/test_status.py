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
from cascade.cli.cli import cli
from cascade.repos import Repo


def test(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        repo = Repo(td)
        line = repo.add_line("line")

        result = runner.invoke(cli, args=["status"])

        assert result.exit_code == 0
        assert "repo of len 1" in result.output
