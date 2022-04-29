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

import pendulum
import pandas as pd
from deepdiff import DeepDiff
from plotly import express as px
from plotly import graph_objects as go

from . import MetaViewer


class HistoryViewer:
    def __init__(self, repo):
        self.repo = repo

        metas = []
        self.params = []
        for name in self.repo.lines:
            # TODO: validate fields used
            viewer_root = os.path.join(self.repo.root, name)
            view = MetaViewer(viewer_root)

            for i in range(len(view)):
                meta = {'line': name, 'num': i}
                # recursively unfold every nested dict to form plain table
                self._add(view[i], meta)
                metas.append(meta)

                params = {
                    'line': name,
                }
                params.update(view[i]['params'])
                self.params.append(params)

        self.table = pd.DataFrame(metas)
        self.table = self.table.sort_values('saved_at')

    def _add(self, elem, meta):
        for key in elem:
            if type(elem[key]) != dict:
                meta[key] = elem[key]
            else:
                self._add(elem[key], meta)

    def _diff(self, p1, params):
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

    def _specific_argmin(self, arr, self_index):
        arg_min = 0
        for i in range(len(arr)):
            if arr[i] <= arr[arg_min] and i != self_index:
                arg_min = i
        return arg_min

    def plot(self, metric):
        # TODO: check all used columns in data
        assert metric in self.table

        # turn time into evenly spaced intervals
        time = [i for i in range(len(table))]
        lines = table['line'].unique()
        line_cols = {line: px.colors.qualitative.Plotly[i] for i, line in enumerate(lines)}

        table['time'] = time
        table['color'] = [line_cols[line] for line in table['line']]
        table = table.fillna('')

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
            for i, e in enumerate(edges):
                t = table.loc[table['line'] == line]
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
            xaxis = dict(tickmode = 'array',
                tickvals = [i for i in range(len(time))],
                ticktext = time_text
            ))
        fig.show()
