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

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import click

from .common import create_container


class QueryParsingError(Exception): ...


class NONE: ...


@dataclass
class Query:
    columns: List[str]
    filter_expr: Optional[str] = None
    sort_expr: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class Result:
    columns: List[str]
    data: List[Dict[str, Any]]
    time_s: int


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
            "end": {"end of query": "error"},
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


class Field:
    def __init__(self, obj: Union[Dict[str, Any], List[Any]]) -> None:
        if isinstance(obj, dict):
            self._obj = {}
            for k, v in obj.items():
                self._obj[k] = Field._field_or_instance(v)
        else:
            self._obj = obj

    @staticmethod
    def _field_or_instance(x):
        if isinstance(x, dict):
            return Field(x)
        elif isinstance(x, list):
            return [Field._field_or_instance(item) for item in x]
        else:
            return x

    def __getattribute__(self, name: Union[str, int]) -> Any:
        if name in super().__getattribute__("_obj"):
            value = self.get(name, default=NONE())
            if isinstance(value, NONE):
                raise KeyError(name)
            else:
                return value
        else:
            return super().__getattribute__(name)

    def get(self, key: str, default: Any = None, sep: str = "."):
        parts = key.split(sep)
        if len(parts) <= 1:
            return self._leaf_get(key, default)
        else:
            deeper = self._leaf_get(parts[0], NONE())
            if isinstance(deeper, NONE):
                return default
            else:
                return deeper.get(sep.join(parts[1:]), default)

    def _leaf_get(self, key, default):
        if isinstance(self._obj, list):
            return self._obj[key]
        else:
            return self._obj.get(key, default)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._obj})"

    def select(self, columns: List[str]) -> "Field":
        return Field({col: self.get(col) for col in columns})

    def to_dict(self):
        return self._obj


class Executor:
    def __init__(self, root: str, container_type: str):
        container = create_container(container_type, root)
        if container:
            self.container = container
            self.type = container_type
        else:
            raise ValueError("Can run queries only inside a container")

    def iterate_over_container(self, container, container_type: str):
        if container_type in ("line", "model_line", "data_line"):
            for i in range(len(container)):
                yield container.load_obj_meta(i)
        elif container_type == "repo":
            for name in container.get_line_names():
                line = container.add_line(name)
                for meta in self.iterate_over_container(line, "line"):
                    yield meta

    def execute(self, q: Query) -> Result:
        start_time = time.time()
        data = []

        for meta in self.iterate_over_container(self.container, self.type):
            ctx = Field(meta[0])  # TODO: somehow deal with meta lists
            ctx = ctx.select(q.columns)
            ctx_dict = ctx.to_dict()
            if q.filter_expr:
                result = eval(q.filter_expr, ctx_dict.copy())
                if not result:
                    continue

            data.append(ctx_dict)

        if q.sort_expr is not None:
            data = sorted(data, key=lambda item: eval(q.sort_expr, item.copy()))

        if q.offset is not None:
            data = data[q.offset :]

        if q.limit is not None:
            data = data[: q.limit]

        end_time = time.time()
        return Result(columns=q.columns, data=data, time_s=round(end_time - start_time, 4))


def render_results(result: Result) -> None:
    click.echo(result)


@click.command("query", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def query(ctx, args: List[str]):
    q = QueryParser().parse(list(args))
    click.echo(q)

    if not ctx.obj.get("meta"):
        return

    ex = Executor(ctx.obj["cwd"], ctx.obj["type"])
    results = ex.execute(q)
    render_results(results)
