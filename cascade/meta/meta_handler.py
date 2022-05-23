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
import json
import datetime
from json import JSONEncoder

import numpy as np


class CustomEncoder(JSONEncoder):
    def default(self, obj):
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

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)):
            return None

        return super(CustomEncoder, self).default(obj)


class MetaHandler:
    """
    Handles the logic of dumping and loading json files
    """
    def read(self, path) -> dict:
        """
        Reads json from path

        Parameters
        ----------
        path:
            Path to the file. If no extension provided, then .json assumed
        """
        assert os.path.exists(path)
        _, ext = os.path.splitext(path)
        if ext == '':
            path += '.json'

        with open(path, 'r') as meta_file:
            meta = json.load(meta_file)
            if isinstance(meta, str):
                meta = json.loads(meta)
            return meta

    def write(self, name, obj) -> None:
        """
        Writes json to path using custom encoder
        """
        with open(name, 'w') as json_meta:
            # enc = CustomEncoder()
            json.dump(obj, json_meta, cls=CustomEncoder)
