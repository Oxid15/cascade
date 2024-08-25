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
import pendulum
from flatten_json import flatten

from ..base import MetaHandler
from ..lines import ModelLine
from ..models import Model
from ..repos import Repo, SingleLineRepo
from .meta_viewer import MetaViewer
from .server import Server


class MetricViewer:
    """
    Interface for viewing metrics in model meta files
    uses Repo to extract metrics of all models if any.
    As metrics it uses data from ``metrics`` field in models'
    meta and as parameters it uses ``params`` field.
    """

    def __init__(
        self, repo: Union[Repo, ModelLine], scope: Union[int, str, slice, None] = None
    ) -> None:
        """
        Parameters
        ----------
        repo: Repo
            Repo object to extract metrics from
        scope: Union[int, str, slice]
            Index or a name of line to view. Can be set using ``__getitem__``
        """
        if isinstance(repo, ModelLine):
            repo = SingleLineRepo(repo)

        meta = MetaHandler.read_dir(repo.get_root())
        if "cascade_version" not in meta[0]:
            raise RuntimeError(
                "This repository was created before 0.13.0 and has incompatible"
                f" metric format. Please, migrate the repo in {repo.get_root()}"
                " to be able to use the viewer."
                "Use cascade.base.utils.migrate_repo_v0_13"
            )

        self._repo = repo
        self._scope = scope
        self._metrics = []
        self.reload_table()

    def __getitem__(self, key: Union[int, str, slice]):
        """
        Sets the scope of the viewer after creation.
        Basically creates new viewer with another scope.
        """
        return MetricViewer(self._repo, scope=key)

    def reload_table(self) -> None:
        def create_metric(meta: Dict[str, Any]) -> Dict[str, Any]:
            metric = {"line": line, "num": i}
            if "created_at" in meta:
                metric["created_at"] = pendulum.parse(meta["created_at"])
                if "saved_at" in meta:
                    metric["saved"] = pendulum.parse(
                        meta["saved_at"]
                    ).diff_for_humans(metric["created_at"])

            if "params" in meta:
                metric.update(meta["params"])
            if "tags" in meta:
                metric["tags"] = meta["tags"]
            if "comments" in meta:
                metric["comment_count"] = len(meta["comments"])
            if "links" in meta:
                metric["link_count"] = len(meta["links"])

            return metric

        self._metrics = []
        selected_names = self._repo.get_line_names()

        if self._scope is not None:
            selected_names = selected_names[self._scope]
            if not isinstance(selected_names, list):
                selected_names = [selected_names]

        for name in selected_names:
            line = self._repo[name]
            viewer_root = line.get_root()

            view = MetaViewer(viewer_root, filt={"type": "model"})

            for i in range(len(line)):
                try:
                    meta = view[i][-1]  # Takes last model from meta
                except IndexError:
                    meta = {}

                _, line = os.path.split(viewer_root)
                if "metrics" in meta:
                    # Need to generate new metric each time
                    for m in meta["metrics"]:
                        metric = create_metric(meta)

                        metric["name"] = m.get("name")
                        metric["value"] = m.get("value")

                        for key in m.keys():
                            if key not in ("name", "value", "created_at"):
                                if m[key] is not None:
                                    metric[key] = m[key]

                        self._metrics.append(metric)
                else:
                    self._metrics.append(create_metric(meta))
        self.table = pd.DataFrame(self._metrics)

    def __repr__(self) -> str:
        return repr(self.table)

    def plot_table(self, show: bool = False):
        """
        Uses plotly to graphically show table with metrics and parameters.
        """

        try:
            import plotly  # noqa: F401
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                """
                        Cannot import plotly. It is conditional
                        dependency you can install it
                        using the instructions from plotly official documentation"""
            )
        else:
            from plotly import graph_objects as go

        data = pd.DataFrame(map(flatten, self.table.to_dict("records")))
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(data.columns), fill_color="#f4c9c7", align="left"
                    ),
                    cells=dict(
                        values=[data[col] for col in data.columns],
                        fill_color="#bcced4",
                        align="left",
                    ),
                )
            ]
        )
        if show:
            fig.show()
        return fig

    def get_best_by(self, metric: str, maximize: bool = True) -> Model:
        """
        Loads the best model by the given metric

        Parameters
        ----------
        metric: str
            Name of the metric
        maximize: bool
            The direction of choosing the best model: ``True`` if greater is better
            and ``False`` if less is better

        Raises
        ------
        TypeError if metric objects cannot be sorted. If only one model in repo, then
        returns it without error since no sorting involved.
        """
        assert metric in self.table["name"].unique(), f"{metric} is not in {self.table.columns}"
        t = self.table.loc[self.table["name"] == metric]

        try:
            t = t.sort_values("value", ascending=maximize)
        except TypeError as e:
            raise TypeError(f"Metric {metric} objects cannot be sorted") from e

        best_row = t.iloc[-1]
        name = os.path.split(best_row["line"])[-1]
        num = best_row["num"]
        return self._repo[name][num]

    def serve(
        self,
        page_size: int = 50,
        include: Union[List[str], None] = None,
        exclude: Union[List[str], None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Runs dash-based server with interactive table of metrics and parameters

        Parameters
        ----------
        page_size: int, optional
            Size of the table in rows on one page
        include: List[str], optional:
            List of parameters or metrics to be added.
            Only they will be present along with some default
        exclude: List[str], optional:
            List of parameters or metrics to be excluded from table
        **kwargs:
            Arguments of dash app. Can be ip or port for example
        """
        server = MetricServer(
            self, page_size=page_size, include=include, exclude=exclude
        )
        server.serve(**kwargs)


class MetricServer(Server):
    def __init__(
        self,
        mv: MetricViewer,
        page_size: int,
        include: Optional[List[str]],
        exclude: Optional[List[str]],
        **kwargs: Any,
    ) -> None:
        self._mv = mv
        self._page_size = page_size
        self._include = include
        self._exclude = exclude

    def _update_graph_callback(self, _app) -> None:
        try:
            from dash import Input, Output
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from plotly import graph_objects as go

        @_app.callback(
            Output(component_id="dependence-figure", component_property="figure"),
            Input(component_id="dropdown-x", component_property="value"),
            Input(component_id="dropdown-y", component_property="value"),
        )
        def _update_graph(x, y):
            fig = go.Figure()
            if x is not None and y is not None:
                fig.add_trace(
                    go.Scatter(
                        x=self._for_plots[x], y=self._for_plots[y], mode="markers"
                    )
                )
                fig.update_layout(title=f"{x} to {y} relation")
            return fig

    def _layout(self):
        try:
            from dash import dash_table, dcc, html
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from plotly import graph_objects as go

        self._mv._repo.reload()
        self._mv.reload_table()

        df = self._mv.table
        if self._exclude is not None:
            df = df.drop(self._exclude, axis=1)

        if self._include is not None:
            df = df[["line", "num"] + self._include]

        self._df_flatten = pd.DataFrame(
            map(lambda x: flatten(x, root_keys_to_ignore=["tags"]), df.to_dict("records"))
        )
        self._for_plots = self._df_flatten.copy()
        for name in self._df_flatten.name.unique():
            self._for_plots[name] = None
            self._for_plots.loc[self._for_plots["name"] == name, name] = (
                self._for_plots.loc[self._for_plots["name"] == name, "value"]
            )
        self._for_plots = self._for_plots.drop(["name", "value"], axis=1)

        if any(df["tags"].apply(lambda x: x != [])):
            self._df_flatten["tags"] = df["tags"].apply(lambda x: ",".join(x))
        dep_fig = go.Figure()

        return html.Div(
            [
                html.H1(
                    children=f"MetricViewer in {self._mv._repo}",
                    style={
                        "textAlign": "center",
                        "color": "#084c61",
                        "font-family": "Montserrat",
                    },
                ),
                dcc.Dropdown(
                    list(self._for_plots.columns), id="dropdown-x", multi=False
                ),
                dcc.Dropdown(
                    list(self._for_plots.columns), id="dropdown-y", multi=False
                ),
                dcc.Graph(id="dependence-figure", figure=dep_fig),
                dash_table.DataTable(
                    columns=[
                        {"name": col, "id": col, "selectable": True}
                        for col in self._df_flatten.columns
                    ],
                    data=self._df_flatten.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=self._page_size,
                ),
            ]
        )

    def serve(self, **kwargs: Any) -> None:
        # Conditional import
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        app = dash.Dash()
        app.layout = self._layout
        self._update_graph_callback(app)
        app.run_server(use_reloader=False, **kwargs)
