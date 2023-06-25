from typing import Any, Dict

from .base_diff_viewer import BaseDiffViewer
from ...base import MetaHandler


class DatasetVersionDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._default_depth = 9
        self._default_diff_depth = 8

    def _read_objects(self, path: str) -> Dict[str, Any]:
        self._check_path(path, "version_history")

        versions = MetaHandler.read(path)["versions"]

        version_dict = {}
        for pipe_key in versions:
            for meta_key in versions[pipe_key]:
                version_dict.update(
                    {
                        versions[pipe_key][meta_key]["version"]: versions[pipe_key][
                            meta_key
                        ]
                    }
                )
        return {key: version_dict[key] for key in sorted(version_dict.keys())}
