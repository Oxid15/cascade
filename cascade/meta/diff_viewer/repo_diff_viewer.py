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
from typing import Dict, Tuple

import pendulum
from deepdiff import DeepDiff

from ...base import Meta, MetaHandler
from ..meta_viewer import MetaViewer
from .base_diff_viewer import BaseDiffViewer


class RepoDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        """
        Parameters
        ----------
        path: str
            Path to the object which states to view
        """
        super().__init__(path)

        self._default_depth = 2
        self._default_diff_depth = 2

    def _check_path(self, path: str, meta_type: Tuple) -> None:
        if not os.path.isdir(path):
            raise ValueError(f"Path `{path}` is not a directory")

        # Check that meta of repo or line exists
        # do not restrict extensions because meta handler would fail with
        # informative message anyway

        meta = MetaHandler.read_dir(path)
        if "type" not in meta[0]:
            raise ValueError(
                f"Meta in {path} has no `type` in its keys! "
                "It may be that you are using DiffViewer on old "
                "type of history logs before 0.10.0."
            )

        if not isinstance(meta, list):
            raise ValueError(
                f"Something is wrong with meta in {path} - it is not a list"
            )

        if "type" not in meta[0]:
            raise ValueError(
                f"Something is wrong with meta in {path} - no type key in it"
            )

        if meta[0]["type"] not in meta_type:
            raise ValueError("The folder you provided is neither the repo nor line")

    def _read_objects(self, path: str) -> Dict[str, Meta]:
        self._check_path(path, ("repo", "line"))

        mev = MetaViewer(path, filt={"type": "model"})
        objs = [meta for meta in mev]
        objs = {meta[0]["path"]: meta for meta in objs}
        return objs

    def _layout(self):
        def _table_row(name, prev_name):
            date = self._objs[name][0]["created_at"]
            date = pendulum.parse(date).format("DD MMMM YYYY HH:mm:ss")

            obj = self._objs[name]
            prev_obj = self._objs[prev_name]

            diff = DeepDiff(prev_obj, obj).to_dict()

            diff_str = ""
            if "dictionary_item_added" in diff:
                diff_str += f'+{len(diff["dictionary_item_added"])}'
            if "values_changed" in diff:
                diff_str += f'~{len(diff["values_changed"])}'
            if "dictionary_item_removed" in diff:
                diff_str += f'-{len(diff["dictionary_item_removed"])}'

            return html.Tr(
                children=[
                    html.Th(date),
                    html.Th(diff_str),
                    html.Th(
                        html.Details(
                            children=[
                                html.Summary(name),
                                DashRenderjson(
                                    id=f"{name}-data",
                                    data={"": obj},
                                    theme=self._json_theme,
                                    max_depth=self._default_depth,
                                ),
                            ]
                        )
                    ),
                ],
                style={"text-align": "left"},
            )

        def line_table(line):
            children = []
            keys = list(lines[line].keys())
            for name, prev_name in zip(keys, [keys[0], *keys[:-1]]):
                children.append(_table_row(name, prev_name))

            return html.Div(
                children=[
                    html.H3(line, style={"color": "#C92C6D"}),
                    html.Table(id=f"table-{line}", children=children),
                ],
                style={"margin-bottom": "10px"},
            )

        try:
            import dash  # noqa: F401
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import dcc, html

        try:
            import dash_renderjson  # noqa: F401
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Cannot import dash_renderjson. It is optional dependency for DiffViewer"
                " and can be installed via `pip install dash_renderjson`"
            )
        else:
            from dash_renderjson import DashRenderjson

        self._objs = self._read_objects(self._path)

        lines = dict()
        for name in self._objs:
            # /full/path/repo/line/model/file.ext
            tail, _ = os.path.split(name)
            tail, _ = os.path.split(tail)
            _, line = os.path.split(tail)

            if line in lines:
                lines[line][name] = self._objs[name]
            else:
                lines[line] = {name: self._objs[name]}

        return html.Div(
            [
                html.H1(
                    children=f"DiffViewer in {self._path}",
                    style={"textAlign": "center", **self._style},
                ),
                dcc.Dropdown(id="left-dropdown", options=list(self._objs.keys())),
                dcc.Dropdown(id="rigth-dropdown", options=list(self._objs.keys())),
                DashRenderjson(
                    id="diff-json",
                    data={"Nothing": "Nothing is selected!"},
                    theme=self._json_theme,
                    max_depth=self._default_diff_depth,
                ),
                *[line_table(line) for line in lines],
            ],
            style={"margin": "5%", **self._style},
        )
