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
from typing import List

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.cli.query import Executor, Query, QueryExecutionError, Result
from cascade.tests.cli.common import init_repo


@pytest.mark.parametrize(
    "params, query, result",
    [
        (
            [{"a": 1}],
            Query(columns=["params.a"]),
            Result(columns=["params.a"], rows=1, data=[{"params.a": 1}], time_s=0),
        ),
        (
            [{"a": 1}, {"b": 1}],
            Query(columns=["params.a"]),
            Result(
                columns=["params.a"], rows=2, data=[{"params.a": 1}, {"params.a": None}], time_s=0
            ),
        ),
        (
            [{"a": 1}, {"b": 1}],
            Query(columns=["params.a or 1"]),
            Result(
                columns=["params.a or 1"],
                rows=2,
                data=[{"params.a or 1": 1}, {"params.a or 1": 1}],
                time_s=0,
            ),
        ),
        (
            [{"a": 1}, {"b": 2}],
            Query(columns=["params.a or params.b"]),
            Result(
                columns=["params.a or params.b"],
                rows=2,
                data=[{"params.a or params.b": 1}, {"params.a or params.b": 2}],
                time_s=0,
            ),
        ),
        (
            [{"a": 1}, {"b": 2}],
            Query(columns=["[params.a, params.b]"]),
            Result(
                columns=["[params.a, params.b]"],
                rows=2,
                data=[{"[params.a, params.b]": [1, None]}, {"[params.a, params.b]": [None, 2]}],
                time_s=0,
            ),
        ),
        (
            [{"a": [0, 1, 2]}],
            Query(columns=["params.a[0]", "params.a[1]"]),
            Result(
                columns=["params.a[0]", "params.a[1]"],
                rows=1,
                data=[
                    {"params.a[0]": 0, "params.a[1]": 1},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": [0, 1, 2]}],
            Query(columns=["min(params.a)"]),
            Result(
                columns=["min(params.a)"],
                rows=1,
                data=[
                    {"min(params.a)": 0},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": 0, "b": 0}, {"a": 0, "b": 1}],
            Query(columns=["params.a"], filter_expr="params.b > 0"),
            Result(
                columns=["params.a"],
                rows=1,
                data=[
                    {"params.a": 0},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": 0, "b": 0}, {"a": 0, "b": 1}],
            Query(columns=["params.a"], filter_expr="params.b == 0"),
            Result(
                columns=["params.a"],
                rows=1,
                data=[
                    {"params.a": 0},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": "1", "b": 0}, {"a": "2", "b": 1}],
            Query(columns=["params.a"], sort_expr="params.b"),
            Result(
                columns=["params.a"],
                rows=2,
                data=[
                    {"params.a": "1"},
                    {"params.a": "2"},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": "1", "b": 0}, {"a": "2", "b": 1}],
            Query(columns=["params.a"], sort_expr="- params.b"),
            Result(
                columns=["params.a"],
                rows=2,
                data=[
                    {"params.a": "2"},
                    {"params.a": "1"},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": "1", "b": 0}, {"a": "2", "b": 1}],
            Query(columns=["params.a"], sort_expr="params.b", desc=True),
            Result(
                columns=["params.a"],
                rows=2,
                data=[
                    {"params.a": "2"},
                    {"params.a": "1"},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": "1", "b": 0}, {"a": "2", "b": 1}],
            Query(
                columns=["params.a"], filter_expr="params.a != '1'", sort_expr="params.b", desc=True
            ),
            Result(
                columns=["params.a"],
                rows=1,
                data=[
                    {"params.a": "2"},
                ],
                time_s=0,
            ),
        ),
        (
            [{"a": "1", "b": 0}, {"a": "2", "b": 1}, {"a": "3", "b": 2}],
            Query(
                columns=["params.a"],
                filter_expr="params.a != '1'",
                sort_expr="params.b",
                desc=True,
                limit=1,
            ),
            Result(
                columns=["params.a"],
                rows=1,
                data=[
                    {"params.a": "3"},
                ],
                time_s=0,
            ),
        ),
    ],
)
def test_params_queries(tmp_path_str, params, query, result):
    init_repo(tmp_path_str, params)

    executor = Executor(tmp_path_str, "repo")
    test_result = executor.execute(query)

    # ignore time when comparing to true result
    test_result.time_s = 0
    assert test_result == result


@pytest.mark.parametrize(
    "params, query",
    [
        ([{}, {}, {}], Query(columns=["open('file.txt')"])),
        ([{}, {}, {}], Query(columns=["import os"])),
        ([{}, {}, {}], Query(columns=["from subprocess import Popen"])),
        ([{}, {}, {}], Query(columns=["eval('print()')"])),
        ([{}, {}, {}], Query(columns=["exec('echo')"])),
        ([{}, {}, {}], Query(columns=["def f(): return 0"])),
    ],
)
def test_dangerous_builtins(tmp_path_str: str, params: List[dict], query: Query):
    init_repo(tmp_path_str, params)

    executor = Executor(tmp_path_str, "repo")
    with pytest.raises(QueryExecutionError):
        executor.execute(query)
