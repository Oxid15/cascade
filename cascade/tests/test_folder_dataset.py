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
import unittest
import shutil
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import FolderDataset


class TestFolderDataset(TestCase):
    def test(self):
        folder = './folder_dataset'
        os.mkdir(folder)
        with open('./folder_dataset/0.txt', 'w') as w:
            w.write('hello')

        ds = FolderDataset(folder)
        meta = ds.get_meta()[0]

        self.assertEqual(len(ds), 1)
        self.assertTrue('name' in meta)
        self.assertTrue('len' in meta)
        self.assertTrue('paths' in meta)
        self.assertTrue('md5sums' in meta)
        self.assertEqual(len(meta['paths']), 1)
        self.assertEqual(len(meta['md5sums']), 1)


if __name__ == '__main__':
    unittest.main()
