from typing import List, Any
from ..models import ModelRepo


class DiffReader:
    def read(self, repo: ModelRepo) -> List[Any]:
        pass


class RepoDiffReader(DiffReader):
    pass


class DiffViewer:
    def __init__(self, repo) -> None:
        pass

    def serve(self, metric: str, **kwargs: Any) -> None:
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

        app = dash.Dash()

        app.layout = html.Div([
            html.H1(
                children=f'DiffViewer',
                style={
                    'textAlign': 'center',
                    'color': '#084c61',
                    'font-family': 'Montserrat'
                }
            ),
            # dcc.Graph(
            #     id='history-figure',
            #     figure=fig),
            dcc.Interval(
                id='history-interval',
                interval=1000 * 3)
        ])

        # @app.callback(Output('history-figure', 'figure'),
        #               Input('history-interval', 'n_intervals'))
        # def update_history(n_intervals):
        #     self._repo.reload()
        #     self._make_table()
        #     return self.plot(metric)

        app.run_server(use_reloader=False, **kwargs)
