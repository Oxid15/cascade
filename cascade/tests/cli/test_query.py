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
from cascade.cli.query import Field, QueryParsingError, empty_field
from cascade.models import BasicModel
from cascade.repos import Repo


def init_repo(temp_dir):
    repo = Repo(temp_dir)
    line = repo.add_line()

    params_list = [
        {"a": {"b": 0}, "l": [0, 1, 2, 3], "ord": 0},
        {"l": [0, 1, 2, 3], "ord": 1},
        {"l": [], "ord": 2},
        {"a": {"b": None}, "ord": 3},
        {"ld": [{"e": "f"}], "ord": 4},
        {"ll": [[0, 1, 2, 3]], "ord": 5},
        {"ord": 6},
    ]

    for p in params_list:
        model = BasicModel()
        model.params.update(p)
        line.save(model)


def corrupt_model_meta(repo_root):
    with open(os.path.join(repo_root, "00000", "00000", "meta.json"), "w") as f:
        f.write("{i am broken json")


def test_parsing(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "params"])
        assert result.exit_code == 0

        result = runner.invoke(cli, args=["query", "params", "filter", "params is not None"])
        assert result.exit_code == 0

        result = runner.invoke(
            cli,
            args=[
                "query",
                "created_at",
                "filter",
                "created_at is not None",
                "sort",
                "created_at",
            ],
        )
        assert result.exit_code == 0

        result = runner.invoke(
            cli,
            args=[
                "query",
                "created_at",
                "filter",
                "created_at is not None",
                "sort",
                "created_at",
                "desc",
            ],
        )
        assert result.exit_code == 0

        result = runner.invoke(
            cli,
            args=[
                "query",
                "created_at",
                "filter",
                "created_at is not None",
                "sort",
                "created_at",
                "offset",
                "5",
            ],
        )
        assert result.exit_code == 0

        result = runner.invoke(
            cli,
            args=[
                "query",
                "created_at",
                "filter",
                "created_at is not None",
                "sort",
                "created_at",
                "desc",
                "offset",
                "5",
            ],
        )
        assert result.exit_code == 0

        result = runner.invoke(
            cli,
            args=[
                "query",
                "created_at",
                "filter",
                "created_at is not None",
                "sort",
                "created_at",
                "desc",
                "offset",
                "5",
                "limit",
                "1",
            ],
        )
        assert result.exit_code == 0


def test_parsing_error(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "filter"])
        assert result.exit_code == 1

        result = runner.invoke(cli, args=["query", "metrics", "sort", "metrics[0]", "filter"])
        assert result.exit_code == 1
        assert type(result.exception) is QueryParsingError


def test_columns(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "params"])
        assert result.stdout.split("\n")[3].strip() == str({"a": {"b": 0}, "l": [0, 1, 2, 3]})
        assert result.exit_code == 0

        result = runner.invoke(cli, args=["query", "params.a.b"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[3].strip() == "0"

        result = runner.invoke(cli, args=["query", "params.c.d.e"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[3].strip() == "None"


def test_lists(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "params.l[0]"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[3].strip() == "0"

        result = runner.invoke(cli, args=["query", "params.ll[0][0]"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[8].strip() == "0"


def test_list_of_dicts(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "params.ld[0].e"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[7].strip() == "f"


def test_columns_validation(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "[item for item in params.ld]"])
        assert result.exit_code == 1
        assert "Only alphanumeric" in result.exc_info[1].args[0]


def test_filter(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(
            cli, args=["query", "params.a.b", "filter", "params.a.b is not None"]
        )
        assert result.stdout.split("\n")[3].strip() == "0"
        assert result.exit_code == 0


def test_sort(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)

        result = runner.invoke(cli, args=["query", "params.ord", "sort", "params.ord"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[3].strip() == "0"

        result = runner.invoke(cli, args=["query", "params.ord", "sort", "params.ord", "desc"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[3].strip() == "6"

        result = runner.invoke(cli, args=["query", "params.a.b", "sort", "params.a.b"])
        assert result.exit_code == 0


def test_corrupted_model_meta(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        init_repo(td)
        corrupt_model_meta(td)

        result = runner.invoke(cli, args=["query", "params.a.b"])
        assert result.exit_code == 0
        assert result.stdout.split("\n")[3].strip() == "None"


def test_empty_field():
    assert empty_field("a") == Field({"a": None})
    assert empty_field("a.b") == Field({"a": {"b": None}})


def test_field():
    f = Field({"params": {"a": 0}, "col": 1, "b": None, "l": [1, 2, 3]})

    assert f.params.a == 0
    assert f.l[0] == 1
    assert f.no is None


def test_field_select():
    f = Field({"params": {"a": 0}, "col": 1, "b": None, "l": [1, 2, 3]})

    assert f.select(["params"]) == Field({"params": {"a": 0}})
    assert f.select(["params.a"]) == Field({"params": {"a": 0}})
    assert f.select(["col"]) == Field({"col": 1})
    assert f.select(["d"]) == Field({"d": None})
    assert f.select(["b.c"]) == Field({"b": {"c": None}})
    assert f.select(["d.e.f"]) == Field({"d": {"e": {"f": None}}})

    assert f.select(["l[1]", "l[2]"]) == Field({"l[1]": 2, "l[2]": 3})
    assert f.select(["l[0]"]) == Field({"l[0]": 1})
