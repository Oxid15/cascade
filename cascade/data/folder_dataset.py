import os

from typing import List, Dict
from hashlib import md5
from .dataset import Dataset, T


class FolderDataset(Dataset):
    """
    Basic "folder of files" dataset. Accepts root folder in which considers all files.
    Is abstract - getitem is not defined, since it is specific for each file type.

    See also
    --------
    cascade.utils.FolderImageDataset
    """
    def __init__(self, root: str, *args, **kwargs) -> None:
        """
        Parameters
        ----------
        root: str
            A path to the folder of files 
        """
        super().__init__(*args, **kwargs)
        self._root = os.path.abspath(root)
        if not os.path.exists(self._root):
            raise FileNotFoundError(self._root)
        self._names = [os.path.join(self._root, name)
                       for name in sorted(os.listdir(self._root)) if not os.path.isdir(name)]

    def __getitem__(self, item) -> T:
        raise NotImplementedError()

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
            'name': repr(self),
            'len': len(self),
            'paths': self._names,
            'md5sums': []
        })

        for name in self._names:
            with open(os.path.join(self._root, name), 'rb') as f:
                meta[0]['md5sums'].append(md5(f.read()).hexdigest())
        return meta

    def __len__(self) -> int:
        return len(self._names)
