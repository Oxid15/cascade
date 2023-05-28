import os
from typing import Any, Dict, Union
from ..base import Traceable
from ..models import ModelRepo


class Workspace(Traceable):
    def __init__(
        self,
        path: str,
        default_repo: Union[str, None] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self._root = path
        self._default = default_repo
        names = [name for name in os.listdir(self._root) if os.path.isdir(name)]
        for name in names:
            pass

    def __getitem__(self, key):
        pass
