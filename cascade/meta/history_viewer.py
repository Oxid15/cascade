"""
Copyright 2022-2023 Ilia Moiseev

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

from typing import List, Union, Dict, Any

import pendulum
import pandas as pd
from flatten_json import flatten
from deepdiff import DeepDiff

from ..models import ModelRepo
from . import Server, MetaViewer


class HistoryViewer(Server):
    """
    The tool which allows user to visualize training history of model versions.
    Uses shows how metrics of models changed over time and how
    models with different hyperparameters depend on each other.
    """

    def __init__(
        self,
        repo: ModelRepo,
        last_lines: Union[int, None] = None,
        last_models: Union[int, None] = None,
    ) -> None:
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

    def _make_table(self) -> None:
        metas = []
        params = []

        line_names = self._repo.get_line_names()
        if self._last_lines is not None:
            # Takes last N lines in correct order
            line_names = line_names[-self._last_lines :]

        for line_name in line_names:
            line = self._repo[line_name]
            view = MetaViewer(line.root, filt={"type": "model"})

            last_models = self._last_models if self._last_models is not None else 0
            for i in range(len(line))[-last_models:]:
                new_meta = {"line": line.root, "num": i}
                try:
                    # TODO: to take only first is not good...
                    meta = view[i][0]
                except IndexError:
                    meta = {}

                new_meta.update(flatten(meta))
                metas.append(new_meta)

                p = {
                    "line": line.root,
                }
                if "params" in meta:
                    if len(meta["params"]) > 0:
                        p.update(flatten({"params": meta["params"]}))
                params.append(p)

        self._table = pd.DataFrame(metas)
        self._params = params
        if "saved_at" in self._table:
            self._table = self._table.sort_values("saved_at")

    @staticmethod
    def _diff(p1: Dict[Any, Any], params: Dict[Any, Any]) -> List:
        diff = [DeepDiff(p1, p2) for p2 in params]
        changed = [0 for _ in range(len(params))]
        for i in range(len(changed)):
            if "values_changed" in diff[i]:
                changed[i] += len(diff[i]["values_changed"])
            if "dictionary_item_added" in diff[i]:
                changed[i] += len(diff[i]["dictionary_item_added"])
            if "dictionary_item_removed" in diff[i]:
                changed[i] += len(diff[i]["dictionary_item_removed"])
        return changed

    @staticmethod
    def _specific_argmin(arr, self_index) -> int:
        arg_min = 0
        for i in range(len(arr)):
            if arr[i] <= arr[arg_min] and i != self_index:
                arg_min = i
        return arg_min

    def _preprocess_metric(self, metric):
        if not isinstance(metric, str):
            raise ValueError(f"Metric {metric} is not a string")
        # After flatten 'metrics_' will be added to the metric name
        if not metric.startswith("metrics_"):
            metric = "metrics_" + metric
        assert (
            metric in self._table
        ), f'Metric {metric.replace("metrics_", "")} is not in the repo'

        return metric

    def plot(self, metric: str, show: bool = False) -> Any:
        """
        Plots training history of model versions using plotly.

        Parameters
        ----------
        metric: str
            Metric should be present in meta of at least one model in repo
        show: bool, optional
            Whether to return and show or just return figure
        """
        try:
            import plotly
        except ModuleNotFoundError:
            self._raise_cannot_import_plotly()
        else:
            from plotly import express as px
            from plotly import graph_objects as go

        metric = self._preprocess_metric(metric)

        # turn time into evenly spaced intervals
        time = [i for i in range(len(self._table))]
        lines = self._table["line"].unique()

        cmap = px.colors.qualitative.Plotly
        cmap_len = len(px.colors.qualitative.Plotly)
        line_cols = {line: cmap[i % cmap_len] for i, line in enumerate(lines)}

        self._table["time"] = time
        self._table["color"] = [line_cols[line] for line in self._table["line"]]
        table = self._table.fillna("")

        # plot each model against metric
        # with all metadata on hover

        fig = px.scatter(
            table,
            x="time",
            y=metric,
            hover_data=[name for name in pd.DataFrame(self._params).columns],
            color="line",
        )

        # determine connections between models
        # plot each one with respected color

        for line in lines:
            params = [p for p in self._params if p["line"] == line]
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
            t = table.loc[table["line"] == line]
            for i, e in enumerate(edges):
                xs += [t["time"].iloc[i], t["time"].iloc[e], None]
                ys += [t[metric].iloc[i], t[metric].iloc[e], None]

            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    marker={"color": t["color"].iloc[0]},
                    name=line,
                    hoverinfo="none",
                )
            )

        # Create human-readable ticks
        now = pendulum.now(tz="UTC")
        time_text = table["saved_at"].apply(
            lambda t: t if t == "" else pendulum.parse(t).diff_for_humans(now)
        )

        fig.update_layout(
            hovermode="x",
            xaxis=dict(
                tickmode="array",
                tickvals=[i for i in range(len(time))],
                ticktext=time_text,
            ),
        )
        if show:
            fig.show()

        return fig

    def serve(self, metric: Union[str, None] = None, **kwargs: Any) -> None:
        """
        Runs dash-based server with HistoryViewer, updating plots in real-time.

        Parameters
        ----------
        metric, optional:
            One of the metrics in the repo. May be left None and chosen later in
            the interface
        **kwargs
            Arguments for app.run_server() for example port or host
        Note
        ----
        This feature needs `dash` to be installed.
        """
        # Conditional import
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import Input, Output, html, dcc

        try:
            import plotly
        except ModuleNotFoundError:
            self._raise_cannot_import_plotly()
        else:
            from plotly import graph_objects as go

        app = dash.Dash()
        fig = self.plot(metric) if metric is not None else go.Figure()

        app.layout = html.Div(
            [
                html.H1(
                    id="viewer-title",
                    children=f"HistoryViewer in {self._repo}",
                    style={
                        "textAlign": "center",
                        "color": "#084c61",
                        "font-family": "Montserrat",
                    },
                ),
                dcc.Dropdown(
                    id="metric-dropwdown",
                    options=[
                        col.replace("metrics_", "")
                        for col in self._table.columns
                        if col.startswith("metrics_")
                    ],
                    value=metric,
                ),
                dcc.Graph(id="history-figure", figure=fig),
                dcc.Interval(id="history-interval", interval=1000 * 3),
            ]
        )

        @app.callback(
            Output("viewer-title", "children"), Input("history-interval", "n_intervals")
        )
        def update_title(n_intervals):
            return f"HistoryViewer in {self._repo}"

        @app.callback(
            Output("history-figure", "figure"),
            Input("history-interval", "n_intervals"),
            Input("metric-dropwdown", component_property="value"),
            prevent_initial_call=True,
        )
        def update_history(n_intervals, metric):
            self._repo.reload()
            self._make_table()
            return self.plot(metric)

        app.run_server(use_reloader=False, **kwargs)
