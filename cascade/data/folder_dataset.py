import os

from typing import List, Dict
from hashlib import md5
from .dataset import Dataset, T


class FolderDataset(Dataset):
    """
    Basic "folder of files" dataset. Accepts root folder in which considers all files.
    Is abstract - getitem is not defined, since it is specific for each file type

    See also
    --------
    cascade.utils.FolderImageDataset
    """
    def __init__(self, root, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root = os.path.abspath(root)
        assert os.path.exists(self.root)
        self.names = [os.path.join(self.root, name) for name in sorted(os.listdir(self.root)) if not os.path.isdir(name)]

    def __getitem__(self, item) -> T:
        raise NotImplementedError()

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
            'name': repr(self),
            'len': len(self),
            'paths': self.names,
            'md5sums': []
        })

        for name in self.names:
            with open(os.path.join(self.root, name), 'rb') as f:
                meta[0]['md5sums'].append(md5(f.read()).hexdigest())
        return meta

    def __len__(self):
        return len(self.names)
