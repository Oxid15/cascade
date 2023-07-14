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

import glob
import os
import pickle
from hashlib import md5
from typing import Any, List, Union

from sklearn.pipeline import Pipeline

from ...base import MetaHandler, PipeMeta
from ...models import BasicModel


class SkModel(BasicModel):
    """
    Wrapper for sklearn models.
    Accepts the name and block to form pipeline.
    Can fit, evaluate, predict save and load out of the box.
    """

    def __init__(
        self, *args: Any, blocks: Union[List[Any], None] = None, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        name: str, optional
            Name of the model
        blocks: list, optional
            List of sklearn transformers to make a pipeline from
        """
        super().__init__(*args, **kwargs)

        if blocks is not None:
            self._pipeline = self._construct_pipeline(blocks)

    @staticmethod
    def _construct_pipeline(blocks: List[Any]) -> Pipeline:
        return Pipeline([(str(i), block) for i, block in enumerate(blocks)])

    def fit(self, x: Any, y: Any, *args: Any, **kwargs: Any) -> None:
        """
        Wrapper for pipeline.fit
        """
        self._pipeline.fit(x, y, *args, **kwargs)

    def predict(self, x: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper for pipeline.predict
        """
        return self._pipeline.predict(x, *args, **kwargs)

    def predict_proba(self, x: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper for pipeline.predict_proba
        """
        return self._pipeline.predict_proba(x, *args, **kwargs)

    @classmethod
    def load(cls, path: str, check_hash: bool = True) -> "SkModel":
        """
        Loads the model from path provided. Path may be a folder,
        if so, model.pkl is assumed.

        If path is the file with no extension, .pkl is added.
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            model_path = os.path.join(path, "model.pkl")
            pipeline_path = os.path.join(path, "pipeline.pkl")
        else:
            model_path = path
            pipeline_path = os.path.join(*os.path.split(path)[:-1], "pipeline.pkl")

        model_path, ext = os.path.splitext(model_path)
        if ext == "":
            ext += ".pkl"
        model_path = model_path + ext

        # TODO: enable check again later
        # if check_hash:
        #     cls._check_model_hash(model_path)

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        with open(pipeline_path, "rb") as f:
            model._pipeline = pickle.load(f)
        return model

    def save(self, path: str) -> None:
        """
        Saves model to the path provided.
        If path is a folder, then creates
        it if not exists and saves there as
        model.pkl
        If path is a file, then saves it accordingly.
        If no extension of file provided, then .pkl is added.

        The model is saved in two parts - the wrapper without pipeline
        and the actual sklearn model as pipeline separately.
        This is done for artifact portability - you can use pipeline in
        deployments directly without the need to bring additional dependency
        with the wrapper. At the same time additional params can still be loaded
        using wrapper that is saved nearby.
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            model_path = os.path.join(path, "model.pkl")
            pipeline_path = os.path.join(path, "pipeline.pkl")
        else:
            model_path = path
            pipeline_path = os.path.join(*os.path.split(path)[:-1], "pipeline.pkl")

        model_path, ext = os.path.splitext(model_path)
        if ext == "":
            ext += ".pkl"
        model_path = model_path + ext

        with open(pipeline_path, "wb") as f:
            pickle.dump(self._pipeline, f)
        pipeline = self._pipeline
        del self._pipeline
        with open(model_path, "wb") as f:
            pickle.dump(self, f)
        self._pipeline = pipeline

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({"pipeline": repr(self._pipeline)})
        return meta
