"""
Copyright 2022-2023 Ilia Moiseev

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

import cv2
from ..data import FolderDataset


class FolderImageDataset(FolderDataset):
    """
    Simple dataset for image folder with lazy loading.
    Accepts the path to the folder with images. In each __getitem__ call
    invokes opencv imread on image and returns it if it exists.
    """

    def __getitem__(self, index: int) -> cv2.Mat:
        name = self._names[index]
        img = cv2.imread(f'{name}')
        if img is not None:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            raise RuntimeError(f'cv2 cannot read {name}')
