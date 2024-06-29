import click


@click.command("add")
@click.pass_context
@click.argument("t", nargs=-1)
def tag_add(ctx, t):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import TraceableOnDisk

    tr = TraceableOnDisk(ctx.obj["cwd"], meta_fmt=ctx.obj["meta_fmt"])
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
