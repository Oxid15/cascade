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


import warnings
from typing import Dict, Union, Any
from . import PipeMeta, MetaFromFile


class Traceable:
    """
    Base class for everything that has metadata in cascade.
    Handles the logic of getting and updating internal meta prefix.
    """
    def __init__(
        self,
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        meta_prefix: Union[Dict[Any, Any], str], optional
            The dictionary that is used to update object's meta in `get_meta` call.
            Due to the call of update can overwrite default values.
            If str - prefix assumed to be path and loaded using MetaHandler.

        See also
        --------
        cascade.base.MetaHandler
        """
        if meta_prefix is None:
            meta_prefix = {}
        elif isinstance(meta_prefix, str):
            meta_prefix = self._read_meta_from_file(meta_prefix)
        self._meta_prefix = meta_prefix

    @staticmethod
    def _read_meta_from_file(path: str) -> MetaFromFile:
        from . import MetaHandler
        return MetaHandler().read(path)

    def get_meta(self) -> PipeMeta:
        """
        Returns
        -------
        meta: PipeMeta
            A list where first element is this object's metadata.
            All other elements represent the other stages of pipeline if present.

            Meta can be anything that is worth to document about
            the object and its properties.

            Meta is a list (see PipeMeta type alias) to allow the formation of pipelines.
        """
        meta = {
            'name': repr(self)
        }
        if hasattr(self, '_meta_prefix'):
            meta.update(self._meta_prefix)
        else:
            self._warn_no_prefix()
        return [meta]

    def update_meta(self, obj: Union[Dict[Any, Any], str]) -> None:
        """
        Updates `_meta_prefix`, which then updates
        dataset's meta when `get_meta()` is called
        """
        if isinstance(obj, str):
            obj = self._read_meta_from_file(obj)

        if isinstance(obj, list):
            raise RuntimeError(
                'Object that was passed or read from path is a list.'
                'There is no clear way how to update this object\'s meta'
                'using list')

        if hasattr(self, '_meta_prefix'):
            self._meta_prefix.update(obj)
        else:
            self._warn_no_prefix()

    @staticmethod
    def _warn_no_prefix() -> None:
        warnings.warn(
            'Object doesn\'t have _meta_prefix. '
            'This may mean super().__init__() wasn\'t'
            'called somewhere'
        )
