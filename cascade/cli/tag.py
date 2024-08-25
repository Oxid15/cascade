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


@click.command("add")
@click.pass_context
@click.argument("t", nargs=-1)
def tag_add(ctx, t):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
    tr.sync_meta()
    tr.tag(t)


@click.command("ls")
@click.pass_context
def tag_ls(ctx):
    if not ctx.obj.get("meta"):
        return

    tags = ctx.obj["meta"][0].get("tags")
    click.echo(tags)


@click.command("rm")
@click.pass_context
@click.argument("t", nargs=-1)
def tag_rm(ctx, t):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
    tr.sync_meta()
    tr.remove_tag(t)


@click.group
@click.pass_context
def tag(ctx):
    """
    Manage tags
    """
    pass


tag.add_command(tag_add)
tag.add_command(tag_ls)
tag.add_command(tag_rm)
