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
import traceback
from collections import Counter
from dataclasses import dataclass
from typing import List, Literal, Optional

import click


@dataclass
class RemoveResult:
    """
    OKAY - file was deleted without any problems

    MISS - the artifact folder was not found or empty

    FAIL - something went wrong when removing a file
    """
    status: Literal["OKAY", "MISS", "FAIL"]
    path: Optional[str] = None
    traceback: Optional[str] = None


def remove_files(path: str) -> List[RemoveResult]:
    if not os.path.exists(path):
        return [RemoveResult("MISS")]

    files = os.listdir(path)
    if len(files) == 0:
        return [RemoveResult("MISS")]

    results = []
    for name in files:
        file_path = os.path.join(path, name)
        try:
            os.remove(file_path)
        except Exception:
            tb = traceback.format_exc()
            results.append(RemoveResult("FAIL", traceback=tb, path=file_path))
        else:
            results.append(RemoveResult("OKAY"))
    return results


@click.group("artifact")
@click.pass_context
def artifact(ctx):
    """
    Manage artifacts
    """


@artifact.command("rm")
@click.pass_context
def artifact_rm(ctx):
    results_list = []
    flat_results = []
    if ctx.obj["type"] == "model":
        results = remove_files(os.path.join(ctx.obj["cwd"], "artifacts"))
        results_list.append(results)
        flat_results.extend(results)
    else:
        raise NotImplementedError()

    c = Counter(res.status for res in flat_results)

    click.echo(f"Found {c['OKAY'] + c['FAIL']} files in {len(results_list)} models")
    click.echo(f"Removed: {c['OKAY']}")
    click.echo(f"Missing files: {c['MISS']}")
    click.echo(f"Failed: {c['FAIL']}")

    if c["FAIL"] != 0:
        for res in flat_results:
            if res.status == "FAIL":
                click.echo(f"Failed to remove {res.path}")
                click.echo(res.traceback)
