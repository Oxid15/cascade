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
import pendulum
import numpy as np
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.meta import MetaHandler


class TestMetaHandler(TestCase):
    def test(self):
        mh = MetaHandler()
        mh.write('test.json', 
        {
            'name': 'test',
            'array': np.zeros(4),
            'none': None,
            'date': pendulum.now(tz='UTC')
        })

        obj = mh.read('test.json')

        os.remove('test.json')

        self.assertEqual(obj['name'], 'test')
        self.assertTrue(all(obj['array'] == np.zeros(4)))
        self.assertTrue(obj['none'] is None)


if __name__ == '__main__':
    unittest.main()
