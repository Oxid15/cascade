from abc import ABC, abstractmethod
from typing import Any, List

from ..base import Meta
from ..base.traceable import Traceable
from ..lines import Line
from ..version import __version__


class BaseRepo(Traceable, ABC):
    """
    Base interface for repos. Repo is the collection of Lines.

    See also
    --------
    cascade.base.Repo
    """

    def __init__(
        self,
        path: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._root = path
        self._lines = dict()
        super().__init__(*args, **kwargs)

    @abstractmethod
    def __getitem__(self, key: str) -> Line: ...

    @abstractmethod
    def __len__(self) -> int: ...

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "root": self._root,
                "len": len(self),
                "type": "repo",
                "cascade_version": __version__,
            }
        )
        return meta

    @abstractmethod
    def get_line_names(self) -> List[str]: ...

    @abstractmethod
    def reload(self) -> None: ...
