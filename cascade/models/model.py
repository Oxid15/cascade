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
import pendulum

from ..base import Traceable


class Model(Traceable):
    """
    Base class for any model.
    Used to provide unified interface to any model, store metadata including metrics.
    """
    def __init__(self, *args, meta_prefix=None, **kwargs) -> None:
        """
        Should be called in any successor - initializes default meta needed.
        Arguments passed in it should be related to model's hyperparameters, architecture.
        All additional arguments should have defaults - to be able to create model and then load.
        Successors may pass all of their parameters to superclass for it to be able to
        log them in meta. Everything that is worth to document about model and data it was trained on can be
        either in params or meta_prefix.
        """
        # Model accepts meta_prefix explicitly to not to record it in 'params'
        self.metrics = {}
        self.params = kwargs
        self.created_at = pendulum.now(tz='UTC')
        super().__init__(meta_prefix=meta_prefix, **kwargs)

    def fit(self, *args, **kwargs) -> None:
        """
        Method to encapsulate training loops.
        May be provided with any training-related arguments.
        """
        raise NotImplementedError()

    def predict(self, *args, **kwargs):
        """
        Method to encapsulate inference.
        May include preprocessing steps to make model self-sufficient.
        """
        raise NotImplementedError()

    def evaluate(self, *args, **kwargs) -> None:
        """
        Evaluates model against any metrics. Should not return any value, just populate self.metrics dict.
        """
        raise NotImplementedError()

    def load(self, filepath, *args, **kwargs) -> None:
        """
        Loads model from provided filepath. May be unpickling process or reading json configs.
        Does not return any model, just restores internal state.
        """
        raise NotImplementedError()

    def save(self, filepath, *args, **kwargs) -> None:
        """
        Saves model's state using provided filepath.
        """
        raise NotImplementedError()

    def get_meta(self) -> List[Dict]:
        # Successors may not call super().__init__
        # they may not have these default fields

        meta = super().get_meta()

        all_default_exist = True
        if hasattr(self, 'created_at'):
            meta[0]['created_at'] = self.created_at
        else:
            all_default_exist = False

        if hasattr(self, 'metrics'):
            meta[0]['metrics'] = self.metrics
        else:
            all_default_exist = False

        if hasattr(self, 'params'):
            meta[0]['params'] = self.params
        else:
            all_default_exist = False

        if not all_default_exist:
            warnings.warn('Model\'s meta is incomplete, maybe you haven\'t call super().__init__ in subclass?')

        meta[0]['type'] = 'model'
        return meta


class ModelModifier(Model):
    """
    Analog of dataset's Modifier. Can be used to chain
    two models in one.
    """
    def __init__(self, model: Model, **kwargs):
        """
        Parameters
        ----------
        model: Model
            A model to modify.
        """
        self._model = model
        super().__init__(**kwargs)

    def get_meta(self) -> List[Dict]:
        prev_meta = self._model.get_meta()
        return super().get_meta() + prev_meta
