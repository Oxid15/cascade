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

import click

from .common import create_container


@click.command("history")
@click.pass_context
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=8050)
@click.option("-l", type=int, help="The number of last lines to show")
@click.option("-m", type=int, help="The number of last models to show")
@click.option("-p", type=int, default=3, help="Update period in seconds")
def view_history(ctx, host, port, l, m, p):  # noqa: E741
    if ctx.obj.get("meta"):
        container = create_container(ctx.obj["type"], ctx.obj["cwd"])
        if not container:
            click.echo(f"Cannot open History Viewer in object of type `{ctx.obj['type']}`")
            return

        from ..meta import HistoryViewer

        HistoryViewer(container, last_lines=l, last_models=m, update_period_sec=p).serve(
            host=host, port=port
        )


@click.command("metric")
@click.pass_context
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=8050)
@click.option("-p", type=int, default=50, help="Page size for table")
@click.option("-i", type=str, multiple=True, help="Metrics or params to include")
@click.option("-x", type=str, multiple=True, help="Metrics or params to exclude")
def view_metric(ctx, host, port, p, i, x):
    type = ctx.obj["type"]
    if type == "repo":
        from ..repos import Repo

        container = Repo(ctx.obj["cwd"])
    elif type == "line":
        from ..models import ModelLine

        container = ModelLine(ctx.obj["cwd"])
    else:
        click.echo(f"Cannot open Metric Viewer in object of type `{type}`")
        return

    from ..meta import MetricViewer

    i = None if len(i) == 0 else list(i)
    x = None if len(x) == 0 else list(x)
    MetricViewer(container).serve(page_size=p, include=i, exclude=x, host=host, port=port)


@click.command("diff")
@click.pass_context
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=8050)
def view_diff(ctx, host, port):
    from ..meta import DiffViewer

    DiffViewer(ctx.obj["cwd"]).serve(host=host, port=port)


@click.group
@click.pass_context
def view(ctx):
    """
    Different viewers
    """
    pass


view.add_command(view_diff)
view.add_command(view_history)
view.add_command(view_metric)
