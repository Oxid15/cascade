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

import datetime
import glob
import json
import os
from dataclasses import asdict, is_dataclass
from json import JSONEncoder
from typing import Any, Dict, NoReturn, Optional

import deepdiff
import numpy as np
import yaml

from . import Meta, MetaIOError, MultipleMetaError, ZeroMetaError
from .utils import Version

default_meta_format = ".json"
supported_meta_formats = (".json", ".yml", ".yaml")

# This is for python 3.7
# where latest deepdiff is 6.7.1
if hasattr(deepdiff.diff, "PrettyOrderedSet"):
    diff_set = getattr(deepdiff.diff, "PrettyOrderedSet")
else:
    diff_set = deepdiff.diff.SetOrdered

class CustomEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, type):
            return str(obj)

        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()

        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        elif isinstance(
            obj,
            (
                np.int_,
                np.intc,
                np.intp,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
            ),  # type: ignore
        ):
            return int(obj)

        elif isinstance(obj, (np.float16, np.float32, np.float64)):  # type: ignore
            return float(obj)

        elif isinstance(obj, (np.complex64, np.complex128)):  # type: ignore
            return {"real": obj.real, "imag": obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, np.bool_):
            return bool(obj)

        elif isinstance(obj, np.void):
            return None

        elif isinstance(obj, diff_set):
            return list(obj)

        elif isinstance(obj, deepdiff.DeepDiff):
            return obj.to_dict()

        elif is_dataclass(obj):
            return asdict(obj)

        elif hasattr(obj, "to_dict"):
            return obj.to_dict()

        elif isinstance(obj, Version):
            return str(obj)

        return super(CustomEncoder, self).default(obj)

    def obj_to_dict(self, obj: Any) -> Any:
        return json.loads(self.encode(obj))


class BaseHandler:
    def read(self, path: str) -> Meta:
        raise NotImplementedError()

    def write(self, path: str, obj: Any, overwrite: bool = True) -> None:
        raise NotImplementedError()

    def _raise_io_error(self, path: str, exc: Optional[Exception] = None) -> NoReturn:
        # Any file decoding errors will be
        # prepended with filepath for user
        # to be able to identify broken file
        if exc is not None:
            raise MetaIOError(f"Error while reading file `{path}`") from exc
        else:
            raise MetaIOError(f"Error while reading file `{path}`")


class JSONHandler(BaseHandler):
    def read(self, path: str) -> Meta:
        _, ext = os.path.splitext(path)
        if ext == "":
            path += ".json"

        with open(path, "r") as meta_file:
            try:
                meta = json.load(meta_file)
                if isinstance(meta, str):
                    meta = json.loads(meta)
            except json.JSONDecodeError as e:
                self._raise_io_error(path, e)
            return meta

    def write(self, path: str, obj: Any, overwrite: bool = True) -> None:
        if not overwrite and os.path.exists(path):
            return

        with open(path, "w") as f:
            json.dump(obj, f, cls=CustomEncoder, indent=4)


class YAMLHandler(BaseHandler):
    def read(self, path: str) -> Meta:
        _, ext = os.path.splitext(path)
        if ext == "":
            path += ".yml"

        with open(path, "r") as meta_file:
            try:
                meta = yaml.safe_load(meta_file)

                # Safe load may return None if something wrong
                if meta is None:
                    self._raise_io_error(path)
            except yaml.YAMLError as e:
                self._raise_io_error(path, e)
            return meta

    def write(self, path: str, obj: Any, overwrite: bool = True) -> None:
        if not overwrite and os.path.exists(path):
            return

        obj = CustomEncoder().obj_to_dict(obj)
        with open(path, "w") as f:
            yaml.safe_dump(obj, f)


class TextHandler(BaseHandler):
    def read(self, path: str) -> Dict[str, str]:
        """
        Reads text file from path and returns dict
        in the form {path: 'text from file'}

        Parameters
        ----------
        path: str
            Path to the file
        """

        with open(path, "r") as meta_file:
            meta = {path: "".join(meta_file.readlines())}
            return meta

    def write(self, path: str, obj: Any, overwrite: bool = True) -> NoReturn:
        raise NotImplementedError("MetaHandler does not write text files, only reads")


class MetaHandler:
    """
    Encapsulates the logic of reading and writing metadata to disk.

    Supported read-write formats are ``.json`` and ``.yml`` or ``.yaml``. Other formats
    are supported as read-only. For example one can read meta from txt or md file.

    Examples
    --------
    >>> from cascade.base import MetaHandler
    >>> MetaHandler.write('meta.json', {'hello': 'world'})
    >>> obj = MetaHandler.read('meta.json')
    >>> MetaHandler.write('meta.yml', {'hello': 'world'})
    >>> obj = MetaHandler.read('meta.yml')
    """

    @classmethod
    def read(cls, path: str) -> Meta:
        """
        Reads object from path.

        Parameters
        ----------
            path: str
                Path to the object.

        Returns
        -------
            obj: Meta

        Raises
        ------
        MetaIOError
            when decoding errors occur
        """
        handler = cls._get_handler(path)
        return handler.read(path)

    @classmethod
    def write(cls, path: str, obj: Any, overwrite: bool = True) -> None:
        """
        Writes object to path.

        Parameters
        ----------
            path: str
                Path where to write object with name and extension
            obj
                An object to be serialized and saved
            overwrite: bool, optional
                Whether to overwrite the file if it already exists. If False
                and file already exists will silently return without saving.

        Raises
        ------
        MetaIOError
            when encoding errors occur
        """
        handler = cls._get_handler(path)
        return handler.write(path, obj, overwrite=overwrite)

    @classmethod
    def _get_handler(cls, path: str) -> BaseHandler:
        ext = os.path.splitext(path)[-1]
        if ext == ".json":
            return JSONHandler()
        elif ext in (".yml", ".yaml"):
            return YAMLHandler()
        else:
            return TextHandler()

    # TODO: template should cover only supported fmts
    @classmethod
    def read_dir(cls, path: str, meta_template: str = "meta.*") -> Meta:
        """
        Reads a single meta file from a given directory

        Parameters
        ----------
        path : str
            Path to a directory
        meta_template : str, optional
            The template to identify meta file, by default "meta.*"

        Returns
        -------
        Meta
            Meta

        Raises
        ------
        ZeroMetaError
            If there is no files satisfying the template in the directory provided
        MultipleMetaError
            If the number of files filtered by the template are more than 1
        """
        meta_paths = glob.glob(os.path.join(path, meta_template))
        if len(meta_paths) == 0:
            raise ZeroMetaError(f"There is no {meta_template} file in {path}")
        elif len(meta_paths) > 1:
            raise MultipleMetaError(f"There are {len(meta_paths)} in {path}")
        else:
            return cls.read(os.path.join(meta_paths[0]))

    @classmethod
    def determine_meta_fmt(cls, path: str, template: str) -> Optional[str]:
        meta_paths = glob.glob(os.path.join(path, template))
        if len(meta_paths) == 1:
            _, ext = os.path.splitext(meta_paths[0])
            return ext

    @classmethod
    def write_dir(
        cls, path: str, obj: Any, overwrite: bool = True, meta_template: str = "meta.*"
    ) -> None:
        """
        Writes meta to directory without specifying file name

        Automatically determines extension and overwrites of file exists

        Parameters
        ----------
        path : str
            Directory to write meta
        obj : Any
            Meta object
        overwrite : bool, optional
            See MetaHandler.write, by default True
        meta_template : str, optional
            The template for meta files, by default "meta.*"
        """
        ext = cls.determine_meta_fmt(path, meta_template)

        if not ext:
            ext = default_meta_format

        cls.write(os.path.join(path, "meta" + ext), obj, overwrite=overwrite)
