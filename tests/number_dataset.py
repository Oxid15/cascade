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
import sys

sys.path.append(os.path.abspath('../..'))
from cascade.data import Dataset


class NumberDataset(Dataset):
    def __init__(self, arr):
        self.numbers = arr
        super().__init__()

    def __getitem__(self, index):
        return self.numbers[index]

    def __len__(self):
        return len(self.numbers)

    def get_meta(self):
        meta = super().get_meta()
        meta[0]['len'] = len(self)
        return meta
