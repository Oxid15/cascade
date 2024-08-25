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

import pendulum
from deepdiff import DeepDiff

from ...models import Workspace
from .repo_diff_viewer import RepoDiffViewer


class WorkspaceDiffViewer(RepoDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)

        self._default_depth = 2
        self._default_diff_depth = 2

        self._callbacks.append(self._update_table_callback)

    def _line_table(self):
        try:
            import dash  # noqa: F401
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import html

        try:
            import dash_renderjson  # noqa: F401
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Cannot import dash_renderjson. It is optional dependency for DiffViewer"
                " and can be installed via `pip install dash_renderjson`"
            )
        else:
            from dash_renderjson import DashRenderjson

        def table_row(name, prev_name):
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

        line_divs = []
        for i, line in enumerate(lines):
            children = []
            keys = list(lines[line].keys())
            for name, prev_name in zip(keys, [keys[0], *keys[:-1]]):
                children.append(table_row(name, prev_name))

            line_divs += [
                html.Div(
                    id=f"line-{i}",
                    children=[
                        html.H3(line, style={"color": "#C92C6D"}),
                        html.Table(id=f"table-{line}", children=children),
                    ],
                    style={"margin-bottom": "10px"},
                )
            ]

        return line_divs

    def _layout(self):
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

        wp = Workspace(self._path)
        self._repo_names = wp.get_repo_names()
        self._repo = self._repo_names[0]

        self._objs = self._read_objects(
            os.path.join(os.path.abspath(self._path), self._repo)
        )

        return html.Div(
            [
                dcc.Dropdown(
                    id="repo-dropdown",
                    options=list(self._repo_names),
                    value=self._repo,
                ),
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
                html.Div(id="lines", children=self._line_table()),
            ],
            style={"margin": "5%", **self._style},
        )

    def _update_table_callback(self, _app) -> None:
        try:
            from dash import Input, Output
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        @_app.callback(
            Output(component_id="lines", component_property="children"),
            Input(component_id="repo-dropdown", component_property="value"),
        )
        def _update_table(repo):
            self._objs = self._read_objects(
                os.path.join(os.path.abspath(self._path), repo)
            )
            return self._line_table()
