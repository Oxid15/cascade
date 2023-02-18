import os
import glob
import json
from typing import List, Any, Literal, Dict
from deepdiff import DeepDiff

from ..base import MetaFromFile, JSONEncoder, MetaHandler
from ..meta import Server, MetaViewer


class DiffReader:
    def read_objects(self, path: str) -> List[MetaFromFile]:
        raise NotImplementedError()


class RepoDiffReader(DiffReader):
    def _check_path(self, path):
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

        meta = MetaHandler().read(metas[0])

        if not isinstance(meta, list):
            raise ValueError(f'Something is wrong with meta in {metas[0]} - it is not a list')

        if 'type' not in meta[0]:
            raise ValueError(f'Something is wrong with meta in {metas[0]} - no type key in it')

        if meta[0]['type'] not in ('repo', 'line'):
            raise ValueError('The folder you provided is neither the repo nor line')

    def read_objects(self, path: str) -> Dict[str, MetaFromFile]:
        self._check_path(path)

        mev = MetaViewer(path, filt={'type': 'model'})
        objs = [meta for meta in mev]
        objs = {meta[0]['name']: meta for meta in objs}
        return objs


class DatasetVersionDiffReader(DiffReader):
    def _check_path(self, path):
        pass

    def read_objects(self, path: str) -> Dict[str, MetaFromFile]:
        self._check_path(path)

        versions = MetaHandler().read(path)

        version_dict = {}
        for pipe_key in versions:
            for meta_key in versions[pipe_key]:
                version_dict.update({versions[pipe_key][meta_key]['version']: versions[pipe_key][meta_key]})
        return version_dict


class DiffViewer(Server):
    def __init__(self, path: str, type: Literal['repo', 'version']) -> None:
        self._path = path
        if type == 'repo':
            self._diff_reader = RepoDiffReader()
        elif type == 'version':
            self._diff_reader = DatasetVersionDiffReader()
        else:
            raise ValueError(f'{type} is not repo or version')

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

        self._objs = self._diff_reader.read_objects(self._path)

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
                theme=self._json_theme
            ),
            html.Div(id='display', children=[
                html.Details(children=[
                    html.Summary(name),
                    DashRenderjson(
                        id=f'data_{i}',
                        data={'': self._objs[name]},
                        theme=self._json_theme
                    )
                ]) for i, name in enumerate(self._objs)
            ])
        ], style={'margin': '5%', **self._style})

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

    def serve(self, **kwargs: Any) -> None:
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        app = dash.Dash()
        self._update_diff_callback(app)
        app.layout = self._layout
        app.run_server(use_reloader=False, **kwargs)
