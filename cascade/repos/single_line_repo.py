from typing import Any, Dict, List, Literal, Optional

from ..lines import Line
from .base_repo import BaseRepo


class SingleLineRepo(BaseRepo):
    def __init__(
        self,
        line: Line,
        *args: Any,
        meta_prefix: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(line.get_root(), *args, meta_prefix=meta_prefix, **kwargs)
        self._lines = {line.get_root(): {"args": [], "kwargs": dict()}}
        self._line = line

    def __getitem__(self, key: str) -> Line:
        if key in self._lines:
            return self._line
        else:
            raise KeyError(
                f"The only line is {list(self._lines.keys())[0]}, {key} does not exist"
            )

    def __repr__(self) -> str:
        return f"SingleLine in {self._root}"

    def get_root(self) -> str:
        return self._root

    def reload(self) -> None:
        self._line.reload()

    def __len__(self) -> Literal[1]:
        return 1

    def get_line_names(self) -> List[str]:
        return [self._root]
