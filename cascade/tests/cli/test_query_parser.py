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

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.cli.query import Query, QueryParser


@pytest.mark.parametrize(
    "tokens, query",
    [
        (
            ["a", "start"],
            Query(columns=["a", "start"]),
        ),
        (
            ["start", "b"],
            Query(columns=["start", "b"]),
        ),
        (
            [
                "start",
                "columns",
                "after_filter",
                "after_sort",
                "after_offset",
                "end",
            ],
            Query(
                columns=[
                    "start",
                    "columns",
                    "after_filter",
                    "after_sort",
                    "after_offset",
                    "end",
                ]
            ),
        ),
    ],
)
def test_parser(tokens, query):
    parsed_query = QueryParser().parse(tokens)
    assert parsed_query.columns == query.columns
    assert parsed_query.filter_expr == query.filter_expr
    assert parsed_query.sort_expr == query.sort_expr
    assert parsed_query.desc == query.desc
    assert parsed_query.limit == query.limit
    assert parsed_query.offset == query.offset
