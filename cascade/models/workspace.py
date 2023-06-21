import os
import glob
from typing import Any, Dict, Union
import warnings
from ..base import Traceable, MetaHandler
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
        dirs = [name for name in os.listdir(self._root) if os.path.isdir(name)]
        self._repo_names = []
        for d in dirs:
            meta_path = sorted(glob.glob(os.path.join(d, 'meta.*')))
            if len(meta_path) == 1:
                meta = MetaHandler.read(meta_path[0])
                if meta[0]['type'] == 'repo':
                    self._repo_names.append(d)
            else:
                warnings.warn(f'Found {len(meta_path)} meta files in {d}')

    def __getitem__(self, key: Any) -> ModelRepo:
        pass

    def __len__(self):
        return len(self._repo_names)
