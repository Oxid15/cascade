from typing import List, Any
from cascade.base import MetaFromFile
from cascade.meta import MetaViewer
from cascade.models import ModelRepo


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
        objs = self._diff_reader.read_objects(self._path)

        # Conditional import
        try:
            import dash
        except ModuleNotFoundError:
            raise ModuleNotFoundError('''
            Cannot import dash. It is conditional
            dependency you can install it
            using the instructions from https://dash.plotly.com/installation''')
        else:
            from dash import Input, Output, html, State, dcc
            from dash_renderjson import DashRenderjson

        app = dash.Dash()

        app.layout = html.Div([
            html.H1(
                children=f'DiffViewer in {self._path}',
                style={
                    'textAlign': 'center',
                    'color': '#084c61',
                    'font-family': 'Montserrat'
                }
            ),
            dcc.Dropdown(id='left-dropdown', options=[meta[0]['name'] for meta in objs]),
            dcc.Dropdown(id='rigth-dropdown', options=[meta[0]['name'] for meta in objs]),

            DashRenderjson(id=f'diff-json', data={'Nothing': 'Nothing is selected!'}),

            html.Div(id='display', children=[
                html.Details(children=[
                    html.Summary(meta[0]['name']),
                    DashRenderjson(id=f'data_{i}', data=meta)
                ]) for i, meta in enumerate(objs)
            ])
        ])

        app.run_server(use_reloader=False, **kwargs)


dv = DiffViewer(r'C:\cascade_integration\repos\demo').serve()
