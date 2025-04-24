"""
Copyright 2022-2025 Ilia Moiseev

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


@click.command("ui")
@click.option("--path", default=".")
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8000)
@click.pass_context
def ui(ctx, path, host, port):
    if not ctx.obj.get("meta"):
        return

    if ctx.obj["meta"][0]["type"] != "workspace":
        click.echo("UI is only available inside workspaces")
        return

    try:
        from cascade_ui.server import run
    except ImportError:
        raise ImportError(
            "cascade_ui package is required to run UI. Install it with 'pip install cascade-ui'"
        )
    else:
        run(path, host, port)
