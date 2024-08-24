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

import os
import pickle
from typing import Any, List, Optional

from sklearn.pipeline import Pipeline

from ...base import Meta
from ...models import BasicModel


class SkModel(BasicModel):
    """
    Wrapper for sklearn models.
    Accepts the name and block to form pipeline.
    Can fit, evaluate, predict save and load out of the box.
    """

    def __init__(
        self, *args: Any, blocks: Optional[List[Any]] = None, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        blocks: list, optional
            List of sklearn transformers to make a pipeline from
        """
        super().__init__(*args, **kwargs)

        if blocks is not None:
            self._pipeline = self._construct_pipeline(blocks)

    @staticmethod
    def _construct_pipeline(blocks: List[Any]) -> Pipeline:
        return Pipeline([(str(i), block) for i, block in enumerate(blocks)])

    def fit(self, *args: Any, **kwargs: Any) -> None:
        """
        Wrapper for pipeline.fit
        """
        self._pipeline.fit(*args, **kwargs)

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper for pipeline.predict
        """
        return self._pipeline.predict(*args, **kwargs)

    def save(self, path: str) -> None:
        """
        Saves model to the path provided.
        Path should be a folder. Creates
        it if not exists and saves there as
        model.pkl

        When saving using this method only wrapper is saved
        if you want to save sklearn model use save_artifact

        See also
        --------
        cascade.utils.sklearn.SkModel.save_artifact
        """
        super().save(path)
        model_path = os.path.join(path, "model.pkl")

        pipeline = self._pipeline
        del self._pipeline
        with open(model_path, "wb") as f:
            pickle.dump(self, f)
        self._pipeline = pipeline

    def save_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves sklearn pipeline

        Args and kwargs are passed into pickle.dump

        Parameters
        ----------
        path : str
            the folder in which to save pipeline.pkl
        """
        if not os.path.isdir(path):
            raise ValueError(f"Error when saving an artifact - {path} is not a folder")

        pipeline_path = os.path.join(path, "pipeline.pkl")
        with open(pipeline_path, "wb") as f:
            pickle.dump(self._pipeline, f, *args, **kwargs)

    def load_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Loads sklearn pipeline

        Args and kwargs are passed into pickle.load

        Parameters
        ----------
        path : str
            the folder from which to load pipeline.pkl

        Raises
        ------
        ValueError
            if the path is not a valid directory
        """
        if not os.path.isdir(path):
            raise ValueError(f"Error when loading an artifact - {path} is not a folder")

        pipeline_path = os.path.join(path, "pipeline.pkl")
        with open(pipeline_path, "rb") as f:
            self._pipeline = pickle.load(f, *args, **kwargs)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update({"pipeline": repr(self._pipeline)})
        return meta
