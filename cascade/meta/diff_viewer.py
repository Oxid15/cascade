import json
from typing import List, Any
from deepdiff import DeepDiff

from ..base import MetaFromFile, JSONEncoder
from ..meta import Server, MetaViewer


class DiffReader:
    def read_objects(self, path: str) -> List[MetaFromFile]:
        raise NotImplementedError()


class RepoDiffReader(DiffReader):
    def read_objects(self, path: str) -> List[MetaFromFile]:
        # TODO: check for repo
        mev = MetaViewer(path, filt={'type': 'model'})
        return [meta for meta in mev]


class DiffViewer(Server):
    def __init__(self, path: str) -> None:
        self._path = path
        self._diff_reader = RepoDiffReader()
        self._objs = dict()

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

    def _read_objects(self):
        objs = self._diff_reader.read_objects(self._path)
        self._objs = {meta[0]['name']: meta for meta in objs}

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

        self._read_objects()

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
