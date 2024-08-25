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
from math import ceil
from typing import Dict, List

import click

from .common import create_container


def comments_table(comments: List[Dict[str, str]]) -> str:
    import pendulum

    left_limit = 50
    between_cols = 3
    w, _ = os.get_terminal_size()

    comm_meta = []
    comm_date = []
    for c in comments:
        comm_meta.append(", ".join((c["id"], c["user"], c["host"])))
        date = pendulum.parse(c["timestamp"]).diff_for_humans(pendulum.now())
        comm_date.append(date)

    w_left = max(max([len(r1) for r1 in comm_meta]), max([len(r2) for r2 in comm_date]))
    w_left = min(w_left, left_limit)
    w_right = w - (w_left + between_cols)

    table = ""
    for i, c in enumerate(comments):
        # Minimum two rows for comments meta data
        n_rows = max(2, ceil(len(c["message"]) / w_right))
        for row in range(n_rows):
            if row == 0:
                table += (
                    comm_meta[i]
                    if len(comm_meta[i]) <= left_limit
                    else comm_meta[i][: left_limit - 3] + "..."
                )
                table += " " * (
                    w_left - min(len(comm_meta[i]), left_limit) + between_cols
                )
            elif row == 1:
                table += comm_date[i]
                table += " " * (w_left - len(comm_date[i]) + between_cols)
            else:
                table += " " * (w_left + between_cols)

            # Output comment's text by batches
            table += (
                c["message"][
                    row * w_right: min((row + 1) * w_right, len(c["message"]))
                ] + "\n"
            )
        table += "\n"
    return table


@click.command("add")
@click.pass_context
@click.option("-c", prompt="Comment")
def comment_add(ctx, c):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
    tr.sync_meta()
    tr.comment(c)


@click.command("ls")
@click.pass_context
def comment_ls(ctx):
    comments = ctx.obj["meta"][0].get("comments")
    if comments:
        t = comments_table(comments)
        click.echo(t)
    else:
        click.echo("No comments here")

    container = create_container(ctx.obj.get("type"), ctx.obj.get("cwd"))
    if container:
        from cascade.lines import ModelLine

        comment_counter = 0
        if isinstance(container, ModelLine):
            for i in range(len(container)):
                meta = container.load_model_meta(i)
                if "comments" in meta[0]:
                    comment_counter += len(meta[0]["comments"])
        else:
            for item in container:
                meta = item.load_meta()
                if "comments" in meta[0]:
                    comment_counter += len(meta[0]["comments"])

        click.echo(
            f"{comment_counter} comment{'s' if comment_counter != 1 else ''} inside total"
        )


@click.command("rm")
@click.pass_context
@click.argument("id")
def comment_rm(ctx, id):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
    tr.sync_meta()
    tr.remove_comment(id)


@click.group
def comment():
    """
    Manage comments
    """


comment.add_command(comment_add)
comment.add_command(comment_ls)
comment.add_command(comment_rm)
