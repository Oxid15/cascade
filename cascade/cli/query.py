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

from dataclasses import dataclass
from typing import List, Optional

import click


class QueryParsingError(Exception): ...


@dataclass
class Query:
    columns: List[str]
    filter_expr: Optional[str] = None
    sort_expr: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class QueryParser:
    def __init__(self):
        self._states = {
            "start": {
                "expression": "start",
                "filter": "filter",
                "sort": "sort",
                "limit": "limit",
                "offset": "offset",
            },
            "filter": {"expression": "after_filter"},
            "after_filter": {"sort": "sort", "limit": "limit", "offset": "offset"},
            "sort": {"expression": "after_sort"},
            "after_sort": {"limit": "limit", "offset": "offset"},
            "limit": {"expression": "after_limit"},
            "after_limit": {"offset": "offset"},
            "offset": {"expression": "end"},
            "end": {"expression": "error"},
        }

    def _report_error(self, i, token, tokens, state: Optional[str] = None):
        tokens.insert(i + 1, "<-")
        expression = " ".join(tokens)
        expression = f"Unexpected token `{token}` at marked (<-) position: " + f"`{expression}`"
        if state:
            expression += f" Expected tokens are any of ({', '.join(self._states[state])})"
        raise QueryParsingError(expression)

    def parse(self, tokens: List[str]) -> Query:
        state = "start"
        columns = []
        filter_expr = None
        sort_expr = None
        limit = None
        offset = None

        for i, token in enumerate(tokens):
            if token in self._states:
                new_state = self._states[state].get(token, "error")

                if new_state == "error":
                    self._report_error(i, token, tokens, state)

                state = new_state
                continue

            if state == "start":
                columns.append(token)
            elif state == "filter":
                filter_expr = token
            elif state == "sort":
                sort_expr = token
            elif state == "limit":
                limit = int(token)
            elif state == "offset":
                offset = int(token)
            elif state == "error":
                self._report_error(i, token, tokens)
            else:
                expected = tuple(self._states[state].keys())
                raise QueryParsingError(
                    f"Expected {'one of ' if len(expected) > 1 else ''}"
                    f"{expected if len(expected) > 1 else expected[0]}"
                    f", got `{token}`"
                )

            state = self._states[state].get("expression", "error")

        q = Query(columns, filter_expr=filter_expr, sort_expr=sort_expr, limit=limit, offset=offset)
        return q


@click.command("query", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def query(args: List[str]):
    q = QueryParser().parse(list(args))
    click.echo(q)
