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

import numpy as np
from ..data import Wrapper


class NumpyWrapper(Wrapper):
    """
    A wrapper around .npy files. Loads file on `__init__`.
    """
    def __init__(self, path, *args, **kwargs):
        self._path = path
        super().__init__(np.load(path), *args, **kwargs)

    def get_meta(self):
        meta = super().get_meta()
        meta[-1]['root'] = self._path
