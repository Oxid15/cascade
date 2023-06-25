from .base_diff_viewer import BaseDiffViewer


class WorkspaceDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)

        self._default_depth = 2
        self._default_diff_depth = 2

    # def
