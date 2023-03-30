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

import os
import json
import datetime
from typing import NoReturn, Union, Dict, Any
from json import JSONEncoder
import deepdiff

import yaml
import numpy as np

from . import MetaFromFile

supported_meta_formats = ('.json', '.yml', '.yaml')


class CustomEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, type):
            return str(obj)

        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()

        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                              np.int16, np.int32, np.int64, np.uint8,
                              np.uint16, np.uint32, np.uint64)):
            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, np.bool_):
            return bool(obj)

        elif isinstance(obj, np.void):
            return None

        elif isinstance(obj, deepdiff.model.PrettyOrderedSet):
            return list(obj)

        return super(CustomEncoder, self).default(obj)

    def obj_to_dict(self, obj: Any) -> Any:
        return json.loads(self.encode(obj))


class BaseHandler:
    def read(self, path: str) -> MetaFromFile:
        raise NotImplementedError()

    def write(self, path: str, obj: Any, overwrite: bool = True) -> None:
        raise NotImplementedError()

    def _raise_io_error(self, path: str, exc: Union[Exception, None] = None) -> NoReturn:
        # Any file decoding errors will be
        # prepended with filepath for user
        # to be able to identify broken file
        if exc is not None:
            raise IOError(f'Error while reading file `{path}`') from exc
        else:
            raise IOError(f'Error while reading file `{path}`')


class JSONHandler(BaseHandler):
    def read(self, path: str) -> MetaFromFile:
        _, ext = os.path.splitext(path)
        if ext == '':
            path += '.json'

        with open(path, 'r') as meta_file:
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

        with open(path, 'w') as f:
            json.dump(obj, f, cls=CustomEncoder, indent=4)


class YAMLHandler(BaseHandler):
    def read(self, path: str) -> MetaFromFile:
        _, ext = os.path.splitext(path)
        if ext == '':
            path += '.yml'

        with open(path, 'r') as meta_file:
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
        with open(path, 'w') as f:
            yaml.safe_dump(obj, f)


class TextHandler(BaseHandler):
    def read(self, path: str) -> Dict:
        """
        Reads text file from path and returns dict
        in the form {path: 'text from file'}

        Parameters
        ----------
        path: str
            Path to the file
        """

        with open(path, 'r') as meta_file:
            meta = {path: ''.join(meta_file.readlines())}
            return meta

    def write(self, path: str, obj: Any, overwrite: bool = True) -> NoReturn:
        raise NotImplementedError(
            'MetaHandler does not write text files, only reads')


class MetaHandler:
    """
    Encapsulates the logic of reading and writing metadata to disk.

    Supported read-write formats are `.json` and `.yml` or `.yaml`. Other formats
    are supported as read-only. For example one can read meta from txt or md file.

    Examples
    --------
    >>> from cascade.base import MetaHandler
    >>> mh = MetaHandler()
    >>> mh.write('meta.json', {'hello': 'world'})
    >>> obj = mh.read('meta.json')
    >>> mh.write('meta.yml', {'hello': 'world'})
    >>> obj = mh.read('meta.yml')
    """
    def read(self, path: str) -> MetaFromFile:
        """
        Reads object from path.

        Parameters
        ----------
            path: str
                Path to the object.

        Returns
        -------
            obj: MetaFromFile

        Raises
        ------
        IOError
            when decoding errors occur
        """
        handler = self._get_handler(path)
        return handler.read(path)

    def write(self, path: str, obj: Any, overwrite: bool = True) -> None:
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
        IOError
            when encoding errors occur
        """
        handler = self._get_handler(path)
        return handler.write(path, obj, overwrite=overwrite)

    def _get_handler(self, path: str) -> BaseHandler:
        ext = os.path.splitext(path)[-1]
        if ext == '.json':
            return JSONHandler()
        elif ext in ('.yml', '.yaml'):
            return YAMLHandler()
        else:
            return TextHandler()
