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

from datetime import datetime
import numpy as np
import pandas as pd

from ..data import Dataset, T


class TimeSeriesDataset(Dataset):
    def __init__(self, time, data):
        if isinstance(data, pd.DataFrame):
            data = data.to_numpy()

        assert len(data.shape) == 1    # TODO: try to release this assert?
        assert len(data) == len(time)
        
        self.time_idx = time
        self.num_idx = [i for i in range(len(data))]
        index = pd.MultiIndex.from_frame(pd.DataFrame(self.time_idx, self.num_idx))
        self.table = pd.DataFrame(data, index=index)

    def get_data(self):
        return self.time_idx, self.table.to_numpy().T[0]

    def _get_slice(self, index):
        # If date slice
        if isinstance(index.start, datetime) or isinstance(index.stop, datetime):
            start = np.where(self.time_idx == index.start)[0][0] if index.start is not None else None
            stop = np.where(self.time_idx == index.stop)[0][0] if index.stop is not None else None

            time = self.time_idx[start:stop + 1]
            data = self.table.loc[index].to_numpy().T[0]
        else:
            # If int slice
            time = self.time_idx[index]
            data = self.table.iloc[index].to_numpy().T[0]

        return TimeSeriesDataset(time, data)

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step is not None:
                raise NotImplementedError()
            return self._get_slice(index)

        elif isinstance(index, int):
            return self.table.iloc[index].item()
        elif isinstance(index, datetime):
            return self.table.loc[index][0].item()
