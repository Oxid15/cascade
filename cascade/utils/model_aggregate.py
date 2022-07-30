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

import warnings
from typing import List, Dict
import pickle
import pandas as pd
from ..models import Model


class ModelAggregate(Model):
    def __init__(self, models=None, agg_func='mean', **kwargs):
        warnings.warn('ModelAggregate will be removed in following versions', FutureWarning)
        super().__init__(**kwargs)
        self.agg_func = agg_func
        if models is None:
            self.models = []
        else:
            self.models = models

    def fit(self, *args, **kwargs):
        raise NotImplementedError()

    def predict(self, *args, **kwargs):
        raise NotImplementedError()

    def evaluate(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def load(self, filepath) -> None:
        raise NotImplementedError()

    def save(self, filepath) -> None:
        with open(filepath, 'wb') as f:
            pickle.dump(self.models, f)

    def get_meta(self) -> List[Dict]:
        metas = []

        for model in self.models:
            metas += model.get_meta()
        meta_table = pd.DataFrame(metas)

        agg_meta = {}

        # Very application-specific ugly code that just works...
        # TODO: refactor this
        for col in meta_table.columns:
            col_type = type(meta_table[col].iloc[0])
            if col_type == str:
                agg_meta[col] = meta_table[col].iloc[0]
            elif col_type == dict:
                agg_meta[col] = {}
                for key in meta_table[col].iloc[0].keys():
                    key_type = type(meta_table[col].iloc[0][key])
                    if key_type == str or key_type == list:
                        agg_meta[col][key] = pd.DataFrame.from_dict(meta_table[col].to_list()).iloc[0][key]
                    else:
                        agg_meta[col][key] = pd.DataFrame.from_dict(meta_table[col].to_list()).agg(self.agg_func).to_dict()
            elif col_type == pd.Timestamp:
                agg_meta[col] = pd.DataFrame.from_dict(meta_table[col].apply(lambda x: x.to_pydatetime()).to_list()).agg(self.agg_func).to_dict()
            else:
                raise NotImplementedError()

        return [agg_meta]
