from typing import Any, Dict

from .base_diff_viewer import BaseDiffViewer
from ...base import MetaHandler


class HistoryDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._default_depth = 2
        self._default_diff_depth = 1

    def _read_objects(self, path: str) -> Dict[str, Any]:
        self._check_path(path, ("history",))

        history = MetaHandler.read(path)["history"]

        return {item["updated_at"]: item for item in history}
