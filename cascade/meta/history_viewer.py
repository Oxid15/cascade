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
from plotly import express as px
from plotly import graph_objects as go

from . import MetaViewer
from .. import __version__


class HistoryViewer:
    """
    The tool which allows user to visualize training history of model versions.
    Uses plotly to show how metrics of models changed in time and how
    models with different hyperparameters depend on each other
    """
    def __init__(self, repo) -> None:
        self.repo = repo

        metas = []
        self.params = []
        for line in self.repo:
            # Try to use viewer only on models using type key
            try:
                view = MetaViewer(line.root, filt={'type': 'model'})
            except KeyError:
                view = [MetaViewer(os.path.join(
                    line.root,
                    os.path.dirname(model_name)))[0] 
                    for model_name in line.model_names]

                warnings.warn(f'''You use cascade {__version__} with the repo generated in version <= 0.4.1 without type key in some of the meta files (in repo, line or model).
                Consider updating your repo's meta by opening it with ModelRepo constructor in new version or manually.
                In the following versions it will be deprecated.''', FutureWarning)

            for i in range(len(line.model_names)):
                new_meta = {'line': line.root, 'num': i}
                new_meta.update(flatten(view[i][-1]))
                metas.append(new_meta)

                params = {
                    'line': line.root,
                }
                if 'params' in view[i][-1]:
                    if len(view[i][-1]['params']) > 0:
                        params.update(flatten({'params': view[i][-1]['params']}))
                self.params.append(params)

        self.table = pd.DataFrame(metas)
        if 'saved_at' in self.table:
            self.table = self.table.sort_values('saved_at')

    def _diff(self, p1, params) -> List:
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

    def _specific_argmin(self, arr, self_index) -> int:
        arg_min = 0
        for i in range(len(arr)):
            if arr[i] <= arr[arg_min] and i != self_index:
                arg_min = i
        return arg_min

    def plot(self, metric: str) -> None:
        """
        Plots training history of model versions using plotly.

        Parameters
        ----------
        metric: str
            Metric should be present in meta of at least one model in repo
        """

        # After flatten 'metrics_' will be added to the metric name
        if not metric.startswith('metrics_'):
            metric = 'metrics_' + metric
        assert metric in self.table

        # turn time into evenly spaced intervals
        time = [i for i in range(len(self.table))]
        lines = self.table['line'].unique()

        cmap = px.colors.qualitative.Plotly
        cmap_len = len(px.colors.qualitative.Plotly)
        line_cols = {line: cmap[i % cmap_len] for i, line in enumerate(lines)}

        self.table['time'] = time
        self.table['color'] = [line_cols[line] for line in self.table['line']]
        table = self.table.fillna('')

        # plot each model against metric
        # with all metadata on hover

        fig = px.scatter(
            table,
            x='time',
            y=metric,
            hover_data=[name for name in pd.DataFrame(self.params).columns],
            color='line'
        )

        # determine connections between models
        # plot each one with respected color

        for line in lines:
            params = [p for p in self.params if p['line'] == line]
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
        time_text = [pendulum.parse(table['saved_at'].iloc[i]) for i in range(len(time))]
        time_text = [t.diff_for_humans(now) for t in time_text]

        fig.update_layout(
            hovermode='x',
            xaxis=dict(
                tickmode='array',
                tickvals=[i for i in range(len(time))],
                ticktext=time_text
            ))
        fig.show()
