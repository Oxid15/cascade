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
import json
import shutil
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.meta import MetaHandler, MetaViewer


class TestMetaHandler(TestCase):
    def test(self):
        mh = MetaHandler()
        mh.write('test.json', {'name': 'test'})

        obj = mh.read('test.json')

        os.remove('test.json')

        self.assert_('name' in obj)
        self.assertEqual(obj['name'], 'test')


class TestMetaViewer(TestCase):
    def test(self):
        root = 'metas'
        os.mkdir(root)
        with open(f'{root}/test.json', 'w') as f:
            json.dump({'name': 'test'}, f)

        mv = MetaViewer(root)
        obj = mv[0]

        shutil.rmtree(root)

        self.assertEqual(len(mv), 1)
        self.assert_('name' in obj)
        self.assertEqual(obj['name'], 'test')


if __name__ == '__main__':
    unittest.main()
