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
# import glob
# from hashlib import md5
import pickle
from typing import Any, Dict, List
import warnings
from sklearn.pipeline import Pipeline

# from ..base import MetaHandler
from ..models import BasicModel


class SkModel(BasicModel):
    """
    Wrapper for sklearn models.
    Accepts the name and block to form pipeline.
    Can fit, evaluate, predict save and load out of the box.
    """
    def __init__(self, name=None, blocks=None, **kwargs) -> None:
        """
        Parameters
        ----------
        name: str, optional
            Name of the model
        blocks: list, optional
            List of sklearn transformers to make a pipeline from
        """
        if name is not None:
            warnings.warn('''You passed not required argument name.
            It is deprecated and will be removed in following versions''', FutureWarning)
            self.name = name
            super().__init__(name=name, **kwargs)
        else:
            super().__init__(**kwargs)

        if blocks is not None:
            self._pipeline = self._construct_pipeline(blocks)

    @staticmethod
    def _construct_pipeline(blocks: List[Any]) -> Pipeline:
        return Pipeline([(str(i), block) for i, block in enumerate(blocks)])

    def fit(self, x, y, *args, **kwargs) -> None:
        """
        Wrapper for pipeline.fit
        """
        self._pipeline.fit(x, y, *args, **kwargs)

    def predict(self, x, *args, **kwargs):
        """
        Wrapper for pipeline.predict
        """
        return self._pipeline.predict(x, *args, **kwargs)

    def predict_proba(self, x, *args, **kwargs):
        """
        Wrapper for pipeline.predict_proba
        """
        return self._pipeline.predict_proba(x, *args, **kwargs)

    # Will be added again when thoroughly tested
    # def _check_model_hash(self, meta, path_w_ext) -> None:
    #     with open(path_w_ext, 'rb') as f:
    #         file_hash = md5(f.read()).hexdigest()
    #     if file_hash == meta['md5sum']:
    #         return
    #     else:
    #         raise RuntimeError(f'.pkl model hash check failed\n \
    #              it may be that model\'s .pkl file was corrupted\n \
    #              hash from meta: {meta["md5sum"]}\n \
    #              hash from .pkl: {file_hash}')

    def load(self, path: str) -> None:
        """
        Loads the model from path provided. If no extension, .pkl is added.
        """
        if os.path.splitext(path)[-1] != '.pkl':
            path += '.pkl'
        # root = os.path.dirname(path)
        # names = glob.glob(os.path.join(f'{root}', 'meta.json'))
        # if len(names):
        #     meta = MetaHandler().read(names[0])
        #     if 'md5sum' in meta:
        #         self._check_model_hash(meta, path)

        with open(path, 'rb') as f:
            self._pipeline = pickle.load(f)

    def save(self, path: str) -> None:
        """
        Saves model to the path provided.
        If no extension, then .pkl is added.
        """
        if os.path.splitext(path)[-1] != '.pkl':
            path += '.pkl'
        with open(f'{path}', 'wb') as f:
            pickle.dump(self._pipeline, f)

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
            'pipeline': repr(self._pipeline)
        })
        return meta
