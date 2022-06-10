"""
Copyright 2022 Ilia Moiseev

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
from plotly import graph_objects as go
import pandas as pd
import dash
from dash import Input, Output, html, dcc

from . import MetaViewer


class MetricViewer:
    """
    Interface for viewing metrics in model meta files
    uses ModelRepo to extract metrics of all models if any
    constructs a `pd.DataFrame` of metrics internally, which is showed in `__repr__`
    """
    def __init__(self, repo) -> None:
        """
        Parameters
        ----------
        repo: ModelRepo
            ModelRepo object to extract metrics from
        """
        self.repo = repo

        self.metrics = []
        for name in self.repo.lines:
            line = self.repo[name]
            viewer_root = os.path.join(self.repo.root, name)

            for i, model_name in enumerate(line.model_names):
                view = MetaViewer(os.path.join(viewer_root, os.path.dirname(model_name)))
                metric = {'line': name, 'num': i}
                meta = view[0][-1]

                if 'metrics' in meta:
                    metric.update(meta['metrics'])
                if 'params' in meta:
                    metric.update(meta['params'])

                self.metrics.append(metric)
        self.table = pd.DataFrame(self.metrics)

    def __repr__(self) -> str:
        return repr(self.table)

    def plot_table(self, show=False) -> None:
        fig = go.Figure(data=[
            go.Table(
                header=dict(values=list(self.table.columns),
                            fill_color='#f4c9c7',
                            align='left'),
                cells=dict(values=[self.table[col] for col in self.table.columns],
                           fill_color='#bcced4',
                           align='left'))
        ])
        if show:
            fig.show()
        return fig

    def serve(self):
        df = self.table

        app = dash.Dash()
        dep_fig = go.Figure()

        app.layout = html.Div([
            html.H1(
                children=f'MetricViewer in {self.repo.root}',
                style={
                    'textAlign': 'center',
                    'color': '#084c61',
                    'font-family': 'Montserrat'
                }
            ),
            dcc.Dropdown(
                list(df.columns),
                id='dropdown-x',
                multi=False),
            dcc.Dropdown(
                list(df.columns),
                id='dropdown-y',
                multi=False),
            dcc.Graph(
                id='dependence-figure',
                figure=dep_fig),
            dcc.Graph(
                id='table',
                figure=self.plot_table(show=False)
            )
        ])

        @app.callback(
            Output(component_id='dependence-figure', component_property='figure'),
            Input(component_id='dropdown-x', component_property='value'),
            Input(component_id='dropdown-y', component_property='value')
        )
        def _update_graph(x, y):
            fig = go.Figure()
            if x is not None and y is not None:
                fig.add_trace(
                    go.Scatter(
                        x=df[x],
                        y=df[y],
                        mode='markers'
                    )
                )
                fig.update_layout(title=f'{x} to {y} relation')
            return fig

        app.run_server(use_reloader=False)
