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
import datetime
import os
import json
import sys
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Dataset, Iterator, Wrapper, Modifier, Sampler
from cascade.tests.number_dataset import NumberDataset


class TestDataset(TestCase):
    def test_getitem(self):
        ds = Dataset()
        with self.assertRaises(NotImplementedError):
            ds[0]

    def test_meta(self):
        now = datetime.datetime.now()
        ds = Dataset(meta_prefix={'time': now})
        meta = ds.get_meta()

        self.assertEqual(type(meta), list)
        self.assertEqual(len(meta), 1)
        self.assertEqual(type(meta[0]), dict)
        self.assertEqual(meta[0]['time'], now)
        self.assertTrue('name' in meta[0])

    def test_update_meta(self):
        ds = Dataset(meta_prefix={'a': 1, 'b': 2})
        ds.update_meta({'b': 3})
        meta = ds.get_meta()

        self.assertEqual(meta[0]['a'], 1)
        self.assertEqual(meta[0]['b'], 3)

    def test_meta_from_file(self):
        with open('test_meta_from_file.json', 'w') as f:
            json.dump({'a': 1}, f)

        ds = Dataset(meta_prefix='test_meta_from_file.json')
        meta = ds.get_meta()

        self.assertTrue('a' in meta[0])
        self.assertEqual(meta[0]['a'], 1)


class TestIterator(TestCase):
    def test(self):
        it = Iterator([1, 2, 3, 4])
        res = []
        for item in it:
            res.append(item)
        self.assertEqual([1, 2, 3, 4], res)


class TestWrapper(TestCase):
    def test(self):
        wr = Wrapper([1, 2, 3, 4])
        res = []
        for i in range(len(wr)):
            res.append(wr[i])
        self.assertEqual([1, 2, 3, 4], res)


class TestModifier(TestCase):
    def test(self):
        ds = NumberDataset([1, 2, 3, 4])
        ds = Modifier(ds)

        res = []
        for i in range(len(ds)):
            res.append(ds[i])
        self.assertEqual([1, 2, 3, 4], res)

        res = []
        for it in ds:
            res.append(it)
        self.assertEqual([1, 2, 3, 4], res)

    def test_meta(self):
        ds = NumberDataset([1, 2, 3, 4])
        ds = Modifier(ds)

        meta = ds.get_meta()
        self.assertEqual(type(meta), list)
        self.assertEqual(len(meta), 2)


class TestSampler(TestCase):
    def test(self):
        ds = NumberDataset([1, 2, 3, 4])
        ds = Sampler(ds, 10)


if __name__ == '__main__':
    unittest.main()
