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

import ast
import time
from dataclasses import dataclass
from types import CodeType
from typing import Any, Dict, List, Optional, Union

import click
import pendulum

from ..base import MetaIOError
from ..base.utils import get_terminal_width
from .common import create_container

NODE_ALLOW_LIST = [
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.IfExp,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.Eq,
    ast.NotEq,
    ast.Store,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
    ast.UAdd,
    ast.USub,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Dict,
    ast.Subscript,
    ast.Slice,
    ast.Attribute,
    ast.Call,
    ast.ListComp,
    ast.DictComp,
    ast.SetComp,
    ast.comprehension,
    ast.GeneratorExp,
]

ALLOWED_BUILTINS = {
    "any": any,
    "all": all,
    "len": len,
    "sum": sum,
    "min": min,
    "max": max,
    "sorted": sorted,
    "abs": abs,
    "round": round,
    "pow": pow,
    "divmod": divmod,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "repr": repr,
    "list": list,
    "tuple": tuple,
    "set": set,
    "dict": dict,
    "frozenset": frozenset,
    "enumerate": enumerate,
    "zip": zip,
    "range": range,
    "reversed": reversed,
    "map": map,
    "filter": filter,
    "None": None,
    "True": True,
    "False": False,
}


class QueryParsingError(Exception): ...


class QueryExecutionError(Exception): ...


class NONE: ...


@dataclass
class Query:
    columns: List[str]
    filter_expr: Optional[str] = None
    sort_expr: Optional[str] = None
    desc: bool = False
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class Result:
    columns: List[str]
    rows: int
    data: List[Dict[str, Any]]
    time_s: float


class QueryParser:
    def __init__(self):
        # This dictionary defines how queries are parsed
        # Each key is the current state we're in
        # then inside the internal dicts there are expected cases

        # For example, when we are in the beginning, the state is "start"
        # then we expect next thing to be the name of a column
        # we switch to "columns" if we see anything
        # then we expect another column or filter for example
        # etc
        self._states = {
            "start": {
                "expression": "columns",
            },
            "columns": {
                "expression": "columns",
                "filter": "filter",
                "sort": "sort",
                "limit": "limit",
                "offset": "offset",
            },
            "filter": {"expression": "after_filter"},
            "after_filter": {"sort": "sort", "limit": "limit", "offset": "offset"},
            "sort": {"expression": "after_sort"},
            "after_sort": {
                "expression": "after_sort",
                "limit": "limit",
                "offset": "offset",
            },
            "offset": {"expression": "after_offset"},
            "after_offset": {"limit": "limit"},
            "limit": {"expression": "end"},
            "end": {"end of query": "error"},
        }

        self.expected = {"_", ".", "[", "]"}

    def _report_error(
        self,
        i: int,
        token: str,
        tokens: List[str],
        postfix: Optional[str] = None,
    ):
        tokens.insert(i + 1, "<-")
        expression = " ".join(tokens)
        expression = (
            f"Unexpected token `{token}` at marked (<-) position: " + f"`{expression}`"
        )
        expression = " ".join((expression, postfix))
        raise QueryParsingError(expression)

    def parse(self, tokens: List[str]) -> Query:
        state = "start"
        columns = []
        filter_expr = None
        sort_expr = None
        desc = False
        limit = None
        offset = None

        if len(tokens) == 0:
            raise QueryParsingError(
                "Parser received empty query."
                " Provide at least one column name or"
                " a list of columns separated by spaces"
                " after `cascade query` command."
                " Example: cascade query created_at"
            )

        for i, token in enumerate(tokens):
            if token in self._states:
                new_state = self._states[state].get(token, "error")

                if new_state == "error":
                    self._report_error(
                        i,
                        token,
                        tokens,
                        postfix=f"Expected tokens are any of ({', '.join(self._states[state])})",
                    )

                state = new_state
                continue

            if state == "start" or state == "columns":
                # self._validate_column(token)
                columns.append(token)
            elif state == "filter":
                filter_expr = token
            elif state == "sort":
                sort_expr = token
            elif state == "limit":
                limit = int(token)
            elif state == "offset":
                offset = int(token)
            elif state == "after_sort" and token == "desc":
                desc = True
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

        q = Query(
            columns,
            filter_expr=filter_expr,
            sort_expr=sort_expr,
            desc=desc,
            limit=limit,
            offset=offset,
        )
        return q


def empty_field(col: str):
    res = {}
    parts = col.split(".")
    if len(parts) == 1:
        res[parts[0]] = None
    else:
        res[parts[0]] = empty_field(".".join(parts[1:]))
    return Field(res)


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

    def __len__(self):
        return len(self._obj)

    def __eq__(self, obj):
        if isinstance(obj, Field):
            return self._obj == obj._obj
        else:
            return super().__eq__(obj)

    def __getattribute__(self, name: Union[str, int]) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return super().__getattribute__("get")(name, None)

    def __repr__(self):
        return self._obj.__repr__()

    def __getitem__(self, index: int):
        if isinstance(self._obj, dict):
            raise ValueError(
                f"Indexing with [{index}] was used for a dict field in query"
                ", if you want to access a field, use field.param1"
            )
        if not isinstance(index, int):
            raise TypeError(f"Tried to index a list with index {index}")

        if self._obj is None or index >= len(self._obj):
            return None

        return self._obj.__getitem__(index)

    def get(self, key: str, default: Any = None, sep: str = "."):
        parts = key.split(sep)
        if len(parts) <= 1:
            return self._leaf_get(key, default)
        else:
            deeper = self._leaf_get(parts[0], NONE)
            if isinstance(deeper, NONE):
                return default
            else:
                return deeper.get(sep.join(parts[1:]), default)

    def _leaf_get(self, key, default):
        if isinstance(self._obj, list):
            return self._obj[key]
        else:
            return self._obj.get(key, default)

    def to_dict(self):
        return self._obj

    def values(self):
        if isinstance(self._obj, dict):
            return self._obj.values()
        else:
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
                try:
                    yield container.load_obj_meta(i)
                except MetaIOError:
                    yield [{}]
        elif container_type == "repo":
            for name in container.get_line_names():
                line = container.add_line(name, line_type=None)
                for meta in self.iterate_over_container(line, "line"):
                    yield meta
        elif container_type == "workspace":
            for repo_name in container.get_repo_names():
                repo = container.add_repo(repo_name)
                for meta in self.iterate_over_container(repo, "repo"):
                    yield meta

    def validate_and_compile(self, expr: str) -> CodeType:
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise QueryExecutionError(
                f"Failed to parse query expression: {expr}"
            ) from e

        for node in ast.walk(tree):
            if type(node) not in NODE_ALLOW_LIST:
                raise QueryExecutionError(
                    f"{type(node).__name__} not allowed in a query"
                )

            if isinstance(node, ast.Attribute) and (
                node.attr.startswith("__") or node.attr in ("format", "format_map")
            ):
                raise QueryExecutionError(f"attribute .{node.attr} not allowed")

            if isinstance(node, ast.Name) and node.id.startswith("__"):
                raise QueryExecutionError(f"name {node.id} not allowed")

        return compile(tree, "query", "eval")

    def eval_or_none(self, expr, context: Dict[str, Any]) -> Optional[Any]:
        try:
            return eval(expr, {"__builtins__": ALLOWED_BUILTINS}, context.copy())
        except Exception:
            return None

    def select(self, ctx: Dict[str, Union[Field, Any]], columns: Dict[str, CodeType]):
        res = {}
        for col in columns:
            res[col] = self.eval_or_none(columns[col], ctx)
        return res

    def execute(self, q: Query) -> Result:
        start_time = time.time()
        data = []
        sorting_keys = []

        # Small optimization
        # Validate once, then execute many times

        col2expr = {}
        for col in q.columns:
            col2expr[col] = self.validate_and_compile(col)

        if q.filter_expr:
            filter_expr = self.validate_and_compile(q.filter_expr)
        else:
            filter_expr = None

        if q.sort_expr:
            sort_expr = self.validate_and_compile(q.sort_expr)
        else:
            sort_expr = None

        # TODO: meta data is independent, can be highly parallel
        for meta in self.iterate_over_container(self.container, self.type):
            full_ctx = Field(meta[0]).to_dict()  # TODO: somehow deal with meta lists
            ctx = self.select(full_ctx, col2expr)

            if filter_expr:
                result = self.eval_or_none(filter_expr, full_ctx)
                if not result:
                    continue

            if sort_expr:
                sorting_key = self.eval_or_none(sort_expr, full_ctx)
                sorting_keys.append(sorting_key)

            data.append(ctx)

        if q.sort_expr is not None:
            # This one sorts the data by the order of sorting_keys
            # we push values containing None to the end

            present = [i for i in range(len(data)) if sorting_keys[i] is not None]
            missing = [i for i in range(len(data)) if sorting_keys[i] is None]
            present.sort(key=lambda i: sorting_keys[i], reverse=q.desc)
            data = [data[i] for i in present + missing]

        if q.offset is not None:
            data = data[q.offset :]

        if q.limit is not None:
            data = data[: q.limit]

        end_time = time.time()
        return Result(
            columns=q.columns,
            rows=len(data),
            data=data,
            time_s=round(end_time - start_time, 4),
        )


def calculate_column_width(n: int) -> List[int]:
    w = get_terminal_width()
    return [w // n for _ in range(n)]


def render_field(value: Union[Field, Any], width: int) -> str:
    s = str(value)
    return s[:width]


def render_header(columns, widths):
    result = []
    for w, col in zip(widths, columns):
        result.append(col + (w - len(col)) * " ")
    return "".join(result)


def render_row(columns: List[str], field: Field, widths: List[int]) -> str:
    result = []
    for col, w in zip(columns, widths):
        rendered_val = render_field(field.get(col), w)
        result.append(rendered_val + (w - len(rendered_val)) * " ")
    return "".join(result)


def render_results(result: Result) -> None:
    widths = calculate_column_width(len(result.columns))

    click.echo("─" * sum(widths))
    click.echo(render_header(result.columns, widths))
    click.echo("─" * sum(widths))
    for field in result.data:
        click.echo(render_row(result.columns, field, widths))
    click.echo("─" * sum(widths))
    click.echo(f"Finished: {pendulum.now()}")
    click.echo(f"Returned rows: {result.rows}")
    click.echo(f"Time: {result.time_s}s")


@click.command("query", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def query(ctx, args: List[str]):
    """
    Get and filter experiment results
    """
    q = QueryParser().parse(list(args))

    if not ctx.obj.get("meta"):
        return

    ex = Executor(ctx.obj["cwd"], ctx.obj["type"])
    results = ex.execute(q)
    render_results(results)
