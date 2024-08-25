"""
Copyright 2022-2024 Ilia Moiseev

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
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from deepdiff import DeepDiff
from flatten_json import flatten

from ..base import MetaHandler, ZeroMetaError
from ..lines import ModelLine
from ..models import Workspace
from ..repos import Repo, SingleLineRepo
from .meta_viewer import MetaViewer
from .server import Server


class HistoryViewer(Server):
    """
    The tool which allows user to visualize training history of model versions.
    Uses shows how metrics of models changed over time and how
    models with different hyperparameters depend on each other.
    """

    def __init__(
        self,
        container: Union[Workspace, Repo, ModelLine],
        last_lines: Optional[int] = None,
        last_models: Optional[int] = None,
        update_period_sec: int = 3,
    ) -> None:
        """
        Parameters
        ----------
        container: Union[Workspace, Repo, ModelLine]
            Container of models to be viewed
        last_lines: int, optional
            Constraints the number of lines back from the last one to view
        last_models: int, optional
            For each line constraints the number of models back from the last one to view
        update_period_sec: int, default is 3
            Update period in seconds
        """

        try:
            import plotly  # noqa: F401
        except ModuleNotFoundError:
            self._raise_cannot_import_plotly()
        else:
            from plotly import express as px
            from plotly import graph_objects as go

            self._px = px
            self._go = go

        self._container = container
        self._last_lines = last_lines
        self._last_models = last_models
        self._update_period_sec = update_period_sec

        repo = self._container
        if isinstance(self._container, ModelLine):
            repo = SingleLineRepo(self._container)

        repos = [repo]
        if isinstance(self._container, Workspace):
            self._container.reload()
            repos = [self._container[name] for name in self._container.get_repo_names()]
            repo = self._container.get_default()
        else:
            for repo in repos:
                repo.reload()

        self._edges = dict()
        self._repo = repo
        self._repos = {repo.get_root(): repo for repo in repos}

        meta = MetaHandler.read_dir(repo.get_root())
        if "cascade_version" not in meta[0]:
            raise RuntimeError(
                "This repository was created before 0.13.0 and has incompatible"
                f" metric format. Please, migrate the repo in {repo.get_root()}"
                " to be able to use the viewer."
                "Use cascade.base.utils.migrate_repo_v0_13"
            )

        self._make_table()

    def _update(self) -> None:
        self._repo.reload()
        self._make_table()

    def _get_last_updated_lines(self, line_names: List[str]) -> List[str]:
        valid_lines = []
        updated_at = []
        for line in line_names:
            try:
                meta = MetaHandler.read_dir(os.path.join(self._repo.get_root(), line))
            except ZeroMetaError:
                continue

            updated_at.append(meta[0]["updated_at"])
            valid_lines.append(line)

        valid_lines = [
            line for line, _ in sorted(zip(valid_lines, updated_at), key=lambda x: x[1])
        ]

        return valid_lines[-self._last_lines:]

    def _make_table(self) -> None:
        metas = []
        params = []

        line_names = self._repo.get_line_names()
        if self._last_lines is not None:
            line_names = self._get_last_updated_lines(line_names)

        for line_name in line_names:
            line = self._repo[line_name]
            line_root = line.get_root()
            view = MetaViewer(line_root, filt={"type": "model"})

            last_models = self._last_models if self._last_models is not None else 0
            for i in range(len(line))[-last_models:]:
                line_name = os.path.split(line_root)[-1]
                new_meta = {"line": line_name, "model": i}
                try:
                    meta = view[i][0]

                    metrics = dict()
                    for metric in meta["metrics"]:
                        name = metric["name"]
                        for key in ["dataset", "split"]:
                            part = metric.get(key)
                            name += "_" + part if part else ""
                        metrics[name] = metric.get("value")
                    meta["metrics"] = metrics

                    new_meta.update(flatten(meta))
                except IndexError:
                    meta = {}
                metas.append(new_meta)

                p = {
                    "line": line_name,
                }
                if "params" in meta:
                    if len(meta["params"]) > 0:
                        p.update(flatten({"params": meta["params"]}))
                params.append(p)

        self._table = pd.DataFrame(metas)
        self._params = params
        if "saved_at" in self._table:
            self._table = self._table.sort_values("saved_at")

        # turn time into evenly spaced intervals
        time = [i for i in range(len(self._table))]
        lines = self._table["line"].unique()

        cmap = self._px.colors.qualitative.Plotly
        cmap_len = len(self._px.colors.qualitative.Plotly)
        line_cols = {line: cmap[i % cmap_len] for i, line in enumerate(lines)}

        self._table["time"] = time
        self._table["color"] = [line_cols[line] for line in self._table["line"]]
        # self._table = self._table.fillna("")

        columns2fill = [
            col for col in self._table.columns if not col.startswith("metrics_")
        ]
        self._table = self._table.fillna({name: "" for name in columns2fill})

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

    def _connect_points(self, line: str, metric: str, fig: Any):
        edges = [0]
        params = [p for p in self._params if p["line"] == line]
        for i in range(1, len(params)):
            diff = self._diff(params[i], params[:i])
            edges.append(self._specific_argmin(diff, i))

        xs = []
        ys = []
        t = self._table.loc[self._table["line"] == line]
        for i, e in enumerate(edges):
            xs += [t["time"].iloc[i], t["time"].iloc[e], None]
            ys += [t[metric].iloc[i], t[metric].iloc[e], None]

        self._edges[line] = {metric: {"edges": (xs, ys), "len": len(t)}}
        return xs, ys

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

        # plot each model against metric
        # with all metadata on hover
        metric = self._preprocess_metric(metric)

        hover_cols = [name for name in pd.DataFrame(self._params).columns]
        if "saved_at" in self._table.columns:
            hover_cols = ["saved_at"] + hover_cols
        hover_cols = ["model"] + hover_cols
        fig = self._px.scatter(
            self._table, x="time", y=metric, hover_data=hover_cols, color="line"
        )
        lines = self._table["line"].unique()

        for line in lines:
            t = self._table.loc[self._table.line == line]
            self._connect_points(line, metric, fig)

            xs, ys = self._edges[line][metric]["edges"]
            fig.add_trace(
                self._go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    name=line,
                    hoverinfo="none",
                    marker_color=t["color"].iloc[0],
                )
            )

        if show:
            fig.show()

        return fig

    def _update_plot(self, metric: str) -> Any:
        metric = self._preprocess_metric(metric)

        hover_cols = [name for name in pd.DataFrame(self._params).columns]
        if "saved_at" in self._table.columns:
            hover_cols = ["saved_at"] + hover_cols
        hover_cols = ["model"] + hover_cols
        fig = self._px.scatter(
            self._table, x="time", y=metric, hover_data=hover_cols, color="line"
        )

        for line in sorted(self._table.line.unique()):
            t = self._table.loc[self._table.line == line]
            if (
                line in self._edges
                and metric in self._edges  # noqa: W503
                and len(t) == self._edges[line][metric]["len"]  # noqa: W503
            ):
                xs, ys = self._edges[line][metric]["edges"]
            else:
                xs, ys = self._connect_points(line, metric, fig)
            fig.add_trace(
                self._go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    name=line,
                    hoverinfo="none",
                    marker_color=t["color"].iloc[0],
                )
            )

        return fig

    def _layout(self, metric: Optional[str]):
        try:
            import dash  # noqa: F401
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import dcc, html  # noqa: F401

        fig = self.plot(metric) if metric is not None else self._go.Figure()

        return html.Div(
            [
                dcc.Dropdown(
                    id="repo-dropdown",
                    options=list(self._repos.keys()),
                    value=self._repo.get_root(),
                ),
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
                dcc.Interval(
                    id="history-interval", interval=1000 * self._update_period_sec
                ),
            ]
        )

    def serve(self, metric: Optional[str] = None, **kwargs: Any) -> None:
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
        This feature needs ``dash`` to be installed.
        """
        # Conditional import
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import Input, Output

        app = dash.Dash()
        app.layout = lambda: self._layout(metric)

        @app.callback(
            Output("viewer-title", "children"), Input("history-interval", "n_intervals")
        )
        def update_title(n_intervals):
            return f"HistoryViewer in {self._repo}"

        @app.callback(
            Output("metric-dropwdown", "options"),
            Input("history-interval", "n_intervals"),
        )
        def update_dropdown(n_intervals):
            return [
                col.replace("metrics_", "")
                for col in self._table.columns
                if col.startswith("metrics_")
            ]

        @app.callback(
            Output("history-figure", "figure"),
            Input("history-interval", "n_intervals"),
            Input("metric-dropwdown", component_property="value"),
            prevent_initial_call=True,
        )
        def update_history(n_intervals, metric):
            self._update()
            return (
                self._update_plot(metric) if metric is not None else self._go.Figure()
            )

        @app.callback(
            Output("metric-dropwdown", "value"),
            Input("repo-dropdown", component_property="value"),
            prevent_initial_call=True,
        )
        def update_repos(name):
            if isinstance(self._container, Workspace):
                self._container.set_default(os.path.split(name)[-1])

        app.run_server(use_reloader=False, **kwargs)
