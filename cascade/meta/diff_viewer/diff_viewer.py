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

import os
from typing import Any

from ...base import MetaHandler, MetaIOError, ZeroMetaError
from ...meta.server import Server
from .repo_diff_viewer import RepoDiffViewer
from .workspace_diff_viewer import WorkspaceDiffViewer


class DiffViewer(Server):
    """
    The dash-based server to view meta-data
    and compare different snapshots using deep diff.

    It can work with Repos or Workspaces
    """

    def __init__(self, path: str) -> None:
        super().__init__()

        self._diff_viewer = self._get_viewer(path)

    def _get_viewer(self, path: str):
        """
        Determines the type of DiffReader and returns it
        """
        if os.path.isdir(path):

            try:
                meta = MetaHandler.read_dir(path)

                if meta[0]["type"] == "repo":
                    return RepoDiffViewer(path)
                elif meta[0]["type"] == "workspace":
                    return WorkspaceDiffViewer(path)
                else:
                    raise ValueError(
                        f"No viewer found for meta with type {meta[0]['type']}"
                    )
            except ZeroMetaError:
                # In this case should check internal folder
                # I suppose that this could be folder
                # that can be Workspace but doesn't have meta
                abs_path = os.path.abspath(path)
                folders = sorted(
                    [
                        path
                        for path in os.listdir(abs_path)
                        if os.path.isdir(os.path.join(abs_path, path))
                    ]
                )
                for folder in folders:
                    try:
                        meta = MetaHandler.read_dir(os.path.join(path, folder))
                    except MetaIOError:
                        continue

                    if meta[0]["type"] == "repo":
                        return WorkspaceDiffViewer(path)
                    elif meta[0]["type"] == "line":
                        return RepoDiffViewer(path)
                    else:
                        raise ValueError(
                            f"No viewer found for folder with objects of type {meta[0]['type']}"
                        )
        else:  # The given meta is a file
            raise ValueError("DiffViewer only supports folders")

    def serve(self, *args: Any, **kwargs: Any):
        return self._diff_viewer.serve(*args, **kwargs)
