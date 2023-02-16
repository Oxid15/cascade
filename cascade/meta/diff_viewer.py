import json
from typing import List, Any
from deepdiff import DeepDiff

from ..base import MetaFromFile, JSONEncoder
from ..meta import MetaViewer


class DiffReader:
    def read_objects(self, path) -> List[MetaFromFile]:
        return [{'a': 'b'}]


class RepoDiffReader(DiffReader):
    def __init__(self) -> None:
        super().__init__()

    def read_objects(self, path) -> List[MetaFromFile]:
        mev = MetaViewer(path, filt={'type': 'model'})
        return [meta for meta in mev]


class DiffViewer:
    def __init__(self, path: str) -> None:
        self._path = path
        self._diff_reader = RepoDiffReader()

    def serve(self, **kwargs: Any) -> None:
        style = {
            'color': '#084c61',
            'font-family': 'Open Sans, Montserrat'
        }

        theme = {
            'base00': '#fefefe',  # background
            'base03': '#cccccc',  # inactive key counter
            'base09': '#FF5F9E',  # numeric values
            'base0B': '#084c61',  # values text
            'base0D': '#C92C6D',  # keys text
        }

        objs = self._diff_reader.read_objects(self._path)
        self._objs = {meta[0]['name']: meta for meta in objs}

        # Conditional import
        try:
            import dash
        except ModuleNotFoundError:
            raise ModuleNotFoundError('''
            Cannot import dash. It is conditional
            dependency you can install it
            using the instructions from https://dash.plotly.com/installation''')
        else:
            from dash import Input, Output, html, dcc
            from dash_renderjson import DashRenderjson

        app = dash.Dash()

        app.layout = html.Div([
            html.H1(
                children=f'DiffViewer in {self._path}',
                style={'textAlign': 'center', **style}
            ),
            dcc.Dropdown(id='left-dropdown', options=list(self._objs.keys())),
            dcc.Dropdown(id='rigth-dropdown', options=list(self._objs.keys())),
            DashRenderjson(id='diff-json', data={'Nothing': 'Nothing is selected!'}, theme=theme),
            html.Div(id='display', children=[
                html.Details(children=[
                    html.Summary(name),
                    DashRenderjson(id=f'data_{i}', data={'': self._objs[name]}, theme=theme)
                ]) for i, name in enumerate(self._objs)
            ])
        ], style={'margin': '5%', **style})

        @app.callback(
            Output(component_id='diff-json', component_property='data'),
            Input(component_id='left-dropdown', component_property='value'),
            Input(component_id='rigth-dropdown', component_property='value'))
        def _update_diff(x, y):
            if x is not None and y is not None:
                diff = DeepDiff(self._objs[x], self._objs[y]).to_dict()
                diff = JSONEncoder().encode(diff)
                diff = json.loads(diff)
                return diff

        app.run_server(use_reloader=False, **kwargs)
