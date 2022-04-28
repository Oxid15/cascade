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
import numpy as np
from plotly import express as px
from plotly import graph_objects as go
from scipy.spatial.distance import hamming 


from . import MetaViewer


class HistoryViewer:
    def __init__(self, repo):
        self.repo = repo

        self.metas = []
        self.params = []
        for name in self.repo.lines:
            # TODO: validate fields used
            viewer_root = os.path.join(self.repo.root, name)
            view = MetaViewer(viewer_root)

            for i in range(len(view)):
                meta = {'line': name, 'num': i}
                self._add(view[i], meta)
                self.metas.append(meta)

                if 'params' in view[i]:
                    params = {
                        'line': name, 
                        'num': i, 
                        'time': np.datetime64(pendulum.parse(view[i]['saved_at'])).astype('long')}
                    params.update(view[i]['params'])
                    self.params.append(params)

        self.table = pd.DataFrame(self.metas)
        self.params = pd.DataFrame(self.params)

    def _add(self, elem, meta):
        for key in elem:
            if type(elem[key]) != dict:
                meta[key] = elem[key]
            else:
                self._add(elem[key], meta)

    def plot(self, metric):
        # TODO: check all used columns in data
        assert metric in self.table
        table = self.table.sort_values('saved_at')

        # turn time into evenly spaced intervals
        time = [i for i in range(len(table))]
        lines = table['line'].unique()
        line_cols = {line: px.colors.qualitative.G10[i] for i, line in enumerate(lines)}

        table['time'] = time
        table['color'] = [line_cols[line] for line in table['line']]

        # plot each model against metric
        # with all metadata on hover

        fig = px.scatter(
            table,
            x='time',
            y=metric,
            color='color',
            hover_data=[name for name in self.params.columns]
        )

        # determine connections between models
        # plot each one with respected color

        for line in lines:
            t = table.loc[table['line'] == line]
            t_np = self.params[self.params['line'] == line].to_numpy()[:, 2:]
            mask = ~np.isnan(t_np.astype(np.float32))
            edges = []
            for i, params in enumerate(t_np):
                if i == 0:
                    edges.append(0)
                    continue
                else:
                    d = np.array([hamming(params, t_np[k], w=mask[i] + mask[k]) for k in range(i)])
                    w = np.array([1 - k / len(d) for k in range(len(d))])
                    edges.append(np.argmin(d*w))

            xs = []
            ys = []
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
            xaxis = dict(tickmode = 'array',
                tickvals = [i for i in range(len(time))],
                ticktext = time_text
            ))
        fig.show()
