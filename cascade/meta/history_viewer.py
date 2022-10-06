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
import warnings
from typing import List
import pendulum
import pandas as pd
from flatten_json import flatten
from deepdiff import DeepDiff
import plotly
from plotly import express as px
from plotly import graph_objects as go

from . import MetaViewer
from .. import __version__
from ..data import Dataset


class HistoryViewer:
    """
    The tool which allows user to visualize training history of model versions.
    Uses shows how metrics of models changed over time and how
    models with different hyperparameters depend on each other.
    """
    def __init__(
        self,
        repo,
        last_lines: int = None,
        last_models: int = None) -> None:
        """
        Parameters
        ----------
        repo: cascade.models.ModelRepo
            Repo to be viewed
        last_lines: int, optional
            Constraints the number of lines back from the last one to view
        last_models: int, optional
            For each line constraints the number of models back from the last one to view
        """
        self._repo = repo
        self._last_lines = last_lines
        self._last_models = last_models
        self._make_table()

    def _make_table(self):
        metas = []
        self._params = []
        for line in [*self._repo][::-1][:self._last_lines]:
            # Try to use viewer only on models using type key
            try:
                view = MetaViewer(line.root, filt={'type': 'model'})
            except KeyError:
                view = [MetaViewer(os.path.join(
                    line.root,
                    os.path.dirname(model_name)))[0]
                    for model_name in line.model_names]

                warnings.warn(f'''You use cascade {__version__} with the repo generated in version <= 0.4.1 without
                type key in some of the meta files (in repo, line or model).
                Consider updating your repo's meta by opening it with ModelRepo constructor in new version or manually.
                In the following versions it will be deprecated.''', FutureWarning)

            for i in range(len(line))[:self._last_models]:
                new_meta = {'line': line.root, 'num': i}
                try:
                    meta = view[i][0]
                except IndexError:
                    meta = {}

                new_meta.update(flatten(meta))
                metas.append(new_meta)

                params = {
                    'line': line.root,
                }
                if 'params' in meta:
                    if len(meta['params']) > 0:
                        params.update(flatten({'params': meta['params']}))
                self._params.append(params)

        self._table = pd.DataFrame(metas)
        if 'saved_at' in self._table:
            self._table = self._table.sort_values('saved_at')

    @staticmethod
    def _diff(p1, params) -> List:
        diff = [DeepDiff(p1, p2) for p2 in params]
        changed = [0 for _ in range(len(params))]
        for i in range(len(changed)):
            if 'values_changed' in diff[i]:
                changed[i] += len(diff[i]['values_changed'])
            if 'dictionary_item_added' in diff[i]:
                changed[i] += len(diff[i]['dictionary_item_added'])
            if 'dictionary_item_removed' in diff[i]:
                changed[i] += len(diff[i]['dictionary_item_removed'])
        return changed

    @staticmethod
    def _specific_argmin(arr, self_index) -> int:
        arg_min = 0
        for i in range(len(arr)):
            if arr[i] <= arr[arg_min] and i != self_index:
                arg_min = i
        return arg_min

    def plot(self, metric: str, show: bool = False) -> plotly.graph_objects.Figure:
        """
        Plots training history of model versions using plotly.

        Parameters
        ----------
        metric: str
            Metric should be present in meta of at least one model in repo
        show: bool, optional
            Whether to return and show or just return figure
        """

        # After flatten 'metrics_' will be added to the metric name
        if not metric.startswith('metrics_'):
            metric = 'metrics_' + metric
        assert metric in self._table, f'Metric {metric.replace("metrics_", "")} is not in the repo'

        # turn time into evenly spaced intervals
        time = [i for i in range(len(self._table))]
        lines = self._table['line'].unique()

        cmap = px.colors.qualitative.Plotly
        cmap_len = len(px.colors.qualitative.Plotly)
        line_cols = {line: cmap[i % cmap_len] for i, line in enumerate(lines)}

        self._table['time'] = time
        self._table['color'] = [line_cols[line] for line in self._table['line']]
        table = self._table.fillna('')

        # plot each model against metric
        # with all metadata on hover

        fig = px.scatter(
            table,
            x='time',
            y=metric,
            hover_data=[name for name in pd.DataFrame(self._params).columns],
            color='line'
        )

        # determine connections between models
        # plot each one with respected color

        for line in lines:
            params = [p for p in self._params if p['line'] == line]
            edges = []
            for i in range(len(params)):
                if i == 0:
                    edges.append(0)
                    continue
                else:
                    diff = self._diff(params[i], params[:i])
                    edges.append(self._specific_argmin(diff, i))

            xs = []
            ys = []
            t = table.loc[table['line'] == line]
            for i, e in enumerate(edges):
                xs += [t['time'].iloc[i], t['time'].iloc[e], None]
                ys += [t[metric].iloc[i], t[metric].iloc[e], None]

            fig.add_trace(go.Scatter(
                x=xs,
                y=ys,
                mode='lines',
                marker={'color': t['color'].iloc[0]},
                name=line,
                hoverinfo='none'
            ))

        # Create human-readable ticks
        now = pendulum.now(tz='UTC')
        time_text = table['saved_at']\
            .apply(lambda t: t if t == '' else pendulum.parse(t).diff_for_humans(now))

        fig.update_layout(
            hovermode='x',
            xaxis=dict(
                tickmode='array',
                tickvals=[i for i in range(len(time))],
                ticktext=time_text
            ))
        if show:
            fig.show()

        return fig

    def serve(self, metric: str, **kwargs):
        """
        Run dash-based server with HistoryViewer, updating plots in real-time.
        
        Note
        ----
        This feature needs `dash` to be installed.
        """
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
        fig = self.plot(metric)

        app.layout = html.Div([
            html.H1(
                children=f'HistoryViewer in {self._repo}',
                style={
                    'textAlign': 'center',
                    'color': '#084c61',
                    'font-family': 'Montserrat'
                }
            ),
            dcc.Graph(
                id='history-figure',
                figure=fig),
            dcc.Interval(
                id='history-interval',
                interval=1000 * 3)
        ])

        @app.callback(Output('history-figure', 'figure'),
                      Input('history-interval', 'n_intervals'))
        def update_history(n_intervals):
            self._repo.reload()
            self._make_table()
            return self.plot(metric)

        app.run_server(use_reloader=False, **kwargs)
