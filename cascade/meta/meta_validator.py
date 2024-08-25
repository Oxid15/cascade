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
from hashlib import md5
from typing import Optional

from deepdiff import DeepDiff
from typing_extensions import Literal

from ..base import Meta, MetaHandler, supported_meta_formats
from ..data.dataset import BaseDataset, T
from .validator import DataValidationException, Validator


class MetaValidator(Validator):
    """
    Standard validator that saves the dataset's meta
    on the first run and checks if it is consistent
    on the following runs.

    ``MetaValidator`` is a ``Modifier`` that checks data
    consistency in several pipeline runs. If pipeline of data
    processing consists of cascade Datasets it uses meta of all
    pipelines to ensure that data is unchanged.

    Capabilities of this validator are as powerful as pipelines meta and
    is defined by extending ``get_meta`` methods.

    Example
    -------
    >>> from cascade.data import Modifier, Wrapper
    >>> from cascade.meta import MetaValidator
    >>> ds = Wrapper([1,2,3,4])  # Define dataset
    >>> ds = Modifier(ds)  # Wrap some modifiers
    >>> ds = Modifier(ds)
    >>> MetaValidator(ds) # Add validation by passing ds, but with no assigning to use data later

    In this example on the first run validator saves meta of this pipeline, which looks
    something like this:

    >>> [{'len': 4, 'name': 'cascade.data.dataset.Modifier'},
    >>> {'len': 4, 'name': 'cascade.data.dataset.Modifier'},
    >>> {'len': 4, 'name': 'cascade.tests.number_dataset.NumberDataset'}]


    On the second run of the pipeline it computes pipeline's meta and then
    meta's hash based on the names of blocks. This is needed to check if
    pipeline structure is changed.
    If it founds that pipeline has the same structure, then meta dicts are
    compared using ``deepdiff`` and if everything is ok it returns.

    If the structure of pipeline is different it saves new meta file.

    See also
    --------
    cascade.data.Modifier
    """

    def __init__(
        self,
        dataset: BaseDataset[T],
        root: Optional[str] = None,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
    ) -> None:
        """
        Parameters
        ----------
        dataset: BaseDataset[T]
            Dataset to validate
        root: str, optional
            Path to the folder in which to store meta
            default is './.cascade'
        meta_fmt: str, optional
            Format of metadata files

        Raises
        ------
        cascade.meta.DataValidationException
        """
        super().__init__(dataset, lambda x: True)
        if root is None:
            root = "./.cascade"
            os.makedirs(root, exist_ok=True)
        self._root = root
        assert (
            meta_fmt in supported_meta_formats
        ), f"Only {supported_meta_formats} are supported formats"

        meta = self._dataset.get_meta()
        name = md5(str.encode(" ".join([m["name"] for m in meta]), "utf-8")).hexdigest()
        name += meta_fmt
        name = os.path.join(self._root, name)

        if os.path.exists(name):
            self.base_meta = self._load(name)
            self._check(meta)
        else:
            self._save(meta, name)

    def _save(self, meta: Meta, name: str) -> None:
        MetaHandler.write(name, meta)
        print(f"Saved as {name}!")

    def _load(self, name: str) -> Meta:
        return MetaHandler.read(name)

    def _check(self, query_meta: Meta) -> None:
        diff = DeepDiff(self.base_meta, query_meta, verbose_level=2)
        if len(diff):
            print(diff.pretty())
            raise DataValidationException(diff)
        else:
            print("OK!")
