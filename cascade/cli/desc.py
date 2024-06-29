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
    tr.describe(d)
