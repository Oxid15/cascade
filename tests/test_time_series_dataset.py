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
from datetime import datetime
import pendulum
import unittest
from unittest import TestCase

import pandas as pd
import numpy as np

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.utils import TimeSeriesDataset, Average, Interpolate, Align
from cascade.tests.number_dataset import NumberDataset


class TestTimeSeriesDataset(TestCase):
    def test_create_lists(self):
        # Lists of datetime
        time = [d.to_pydatetime() for d in pd.date_range(datetime(2000, 1, 1), datetime(2000, 1, 10), freq='1d')]
        data = [i for i in range(len(time))]
        ts = TimeSeriesDataset(time=time, data=data)

    def test_create_arrays(self):
        # Arrays of datetime
        time = np.array([datetime(2000, 1, 1),
                         datetime(2000, 1, 2),
                         datetime(2000, 1, 3)])
        data = np.array([1, 2, 3])
        ts = TimeSeriesDataset(time=time, data=data)

    def test_unsorted_time(self):
        # Unsorted datetime
        time = [datetime(2000, 1, 2),
                datetime(2000, 1, 1),
                datetime(2000, 1, 3)]
        data = np.array([2, 1, 3])
        ts = TimeSeriesDataset(time=time, data=data)

        time, data = ts.get_data()

        self.assertTrue(np.all(data == np.array([1, 2, 3])))
        self.assertTrue(np.all(time == np.array([datetime(2000, 1, 1),
                                                 datetime(2000, 1, 2),
                                                 datetime(2000, 1, 3)])))

    def test_no_datetime(self):
        time = [i for i in range(10)]
        data = [i for i in range(len(time))]

        # Only datetime instances in time
        with self.assertRaises(AssertionError):
            ts = TimeSeriesDataset(time=time, data=data)

    def test_length_check(self):
        time = np.array([datetime(2000, 1, 1),
                         datetime(2000, 1, 2),
                         datetime(2000, 1, 3)])
        data = np.array([1, 2])
        with self.assertRaises(AssertionError):
            ts = TimeSeriesDataset(time=time, data=data)

    def test_shape_check(self):
        time = np.array([datetime(2000, 1, 1),
                         datetime(2000, 1, 2),
                         datetime(2000, 1, 3)])
        data = np.array([[1, 2], [1, 2], [1, 2]])
        with self.assertRaises(AssertionError):
            ts = TimeSeriesDataset(time=time, data=data)

    def test_get_int(self):
        time = np.array([datetime(2001, 1, 1),
                         datetime(2002, 2, 2),
                         datetime(2003, 3, 3)])
        data = np.array([1, 2, 3])
        ts = TimeSeriesDataset(time=time, data=data)

        items = []
        for i in range(len(ts)):
            items.append(ts[i])
        self.assertEqual(items, [1, 2, 3])

    def test_get_datetime(self):
        time = np.array([datetime(2001, 1, 1),
                         datetime(2002, 2, 2),
                         datetime(2003, 3, 3)])
        data = np.array([1, 2, 3])
        ts = TimeSeriesDataset(time=time, data=data)

        items = []
        for t in [datetime(2001, 1, 1), datetime(2002, 2, 2), datetime(2003, 3, 3)]:
            items.append(ts[t])
        self.assertEqual(items, [1, 2, 3])

    def test_slice_int(self):
        time = np.array([datetime(2001, 1, 1),
                         datetime(2001, 1, 2),
                         datetime(2001, 1, 3),
                         datetime(2001, 1, 4),
                         datetime(2001, 1, 5)])
        data = np.array([1, 2, 3, 4, 5])
        ts = TimeSeriesDataset(time=time, data=data)

        sl = ts[1:4]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [2, 3, 4])

        sl = ts[:2]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [1, 2])

        sl = ts[2:]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [3, 4, 5])

    def test_slice_datetime(self):
        time = np.array([datetime(2001, 1, 1),
                         datetime(2001, 1, 2),
                         datetime(2001, 1, 3),
                         datetime(2001, 1, 4),
                         datetime(2001, 1, 5)])
        data = np.array([1, 2, 3, 4, 5])
        ts = TimeSeriesDataset(time=time, data=data)

        sl = ts[datetime(2001, 1, 2): datetime(2001, 1, 4)]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [2, 3, 4])

        sl = ts[: datetime(2001, 1, 2)]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [1, 2])

        sl = ts[datetime(2001, 1, 3):]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [3, 4, 5])

    def test_where_datetime(self):
        time = np.array([datetime(2001, 1, 1),
                         datetime(2001, 1, 2),
                         datetime(2001, 1, 3),
                         datetime(2001, 1, 4),
                         datetime(2001, 1, 5)])
        data = np.array([1, 2, 3, 4, 5])
        ts = TimeSeriesDataset(time=time, data=data)

        sl = ts[[1, 2, 4]]
        items = []
        for i in range(len(sl)):
            items.append(sl[i])
        self.assertEqual(items, [2, 3, 5])


class TestAverage(TestCase):
    def test_offset_aware(self):
        time = np.array([pendulum.datetime(2001, 1, 1),
                         pendulum.datetime(2001, 1, 2),
                         pendulum.datetime(2001, 1, 3),
                         pendulum.datetime(2002, 1, 1),
                         pendulum.datetime(2002, 1, 2),
                         pendulum.datetime(2002, 1, 3)])
        data = np.array([1, 2, 3, 3, 2, 1])
        ts = TimeSeriesDataset(time=time, data=data)
        ts = Average(ts)

        self.assertEqual([ts[i] for i in range(len(ts))], [2, 2])


class TestInterpolate(TestCase):
    def test(self):
        time = np.array([pendulum.datetime(2001, 1, 1),
                         pendulum.datetime(2001, 1, 2),
                         pendulum.datetime(2001, 1, 3)])
        data = np.array([1., np.nan, 3.])
        ts = TimeSeriesDataset(time=time, data=data)
        ts = Interpolate(ts)

        self.assertEqual([ts[i] for i in range(len(ts))], [1, 2, 3])


class TestAlign(TestCase):
    def test(self):
        time = np.array([pendulum.datetime(2001, 1, 1),
                         pendulum.datetime(2001, 1, 2),
                         pendulum.datetime(2001, 1, 3)])
        data = np.array([1., np.nan, 3.])
        ts = TimeSeriesDataset(time=time, data=data)
        ts = Align(ts, [pendulum.datetime(2001, 1, 1), pendulum.datetime(2001, 1, 3)])

        self.assertEqual([ts[i] for i in range(len(ts))], [1, 3])


if __name__ == '__main__':
    unittest.main()
