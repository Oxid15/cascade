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

from ..base import MetaHandler, PipeMeta
from ..models import BasicModel


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
    def _check_model_hash(cls, path: str) -> None:
        root = os.path.dirname(path)
        names = glob.glob(os.path.join(f"{root}", "meta.*"))
        if len(names) == 1:
            meta = MetaHandler.read(names[0])
            # Uses first meta in list
            # Usually the list is of unit length
            meta = meta[0]
            if "md5sum" in meta:
                with open(path, "rb") as f:
                    file_hash = md5(f.read()).hexdigest()
                if file_hash != meta["md5sum"]:
                    raise RuntimeError(
                        f".pkl model hash check failed "
                        f"it may be that model's .pkl file was corrupted\n"
                        f'hash from {names[0]}: {meta["md5sum"]}\n'
                        f"hash of {path}: {file_hash}"
                    )
        elif len(names) > 1:
            raise RuntimeError(f"Multiple possible meta-files found: {names}")

    @classmethod
    def load(cls, path: str, check_hash: bool = True) -> "SkModel":
        """
        Loads the model from path provided. Path may be a folder,
        if so, model.pkl is assumed.

        If path is the file with no extension, .pkl is added.
        """
        if os.path.isdir(path):
            path = os.path.join(path, "model.pkl")

        path, ext = os.path.splitext(path)
        if ext == "":
            ext += ".pkl"

        path = path + ext

        if check_hash:
            cls._check_model_hash(path)

        with open(path, "rb") as f:
            model = pickle.load(f)

        return model

    def save(self, path: str) -> None:
        """
        Saves model to the path provided.
        If path is a folder, then creates
        it if not exists and saves there as
        model.pkl
        If path is a file, then saves it accordingly.
        If no extension of file provided, then .pkl is added.
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            path = os.path.join(path, "model.pkl")

        path, ext = os.path.splitext(path)
        if ext == "":
            ext += ".pkl"

        path = path + ext

        with open(f"{path}", "wb") as f:
            pickle.dump(self.__dict__, f)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({"pipeline": repr(self._pipeline)})
        return meta
