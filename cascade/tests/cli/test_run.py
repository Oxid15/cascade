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

from click.testing import CliRunner, Result

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.cli.cli import cli


def write_script(script: str, d: str):
    path = os.path.join(d, "script.py")
    with open(path, "w") as f:
        f.write(script)
    return path


def run_run(*args) -> Result:
    runner = CliRunner()
    result = runner.invoke(cli, args=["run", "-y", *args])
    return result


def test_missing_script():
    result = run_run("missing_script.py")
    assert result.exit_code == 1
    assert type(result.exception) == FileNotFoundError  # noqa: E721


def test_missing_config_key(tmp_path_str):
    script = "\n".join(
        [
            "from cascade.base import Config",
            "class ThisConfig(Config):",
            "    a: int = 0",
        ]
    )

    path = write_script(script, tmp_path_str)
    result = run_run(path, "--b", "1")

    assert result.exit_code == 1
    assert type(result.exception) == KeyError  # noqa: E721


def test_different_types(tmp_path_str):
    script = "\n".join(
        [
            "from cascade.base import Config",
            "class ThisConfig(Config):",
            "    a: int = 0",
            "    b: float = 1.2",
            "    c: str = 'hello'",
            "    d = [0, 1, 2]",
            "    e = {'key': 1}",
            "    f = {1, 2, 3}",
            "    g: str = 'hello again'",
            "    h = []",
            "    i = (9, 8, 7)",
            "print([type(item) for item in ThisConfig().to_dict().values()])",
        ]
    )

    path = write_script(script, tmp_path_str)
    result = run_run(path)

    assert result.exit_code == 0
    assert result.stdout.endswith(
        "[<class 'int'>, <class 'float'>, <class 'str'>, <class 'list'>,"
        " <class 'dict'>, <class 'set'>, <class 'str'>, <class 'list'>, <class 'tuple'>]\n"
    )


def test_different_types_override(tmp_path_str):
    script = "\n".join(
        [
            "from cascade.base import Config",
            "class ThisConfig(Config):",
            "    a: int = 0",
            "    b: float = 1.2",
            "    c: str = 'hello'",
            "    d = [0, 1, 2]",
            "    e = {'key': 1}",
            "    f = {1, 2, 3}",
            "    g: str = 'hello again'",
            "    h = []",
            "    i = (9, 8, 7)",
            "print([type(item) for item in ThisConfig().to_dict().values()])",
        ]
    )

    path = write_script(script, tmp_path_str)
    result = run_run(
        path,
        "--a",
        "1",
        "--b",
        "3.14",
        "--c",
        "'hii'",
        "--d",
        "[3, 4, 5]",
        "--e",
        "{'key': 2}",
        "--f",
        "{4, 5, 6}",
        "--g",
        "'qwerty'",
        "--i",
        "(5, 6, 7)",
    )

    assert result.exit_code == 0
    assert result.stdout.endswith(
        "[<class 'int'>, <class 'float'>, <class 'str'>, <class 'list'>,"
        " <class 'dict'>, <class 'set'>, <class 'str'>, <class 'list'>, <class 'tuple'>]\n"
    )
