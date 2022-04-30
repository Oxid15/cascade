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
            data = np.array([])
            time = np.array([])

        assert len(data) == len(time)
        assert len(data.shape) == 1, f'series must be 1d, got shape {data.shape}'
        assert all([isinstance(t, datetime) for t in time]), \
            'time elements should be of type datetime.datetime'

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
