import click


@click.group("artifact")
@click.pass_context
def artifact(ctx):
    """
    Manage artifacts
    """


@artifact.command("rm")
@click.pass_context
def artifact_rm(ctx):
    if ctx.obj["type"] != "model":
        click.echo(f"Cannot remove an artifact from {ctx.obj['type']}")

    raise NotImplementedError()