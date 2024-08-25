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
import warnings
from shutil import copyfile
from typing import Any, Callable, Optional, Union

import pendulum

from ..base import Meta, Traceable, raise_not_implemented
from ..data import Dataset
from ..metrics import Metric, MetricType


class Model(Traceable):
    """
    Base class for any model.
    Used to provide unified interface to any model, store metadata including metrics.
    """

    def __init__(
        self, *args: Any, meta_prefix: Union[Meta, str, None] = None, **kwargs: Any
    ) -> None:
        """
        Should be called in any successor - initializes default meta needed.

        Successors may pass all of their parameters to superclass for it to be able to
        log them in meta. Everything that is worth to document about the model
        can be put either in params or meta_prefix
        """
        self.metrics = []
        self.params = kwargs
        self.created_at = pendulum.now(tz="UTC")
        self._file_artifacts_paths = []
        self._file_artifact_missing_oks = []
        self._log_callbacks = []
        # Model accepts meta_prefix explicitly to not to record it in 'params'
        super().__init__(*args, meta_prefix=meta_prefix, **kwargs)

    def fit(self, *args: Any, **kwargs: Any) -> None:
        """
        Method to encapsulate training loops.
        May be provided with any training-related arguments.
        """
        raise_not_implemented("cascade.models.Model", "fit")

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        """
        Method to encapsulate inference.
        May include preprocessing steps to make model self-sufficient.
        """
        raise_not_implemented("cascade.models.Model", "predict")

    def evaluate(self, *args: Any, **kwargs: Any) -> None:
        """
        Evaluates model against any metrics. Should not return any value, just populate self.metrics
        """
        raise_not_implemented("cascade.models.Model", "evaluate")

    @classmethod
    def load(cls, path: str, *args: Any, **kwargs: Any) -> "Model":
        """
        Loads model from provided path
        """
        raise_not_implemented("cascade.models.Model", "load")

    def save(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Does additional saving routines. Call this if you call
        save() in any subclass.

        Creates the folder,
        copies file artifacts added by add_file
        automatically

        Parameters
        ----------
        path : str
            Path to the model folder

        Raises
        ------
        ValueError
            If the path is not a folder
        FileNotFoundError
            If the file that should be copied does not exists and
            it is not ok. See ``add_file`` for more info.

        See also
        --------
        cascade.models.Model.add_file
        """
        os.makedirs(path, exist_ok=True)

        if not hasattr(self, "_file_artifacts_paths"):
            warnings.warn(
                "Failed to perform basic Model.save since some attributes are missing"
                "maybe you haven't call super().__init__ in Model's subclass?"
            )
            return

        for filepath, but_its_ok in zip(
            self._file_artifacts_paths, self._file_artifact_missing_oks
        ):
            if not os.path.exists(filepath):
                if but_its_ok:
                    continue
                raise FileNotFoundError(
                    f"File {filepath} not found when trying to copy an artifact of model at {path}"
                )
            filename = os.path.split(filepath)[-1]

            files_folder = os.path.join(path, "files")
            os.makedirs(files_folder, exist_ok=True)

            copyfile(filepath, os.path.join(files_folder, filename))

    def load_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Loads standalone model's artifact using provided filepath and sets it inside the model
        """
        raise_not_implemented("cascade.models.Model", "load_artifact")

    def save_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves standalone model's artifact using provided filepath
        """
        raise_not_implemented("cascade.models.Model", "save_artifact")

    def get_meta(self) -> Meta:
        # Successors may not call super().__init__
        # they may not have these default fields

        meta = super().get_meta()
        meta[0]["type"] = "model"

        all_default_exist = True
        for attr in ("created_at", "metrics", "params"):
            if hasattr(self, attr):
                meta[0][attr] = self.__getattribute__(attr)
            else:
                all_default_exist = False

        if not all_default_exist:
            warnings.warn(
                "Model's meta is incomplete, "
                "maybe you haven't call super().__init__ in subclass?"
            )

        return meta

    def add_file(self, path: str, missing_ok: bool = False) -> None:
        """
        Add additional file artifact to the model
        Copy the file to the model folder when saving model.

        Parameters
        ----------
        path : str
            Path to the file to be copied. Can be
            missing at the time of the call, but should be
            present when calling save()
        missing_ok : bool, optional
            If it is okay when the file does not exist. Raises an error if False, by default False
        """
        self._file_artifacts_paths.append(path)
        self._file_artifact_missing_oks.append(missing_ok)

    def add_log_callback(self, callback: Callable[["Model"], None]) -> None:
        """
        Registers a callback to be executed
        while logging metrics. Usually is used internally
        and is not initially intended as a public method

        Parameters
        ----------
        callback : Callable[[Model], None]
            A function that accepts a model

        See also
        --------
        cascade.models.Model.log_metrics
        """
        self._log_callbacks.append(callback)

    def add_metric(
        self,
        metric: Union[str, Metric],
        value: Optional[MetricType] = None,
        **kwargs: Any,
    ) -> None:
        """
        Adds metric value to the model. If metric already exists in the list, updates its value.

        Parameters
        ----------
        metric : Union[str, Metric]
            Either metric name or metric object. If object, then second argument is ignored
        value : Optional[MetricType]
            Metric value when metric is str, by default None

        Any additional args will go to the Metric constructor for flexibility if metric is str

        Raises
        ------
        ValueError
            If in either value or metric.value is None
        TypeError
            If metric is of inappropriate type
        """
        if isinstance(metric, str):
            metric = Metric(name=metric, value=value, **kwargs)
        elif not isinstance(metric, Metric):
            raise TypeError(f"Metric can be either str or Metric type, not {type(metric)}")

        # Model be initialized not properly
        if not hasattr(self, "metrics"):
            self.metrics = []

        # Overwrites metric if it is the same, but
        # value is different
        for i, base_metric in enumerate(self.metrics):
            if metric == base_metric:
                self.metrics[i] = metric
                return

        self.metrics.append(metric)

    def link_dataset(
        self,
        ds: Dataset,
        name: Optional[str] = None,
        split: Optional[str] = None,
        line: Optional[Any] = None,
    ) -> None:
        """
        Convenience function for linking datasets. Produces more readable meta files and records
        useful info without much hassle

        Parameters
        ----------
        ds : Dataset
            Dataset to link
        name : Optional[str], optional
            Dataset name, by default None
        split : Optional[str], optional
            Split if applicable, may be "train", "test", etc, by default None
        line : Optional[DataLine], optional
            DataLine where this dataset is stored if applicable, by default None
        """
        ds_meta = ds.get_meta()
        meta = {}
        for key in ["type", "description", "tags", "comments"]:
            if ds_meta[0].get(key):
                meta[key] = ds_meta[0][key]

        if split:
            meta["split"] = split

        if line is not None:
            meta["version"] = str(line.get_version(ds))
            meta["line_root"] = line.get_root()

        self.link(name=name, meta=[meta])

    def log(self) -> None:
        """
        Sequentially calls every log callback.
        Use this if you want to make a checkpoint of a model
        from inside the model. Callback should be a function that
        given the model saves it. For example ModelLine.save method.
        ModelLine.add_model registers callback with only_meta=True automatically
        when creating a new model using ``create_model``.

        See also
        --------
        cascade.models.ModelLine.add_model
        cascade.models.Model.add_log_callback
        """
        for callback in self._log_callbacks:
            callback(self)


class ModelModifier(Model):
    """
    Analog of dataset's Modifier. Can be used to chain
    two models in one.
    """

    def __init__(self, model: Model, *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        model: Model
            A model to modify.
        """
        self._model = model
        super().__init__(*args, **kwargs)

    def get_meta(self) -> Meta:
        prev_meta = self._model.get_meta()
        return super().get_meta() + prev_meta
