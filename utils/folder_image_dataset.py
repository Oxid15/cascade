"""
Copyright 2022 Ilia Moiseev

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
from hashlib import md5
from typing import List, Dict

import cv2
from ..data import Dataset, T


class FolderImageDataset(Dataset):
    """
    Simple dataset for image folder with lazy loading.
    Accepts the path to the folder with images. In each __getitem__ call
    invokes opencv imread on image and returns it if it exists.
    """
    def __init__(self, root):
        self.root = os.path.abspath(root)
        assert os.path.exists(self.root)
        self.image_names = sorted(os.listdir(self.root))

    def __getitem__(self, index) -> T:
        name = self.image_names[index]
        fullname = os.path.join(self.root, name)
        img = cv2.imread(f'{fullname}')
        if img is not None:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            raise RuntimeError(f'cv2 cannot read {fullname}')

    def __len__(self):
        return len(self.image_names)

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
                'name': repr(self),
                'size': len(self),
                'paths': self.image_names,
                'md5sums': []
        })

        for name in self.image_names:
            with open(os.path.join(self.root, name), 'rb') as f:
                meta[0]['md5sums'].append(md5(f.read()).hexdigest())
        return meta
