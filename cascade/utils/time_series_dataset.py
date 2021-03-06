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

from typing import Iterable

import pendulum
from datetime import datetime
import numpy as np
import pandas as pd

from ..data import Dataset, Modifier


class TimeSeriesDataset(Dataset):
    def __init__(self, *args, time=None, data=None, **kwargs):
        if time is not None and data is not None:
            data = np.asarray(data)
            time = np.asarray(time)
        else:
            # The case of multiple inheritance
            # time and data can be omitted to match with general signature of Dataset
            data = np.array([])
            time = np.array([])

        assert len(data) == len(time)
        assert len(data.shape) == 1, f'series must be 1d, got shape {data.shape}'
        assert all([isinstance(t, datetime) for t in time]), \
            'time elements should be instances of datetime.datetime'

        # Time can be non-monotonic (don't increase or decrease on every step)
        # check for monotonicity seems to be more expensive than sort
        index = np.argsort(time)
        time = time[index]
        data = data[index]

        self.time = time
        self.num_idx = [i for i in range(len(data))]
        index = pd.MultiIndex.from_frame(pd.DataFrame(self.time, self.num_idx))
        self.table = pd.DataFrame(data, index=index)
        super().__init__(*args, **kwargs)

    def to_numpy(self):
        return self.table.to_numpy().T[0]

    def to_pandas(self):
        return pd.DataFrame(self.to_numpy(), index=self.time)

    def get_data(self):
        return self.time, self.to_numpy()

    def _get_slice(self, index):
        # If date slice
        if isinstance(index.start, datetime) or isinstance(index.stop, datetime):
            start = np.where(self.time == index.start)[0][0] \
                if index.start is not None else None
            stop = np.where(self.time == index.stop)[0][0] \
                if index.stop is not None else None
            if stop is not None:
                stop += 1

            time = self.time[start:stop]
            data = self.table.loc[index].to_numpy().T[0]
        else:
            # If int slice
            time = self.time[index]
            data = self.table.iloc[index].to_numpy().T[0]

        return TimeSeriesDataset(time=time, data=data)

    def _get_where(self, index):
        if isinstance(index[0], slice):
            raise NotImplementedError()

        if isinstance(index[0], datetime):
            new_time = np.array(index)
        else:
            new_time = self.time[[i for i in index]]

        new_data = np.zeros(len(index))
        for k, i in enumerate(index):
            new_data[k] = self[i]
        return TimeSeriesDataset(time=new_time, data=new_data)

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step is not None:
                raise NotImplementedError()
            return self._get_slice(index)
        elif isinstance(index, int):
            return self.table.iloc[index].item()
        elif isinstance(index, datetime):
            return self.table.loc[index][0].item()
        elif isinstance(index, Iterable):
            return self._get_where(index)
        else:
            raise NotImplementedError(f'__getitem__ is not implemented for {type(index)}')

    def __len__(self):
        return len(self.num_idx)


class Average(TimeSeriesDataset, Modifier):
    def __init__(self, dataset: TimeSeriesDataset, unit='years', amount=1, *args, **kwargs):
        time, data = dataset.get_data()
        reg_time = [d for d in pendulum.period(time[0], time[-1]).range(unit, amount=amount)]
        reg_data = self._avg(data, time, reg_time)
        assert len(reg_data) > 1, 'Please, provide unit that would get more than one period'
        super().__init__(dataset, time=reg_time, data=reg_data, *args, **kwargs)

    def _avg(self, arr, arr_dates, dates):
        new_p = np.zeros(len(dates))
        for i in range(len(dates) - 1):
            data = arr[(arr_dates >= dates[i]) & (arr_dates < dates[i + 1])]
            mean = np.nanmean(data)
            new_p[i] = mean
        if len(new_p) > 1:
            new_p[i + 1] = arr[(arr_dates >= dates[i + 1])].mean()  # last one
        return new_p


class Interpolate(TimeSeriesDataset, Modifier):
    def __init__(self, dataset, method='linear', limit_direction='both', **kwargs):
        t = dataset.table
        t.index = pd.Index(dataset.time)
        t = t[0].interpolate(method=method, limit_direction=limit_direction)
        super().__init__(dataset, time=dataset.time, data=t.to_numpy(), **kwargs)


class Align(TimeSeriesDataset, Modifier):
    def __init__(self, dataset, time, *args, **kwargs):
        super().__init__(dataset, time=time, data=dataset[time], *args, **kwargs)
