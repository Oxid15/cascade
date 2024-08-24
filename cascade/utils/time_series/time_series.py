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
from typing import Any, Iterable

import numpy as np
import pandas as pd
import pendulum

from ...base import Meta
from ...data import Modifier
from .time_series_dataset import TimeSeriesDataset


class Average(TimeSeriesDataset, Modifier):
    """
    Averages values over some time step.
    """

    def __init__(
        self,
        dataset: TimeSeriesDataset,
        unit: str = "years",
        amount: int = 1,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        dataset: TimeSeriesDataset,
            A dataset to average
        unit: str, optional
            Time unit over which to average - years, month, etc.
        amount:
            The amount of units over which to average. For example for six month periods use
            ``unit='months'`` and ``amount=6``.
        """
        time, data = dataset.get_data()
        try:
            # This is pendulum 2.x
            reg_time = [
                d for d in pendulum.period(time[0], time[-1]).range(unit, amount=amount)
            ]
        except AttributeError:
            # If it doesn't work then try pendulum 3.x
            reg_time = [
                d for d in pendulum.interval(time[0], time[-1]).range(unit, amount=amount)
            ]

        reg_data = self._avg(data, time, reg_time)
        assert len(reg_data) > 1, (
            "Please, provide unit that " "would get more than one period"
        )

        self._unit = unit
        self._amount = amount

        super().__init__(dataset, time=reg_time, data=reg_data, *args, **kwargs)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update({"unit": self._unit, "amount": self._amount})
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

    def __init__(
        self,
        dataset: TimeSeriesDataset,
        method: str = "linear",
        limit_direction: str = "both",
        **kwargs: Any,
    ) -> None:
        t = dataset.to_pandas()
        time, _ = dataset.get_data()
        t.index = pd.Index(time)
        t = t[0].interpolate(method=method, limit_direction=limit_direction)
        super().__init__(dataset, time=time, data=t.to_numpy(), **kwargs)

        self._method = method
        self._limit_direction = limit_direction

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {"method": self._method, "limit_direction": self._limit_direction}
        )
        return meta


class Align(TimeSeriesDataset, Modifier):
    """
    Given dataset and some time scale selects
    data from dataset using time scale. Works
    only if dataset has data in given points
    in time.
    """

    def __init__(
        self,
        dataset: TimeSeriesDataset,
        time: Iterable[datetime],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(dataset, time=time, data=dataset[time], *args, **kwargs)
