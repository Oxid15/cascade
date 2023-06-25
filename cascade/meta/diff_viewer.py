"""
Copyright 2022-2023 Ilia Moiseev

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
import glob
import json
from typing import Any, Dict, Literal, Union, Tuple

from deepdiff import DeepDiff
import pendulum

from ..base import MetaFromFile, JSONEncoder, MetaHandler, supported_meta_formats
from ..meta import Server, MetaViewer


class BaseDiffViewer(Server):
    def __init__(self, path) -> None:
        super().__init__()

        self._check_path(path)
        self._path = path

        self._style = {
            'color': '#084c61',
            'font-family': 'Open Sans, Montserrat'
        }

        self._json_theme = {
            'base00': '#fefefe',  # background
            'base03': '#cccccc',  # inactive key counter
            'base09': '#FF5F9E',  # numeric values
            'base0B': '#084c61',  # values text
            'base0D': '#C92C6D',  # keys text
        }

    def _check_path(self, path, meta_type):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

    def _read_objects(self, path):
        raise NotImplementedError()

    def _layout(self):
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import html, dcc

        try:
            import dash_renderjson
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                'Cannot import dash_renderjson. It is optional dependency for DiffViewer'
                ' and can be installed via `pip install dash_renderjson`')
        else:
            from dash_renderjson import DashRenderjson

        self._objs = self._read_objects(self._path)

        return html.Div([
            html.H1(
                children=f'DiffViewer in {self._path}',
                style={'textAlign': 'center', **self._style}
            ),
            dcc.Dropdown(id='left-dropdown', options=list(self._objs.keys())),
            dcc.Dropdown(id='rigth-dropdown', options=list(self._objs.keys())),
            DashRenderjson(
                id='diff-json',
                data={'Nothing': 'Nothing is selected!'},
                theme=self._json_theme,
                max_depth=self._default_diff_depth
            ),
            html.Div(id='display', children=[
                html.Details(children=[
                    html.Summary(name),
                    DashRenderjson(
                        id=f'data_{i}',
                        data={'': self._objs[name]},
                        theme=self._json_theme,
                        max_depth=self._default_depth
                    )
                ]) for i, name in enumerate(self._objs)
            ])
        ], style={'margin': '5%', **self._style})

    def serve(self, **kwargs: Any) -> None:
        '''
        Runs dash server

        Parameters
        ----------
        **kwargs
            Arguments for run_server for example port
        '''
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        app = dash.Dash()
        self._update_diff_callback(app)
        app.layout = self._layout
        app.run_server(use_reloader=False, **kwargs)

        mev = MetaViewer(path, filt={'type': 'model'})
        objs = [meta for meta in mev]
        objs = {f'Model {i:0>5d}': meta for i, meta in enumerate(objs)}
        return objs

    def _update_diff_callback(self, _app) -> None:
        try:
            from dash import Output, Input
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        @_app.callback(
            Output(component_id='diff-json', component_property='data'),
            Input(component_id='left-dropdown', component_property='value'),
            Input(component_id='rigth-dropdown', component_property='value'))
        def _update_diff(x, y):
            if x is not None and y is not None:
                diff = DeepDiff(self._objs[x], self._objs[y]).to_dict()
                diff = JSONEncoder().encode(diff)
                diff = json.loads(diff)
                return diff


class DatasetVersionDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._default_depth = 9
        self._default_diff_depth = 8

    def _read_objects(self, path: str) -> Dict[str, Any]:
        self._check_path(path, 'version_history')

        versions = MetaHandler.read(path)['versions']

        version_dict = {}
        for pipe_key in versions:
            for meta_key in versions[pipe_key]:
                version_dict.update({versions[pipe_key][meta_key]['version']: versions[pipe_key][meta_key]})
        return {key: version_dict[key] for key in sorted(version_dict.keys())}


class HistoryDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._default_depth = 2
        self._default_diff_depth = 1

    def _read_objects(self, path: str) -> Dict[str, Any]:
        self._check_path(path, ('history',))

        history = MetaHandler.read(path)['history']

        return {item['updated_at']: item for item in history}


class RepoDiffViewer(BaseDiffViewer):
    def __init__(
        self,
        path
    ) -> None:
        '''
        Parameters
        ----------
        path: str
            Path to the object which states to view
        '''
        super().__init__(path)

        self._default_depth = 2
        self._default_diff_depth = 2

    def _check_path(self, path: str, meta_type: Tuple) -> None:
        if not os.path.isdir(path):
            raise ValueError(f'Path `{path}` is not a directory')

        # Check that meta of repo or line exists
        # do not restrict extensions because meta handler would fail with
        # informative message anyway
        metas = glob.glob(os.path.join(path, 'meta.*'))
        if len(metas) == 0:
            raise ValueError(
                f'There is no meta file in the directory provided: {path}'
            )

        # No idea how to handle multiple metas
        # and what it means
        if len(metas) > 1:
            raise ValueError(
                f'Multiple meta files in the directory provided: {path}'
            )

        meta = MetaHandler.read(metas[0])
        if 'type' not in meta[0]:
            raise ValueError(
                f'Meta in file {metas[0]} has no `type` in its keys! '
                'It may be that you are using DiffViewer on old '
                'type of history logs before 0.10.0.'
            )

        if not isinstance(meta, list):
            raise ValueError(f'Something is wrong with meta in {metas[0]} - it is not a list')

        if 'type' not in meta[0]:
            raise ValueError(f'Something is wrong with meta in {metas[0]} - no type key in it')

        if meta[0]['type'] in meta_type:
            raise ValueError('The folder you provided is neither the repo nor line')

    def _read_objects(self, path: str) -> Dict[str, MetaFromFile]:
        self._check_path(path, ('repo', 'line'))

        mev = MetaViewer(path, filt={'type': 'model'})
        objs = [meta for meta in mev]
        objs = {meta[0]['name']: meta for meta in objs}
        return objs

    def _layout(self):
        def _table_row(name, prev_name):
            date = self._objs[name][0]['created_at']
            date = pendulum.parse(date).format('DD MMMM YYYY HH:mm:ss')

            obj = self._objs[name]
            prev_obj = self._objs[prev_name]
            
            diff = DeepDiff(prev_obj, obj).to_dict()

            diff_str = ''
            if 'dictionary_item_added' in diff:
                diff_str += f'+{len(diff["dictionary_item_added"])}'
            if 'values_changed' in diff:
                diff_str += f'~{len(diff["values_changed"])}'
            if 'dictionary_item_removed' in diff:
                diff_str += f'-{len(diff["dictionary_item_removed"])}'
            
            return html.Tr(children=[
                    html.Th(date),
                    html.Th(diff_str),
                    html.Th(
                        html.Details(children=[
                                html.Summary(name),
                                    DashRenderjson(
                                        id=f'{name}-data',
                                        data={'': obj},
                                        theme=self._json_theme,
                                        max_depth=self._default_depth
                                )
                            ]
                        )
                    )
                ],
                style={'text-align': 'left'}
            )

        def line_table(line):
            children = []
            keys = list(lines[line].keys())
            for name, prev_name in zip(keys, [keys[0], *keys[:-1]]):
                children.append(_table_row(name, prev_name))

            return html.Div(children=[
                html.H3(line, style={'color': '#C92C6D'}),
                html.Table(id=f'table-{line}', children=children)
            ],  style={'margin-bottom': '10px'})

        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import html, dcc

        try:
            import dash_renderjson
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                'Cannot import dash_renderjson. It is optional dependency for DiffViewer'
                ' and can be installed via `pip install dash_renderjson`')
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

        return html.Div([
            html.H1(
                children=f'DiffViewer in {self._path}',
                style={'textAlign': 'center', **self._style}
            ),
            dcc.Dropdown(id='left-dropdown', options=list(self._objs.keys())),
            dcc.Dropdown(id='rigth-dropdown', options=list(self._objs.keys())),
            DashRenderjson(
                id='diff-json',
                data={'Nothing': 'Nothing is selected!'},
                theme=self._json_theme,
                max_depth=self._default_diff_depth
            ),
            *[line_table(line) for line in lines],
        ], style={'margin': '5%', **self._style})


class WorkspaceDiffViewer(BaseDiffViewer):
    def __init__(
        self,
        path: str
    ) -> None:
        super().__init__(path)

        self._default_depth = 2
        self._default_diff_depth = 2

    # def 


class DiffViewer(Server):
    '''
    The dash-based server to view meta-data
    and compare different snapshots using deep diff.

    It can work with ModelRepo's, ModelLine's, files
    that store version logs and history of entities
    such as data registration logs.
    '''
    def __init__(self, path: str) -> None:
        super().__init__()

        self._diff_viewer = self._get_viewer(path)

    def _get_viewer(self, path: str):
        '''
        Determines the type of DiffReader and returns it
        '''
        if os.path.isdir(path):
            meta_path = sorted(glob.glob(os.path.join(path, 'meta.*')))
            if len(meta_path) != 1:
                raise RuntimeError(f'Found {len(meta_path)} files in {path}')
            meta = MetaHandler().read(meta_path[0])

            if meta[0]["type"] == "repo":
                return RepoDiffViewer(path)
            elif meta[0]["type"] == "workspace":
                return WorkspaceDiffViewer(path)
            else:
                raise ValueError(f"No viewer found for meta with type {meta[0]['type']}")
        else:
            _, ext = os.path.splitext(path)
            if ext not in supported_meta_formats:
                raise ValueError(
                    f'{path} file extension is not in supported'
                    f' meta formats: {supported_meta_formats}'
                )

            meta = MetaHandler().read(path)
            if 'type' not in meta:
                raise ValueError(
                    f'Meta in file {path} has no `type` in its keys!'
                    'It may be that you are using DiffViewer on old '
                    'type of history logs before 0.10.0.'
                )

            if meta['type'] == 'version_history':
                return DatasetVersionDiffViewer(path)

            if meta['type'] == 'history':
                return HistoryDiffViewer(path)

            raise ValueError(
                'No reader found for this type of file. '
                'Available types are: for Repo or Line, for DatasetVersion logs or for History log.'
            )

    def serve(self, *args, **kwargs):
        return self._diff_viewer.serve(*args, **kwargs)
