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

from typing import Iterable, Any, Union, Tuple

import pendulum
from datetime import datetime
import numpy as np
import pandas as pd

from ..base import PipeMeta
from ..data import Dataset, Modifier


class TimeSeriesDataset(Dataset):
    """
    Dataset to simplify the work with time series.
    Manages the time and data. Reflects the list API
    and implements access by index and by datetime also.
    More than that, slices with indices and with datetimes can also be used.
    """
    def __init__(self, *args: Any,
                 time: Union[Iterable[datetime], None] = None,
                 data: Union[Iterable[Any], None] = None,
                 **kwargs: Any) -> None:
        """
        Parameters
        ----------
        time: Iterable[datetime], optional
            The time dimension. Should be represented subclasses of datetime
        data: Iterable, optional
            The data dimension. Should be 1D array or list.
        """
        if time is not None and data is not None:
            data = np.asarray(data)
            time = np.asarray(time)
        else:
            # The case of multiple inheritance
            # time and data can be omitted to match
            # with general signature of Dataset
            data = np.array([])
            time = np.array([])

        assert len(time) == len(data), f'Time and data should have same \
            length, got {len(time)} and {len(data)}'
        assert len(data.shape) == 1, f'series must be 1d, \
            got shape {data.shape}'
        assert all([isinstance(t, datetime) for t in time]), \
            'time elements should be instances of datetime.datetime'

        # Time can be non-monotonic (don't increase or decrease on every step)
        # check for monotonicity seems to be more expensive than sort
        index = np.argsort(time)
        time = time[index]
        data = data[index]

        self._time = time
        self._num_idx = [i for i in range(len(data))]
        index = pd.MultiIndex.from_frame(
            pd.DataFrame(self._time, self._num_idx))
        self._table = pd.DataFrame(data, index=index)
        super().__init__(*args, **kwargs)

    def to_numpy(self) -> np.ndarray:
        """
        Returns only data without time in numpy array format.

        Returns
        -------
        data: np.ndarray
            np.array of data.
        """
        return self._table.to_numpy().T[0]

    def to_pandas(self) -> pd.DataFrame:
        """
        Returns
        -------
        data: pd.DataFrame
            table with time as index
        """
        return pd.DataFrame(self.to_numpy(), index=self._time)

    def get_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns
        -------
        data: tuple
            Time and data as np.array
        """
        return self._time, self.to_numpy()

    def _get_slice(self, index: int):
        # If date slice
        if isinstance(index.start, datetime) or \
                isinstance(index.stop, datetime):

            start = np.where(self._time == index.start)[0][0] \
                if index.start is not None else None
            stop = np.where(self._time == index.stop)[0][0] \
                if index.stop is not None else None
            if stop is not None:
                stop += 1

            time = self._time[start:stop]
            data = self._table.loc[index].to_numpy().T[0]
        else:
            # If int slice
            time = self._time[index]
            data = self._table.iloc[index].to_numpy().T[0]

        return TimeSeriesDataset(time=time, data=data)

    def _get_where(self, index: Union[int, slice]):
        if isinstance(index[0], slice):
            raise NotImplementedError()

        if isinstance(index[0], datetime):
            new_time = np.array(index)
        else:
            new_time = self._time[[i for i in index]]

        new_data = np.zeros(len(index))
        for k, i in enumerate(index):
            new_data[k] = self[i]
        return TimeSeriesDataset(time=new_time, data=new_data)

    def __getitem__(self, index: Union[int, slice, datetime, Iterable[int]]):
        if isinstance(index, slice):
            if index.step is not None:
                raise NotImplementedError()
            return self._get_slice(index)
        elif isinstance(index, int):
            return self._table.iloc[index].item()
        elif isinstance(index, datetime):
            return self._table.loc[index][0].item()
        elif isinstance(index, Iterable):
            return self._get_where(index)
        else:
            raise NotImplementedError(
                f'__getitem__ is not implemented for {type(index)}'
            )

    def __len__(self) -> int:
        return len(self._num_idx)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update(
            {
                'time_from': self._time[0],
                'time_to': self._time[-1],
                'info': self._table.describe().to_dict()
            }
        )
        return meta


class Average(TimeSeriesDataset, Modifier):
    """
    Averages values over some time step.
    """
    def __init__(self, dataset: TimeSeriesDataset,
                 unit: str = 'years',
                 amount: int = 1, *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        dataset: TimeSeriesDataset,
            A dataset to average
        unit: str, optional
            Time unit over which to average - years, month, etc.
        amount:
            The amount of units over which to average. For example for six month periods use
            `unit='months'` and `amount=6`.
        """
        time, data = dataset.get_data()
        reg_time = [d for d in pendulum
                    .period(time[0], time[-1])
                    .range(unit, amount=amount)]

        reg_data = self._avg(data, time, reg_time)
        assert len(reg_data) > 1, 'Please, provide unit that ' \
                                  'would get more than one period'

        self._unit = unit
        self._amount = amount

        super().__init__(dataset, time=reg_time,
                         data=reg_data, *args, **kwargs)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update(
            {
                'unit': self._unit,
                'amount': self._amount
            }
        )
        return meta

    @staticmethod
    def _avg(arr, arr_dates, dates):
        new_p = np.zeros(len(dates))
        for i in range(len(dates) - 1):
            data = arr[(arr_dates >= dates[i]) & (arr_dates < dates[i + 1])]
            mean = np.nanmean(data)
            new_p[i] = mean
        if len(new_p) > 1:
            new_p[i + 1] = arr[(arr_dates >= dates[i + 1])].mean()  # last one
        return new_p


class Interpolate(TimeSeriesDataset, Modifier):
    """
    The wrapper around pd.Series.interpolate.
    """
    def __init__(self, dataset: TimeSeriesDataset,
                 method: str = 'linear',
                 limit_direction: str = 'both',
                 **kwargs: Any) -> None:
        t = dataset.to_pandas()
        time, _ = dataset.get_data()
        t.index = pd.Index(time)
        t = t[0].interpolate(method=method, limit_direction=limit_direction)
        super().__init__(dataset, time=time, data=t.to_numpy(), **kwargs)

        self._method = method
        self._limit_direction = limit_direction

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update(
            {
                'method': self._method,
                'limit_direction': self._limit_direction
            }
        )
        return meta


class Align(TimeSeriesDataset, Modifier):
    """
    Given dataset and some time scale selects
    data from dataset using time scale. Works
    only if dataset has data in given points
    in time.
    """
    def __init__(self, dataset: TimeSeriesDataset,
                 time: Iterable[datetime], *args: Any, **kwargs: Any) -> None:
        super().__init__(dataset, time=time,
                         data=dataset[time], *args, **kwargs)
