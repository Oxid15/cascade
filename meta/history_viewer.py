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
        for name in self.repo.lines:
            viewer_root = os.path.join(self.repo.root, name)
            view = MetaViewer(viewer_root)

            for i in range(len(view)):
                meta = {'line': name, 'num': i}
                self._add(view[i], meta)
                self.metas.append(meta)

        self.table = pd.DataFrame(self.metas)

    def _add(self, elem, meta):
        for key in elem:
            if type(elem[key]) != dict:
                meta[key] = elem[key]
            else:
                self._add(elem[key], meta)

    def plot(self, metric):
        assert metric in self.table
        table = self.table.sort_values('saved_at')

        time = [i for i in range(len(table))]
        lines = table['line'].unique()
        line_cols = {line: px.colors.qualitative.G10[i] for i, line in enumerate(lines)}

        table['time'] = time
        table['color'] = [line_cols[line] for line in table['line']]

        fig = go.Figure()
        for line in lines:
            t = table.loc[table['line'] == line]
            fig.add_trace(go.Scatter(
                x=t['time'],
                y=t[metric],
                mode='markers',
                marker={
                    'color': t['color']
                },
                name=line))
        
            t_np = table[table['line'] == line].to_numpy()
            edges = []
            for i, model in enumerate(t_np):
                if i == 0:
                    edges.append(0)
                    continue
                else:
                    edges.append(np.argmin([hamming(model, t_np[k]) for k in range(i)]))

            xs = []
            ys = []

            for i, e in enumerate(edges):
                xs += [t['time'].iloc[i], t['time'].iloc[e], None]
                ys += [t[metric].iloc[i], t[metric].iloc[e], None]

            fig.add_trace(go.Scatter(
                x=xs, 
                y=ys, 
                mode='lines', 
                marker={
                'color': t['color'].iloc[0]
                },
                name=line,
                hoverinfo='none'
                ))

        fig.update_layout(hovermode='x')
        fig.show()
