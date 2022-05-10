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
from typing import List, Dict

import numpy as np
from ..data import Dataset


class TextClassificationDataset(Dataset):
    def __init__(self, path, encoding='utf-8'):
        self.encoding = encoding
        self.root = os.path.abspath(path)
        folders = os.listdir(self.root)
        self.paths = []
        self.labels = []
        for i, folder in enumerate(folders):
            files = [name for name in os.listdir(os.path.join(self.root, folder))]
            self.paths += [os.path.join(self.root, folder, f) for f in files]
            self.labels += [i for _ in range(len(files))]

        print(f'Found {len(folders)} classes: \
            {[(folder, len(os.listdir(os.path.join(self.root, folder)))) for folder in folders]}')

    def __getitem__(self, index):
        with open(self.paths[index], 'r', encoding=self.encoding) as f:
            text = ' '.join(f.readlines())
            label = self.labels[index]
        return text, label

    def __len__(self):
        return len(self.paths)

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
                'name': repr(self),
                'size': len(self),
                'root': self.root,
                'labels': np.unique(self.labels).tolist()
            })
        return meta
