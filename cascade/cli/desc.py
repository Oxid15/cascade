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


@click.group("desc")
@click.pass_context
def desc(ctx):
    """
    Manage descriptions
    """


@desc.command("add")
@click.pass_context
@click.option("-d", prompt="Description: ")
def desc_add(ctx, d):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
    tr.sync_meta()
    tr.describe(d)


@desc.command("rm")
@click.pass_context
def desc_rm(ctx):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
    tr.sync_meta()
    tr.remove_description()
