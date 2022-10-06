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
from typing import List
import warnings
import pendulum
from flatten_json import flatten
from plotly import graph_objects as go
import pandas as pd

from . import MetaViewer
from .. import __version__


class MetricViewer:
    """
    Interface for viewing metrics in model meta files
    uses ModelRepo to extract metrics of all models if any.
    As metrics it uses data from `metrics` field in models'
    meta and as parameters it uses `params` field.
    """
    def __init__(self, repo) -> None:
        """
        Parameters
        ----------
        repo: ModelRepo
            ModelRepo object to extract metrics from
        """
        self._repo = repo
        self._metrics = []
        self.reload_table()

    def reload_table(self) -> None:
        """
        Updates internal state
        """
        self._metrics = []
        for line in self._repo:
            viewer_root = line.root

            # Try to use viewer only on models using type key
            try:
                view = MetaViewer(viewer_root, filt={'type': 'model'})
            except KeyError:
                view = [
                    MetaViewer(os.path.join(viewer_root, os.path.dirname(model_name)))[0]
                    for model_name in line.model_names
                ]

                warnings.warn(f'''You use cascade {__version__} with the repo generated in version <= 0.4.1 without
                type key in some of the meta files (in repo, line or model).
                Consider updating your repo's meta by opening it with ModelRepo constructor in new version or manually.
                In the following versions it will be deprecated.''', FutureWarning)

            for i in range(len(line.model_names)):
                try:
                    meta = view[i][-1]  # Takes last model from meta
                except IndexError:
                    meta = {}

                metric = {
                    'line': viewer_root,
                    'num': i
                }

                if 'created_at' in meta:
                    metric['created_at'] = \
                        pendulum.parse(meta['created_at'])
                    if 'saved_at' in meta:
                        metric['saved'] = \
                            pendulum.parse(meta['saved_at']) \
                            .diff_for_humans(metric['created_at'])

                if 'metrics' in meta:
                    metric.update(meta['metrics'])
                if 'params' in meta:
                    metric.update(meta['params'])

                self._metrics.append(metric)
        self.table = pd.DataFrame(self._metrics)

    def __repr__(self) -> str:
        return repr(self.table)

    def plot_table(self, show: bool = False):
        """
        Uses plotly to graphically show table with metrics and parameters.
        """
        data = pd.DataFrame(map(flatten, self.table.to_dict('records')))
        fig = go.Figure(data=[
            go.Table(
                header=dict(values=list(data.columns),
                            fill_color='#f4c9c7',
                            align='left'),
                cells=dict(values=[data[col] for col in data.columns],
                           fill_color='#bcced4',
                           align='left')
            )
        ])
        if show:
            fig.show()
        return fig

    def serve(
        self,
        page_size: int = 50,
        include: List[str] = None,
        exclude: List[str] = None,
        **kwargs) -> None:
        """
        Runs dash-based server with interactive table of metrics and parameters.

        Parameters
        ----------
        page_size: int, optional
            Size of the table in rows on one page
        include: List[str], optional:
            List of parameters or metrics to be added. Only them will be present along with some default.
        exclude: List[str], optional:
            List of parameters or metrics to be excluded from table.
        **kwargs:
            Arguments of dash app. Can be ip or port for example.
        """
        server = MetricServer(self, page_size=page_size, include=include, exclude=exclude)
        server.serve(**kwargs)


class MetricServer:
    def __init__(self, mv, page_size, include, exclude, **kwargs) -> None:
        self._mv = mv
        self._page_size = page_size
        self._include = include
        self._exclude = exclude

    def _update_graph_callback(self, _app):
        try:
            from dash import Output, Input
        except ModuleNotFoundError:
            self._raise_cannot_import()

        @_app.callback(
            Output(component_id='dependence-figure', component_property='figure'),
            Input(component_id='dropdown-x', component_property='value'),
            Input(component_id='dropdown-y', component_property='value'))
        def _update_graph(x, y):
            fig = go.Figure()
            if x is not None and y is not None:
                fig.add_trace(
                    go.Scatter(
                        x=self._df_flatten[x],
                        y=self._df_flatten[y],
                        mode='markers'
                    )
                )
                fig.update_layout(title=f'{x} to {y} relation')
            return fig

    def _layout(self):
        try:
            from dash import html, dcc, dash_table
        except ModuleNotFoundError:
            self._raise_cannot_import()

        self._mv._repo.reload()
        self._mv.reload_table()

        df = self._mv.table
        if self._exclude is not None:
            df = df.drop(self._exclude, axis=1)

        if self._include is not None:
            df = df[['line', 'num'] + self._include]

        self._df_flatten = pd.DataFrame(map(flatten, df.to_dict('records')))
        dep_fig = go.Figure()

        return html.Div([
            html.H1(
                children=f'MetricViewer in {self._mv._repo}',
                style={
                    'textAlign': 'center',
                    'color': '#084c61',
                    'font-family': 'Montserrat'
                }
            ),
            dcc.Dropdown(
                list(self._df_flatten.columns),
                id='dropdown-x',
                multi=False),
            dcc.Dropdown(
                list(self._df_flatten.columns),
                id='dropdown-y',
                multi=False),
            dcc.Graph(
                id='dependence-figure',
                figure=dep_fig),
            dash_table.DataTable(
                columns=[
                    {'name': col, 'id': col, 'selectable': True} for col in self._df_flatten.columns
                ],
                data=self._df_flatten.to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=self._page_size,
            )
        ])

    def serve(self, **kwargs):
        # Conditional import
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import()

        app = dash.Dash()
        app.layout = self._layout
        self._update_graph_callback(app)
        app.run_server(use_reloader=False, **kwargs)

    def _raise_cannot_import(self):
        raise ModuleNotFoundError('''
                    Cannot import dash. It is conditional
                    dependency you can install it
                    using the instructions from https://dash.plotly.com/installation''')
