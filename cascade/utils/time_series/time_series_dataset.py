"""
Copyright 2022-2024 Ilia Moiseev

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

from datetime import datetime
from typing import Any, Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd

from ...base import Meta
from ...data.dataset import Dataset, T


class TimeSeriesDataset(Dataset[T]):
    """
    Dataset to simplify the work with time series.
    Manages the time and data. Reflects the list API
    and implements access by index and by datetime also.
    More than that, slices with indices and with datetimes can also be used.
    """

    def __init__(
        self,
        *args: Any,
        time: Optional[Iterable[datetime]] = None,
        data: Optional[Iterable[Any]] = None,
        **kwargs: Any,
    ) -> None:
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

        assert len(time) == len(
            data
        ), f"Time and data should have same \
            length, got {len(time)} and {len(data)}"
        assert (
            len(data.shape) == 1
        ), f"series must be 1d, \
            got shape {data.shape}"
        assert all(
            [isinstance(t, datetime) for t in time]
        ), "time elements should be instances of datetime.datetime"

        # Time can be non-monotonic (don't increase or decrease on every step)
        # check for monotonicity seems to be more expensive than sort
        index = np.argsort(time)
        time = time[index]
        data = data[index]

        self._time = time
        self._num_idx = [i for i in range(len(data))]
        index = pd.MultiIndex.from_frame(pd.DataFrame(self._time, self._num_idx))
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
        if isinstance(index.start, datetime) or isinstance(index.stop, datetime):
            start = (
                np.where(self._time == index.start)[0][0]
                if index.start is not None
                else None
            )
            stop = (
                np.where(self._time == index.stop)[0][0]
                if index.stop is not None
                else None
            )
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
                f"__getitem__ is not implemented for {type(index)}"
            )

    def __len__(self) -> int:
        return len(self._num_idx)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "time_from": self._time[0],
                "time_to": self._time[-1],
                "info": self._table.describe().to_dict(),
            }
        )
        return meta
