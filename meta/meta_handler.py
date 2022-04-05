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


class MetaViewer:
    """
    The class to read and write meta data.
    """
    def __init__(self, root) -> None:
        """
        Parameters:
        -----------
        root:
            path to the folder containing meta files in .json format
            to dump and load .json files MetaHandler is used
        See also:
        ---------
        cascade.meta.ModelRepo
        cascade.meta.MetaHandler
        """
        assert os.path.exists(root)
        self.root = root
        self.mh = MetaHandler()

        names = [name for name in sorted(os.listdir(self.root)) if os.path.splitext(name)[-1] == '.json']
        self.metas = []
        for name in names:
            self.metas.append(self.mh.read(os.path.join(self.root, name)))

    def __getitem__(self, index) -> dict:
        """
        Returns:
        --------
        meta: dict
            object containing meta
        """
        return self.metas[index]

    def __len__(self) -> int:
        return len(self.metas)

    def __repr__(self) -> str:
        def pretty(d, indent=0, sep=' '):
            out = ''
            for key in d:
                if isinstance(d, dict):
                    value = d[key]
                    out += sep * indent + str(key) + ':\n'
                else:
                    value = key
                if isinstance(value, dict) or isinstance(value, list):
                    out += pretty(value, indent + 1)
                else:
                    out += sep * (indent + 1) + str(value) + sep
                    out += '\n'
            return out

        out = f'MetaViewer at {self.root}:\n'
        for i, meta in enumerate(self.metas):
            out += '-' * 20 + '\n'
            out += f'  Meta {i}:\n'
            out += '-' * 20 + '\n'
            out += pretty(meta, 4)
        return out

    def write(self, name, obj: dict) -> None:
        """
        Dumps obj to name
        """
        self.metas.append(obj)
        self.mh.write(name, obj)

    def read(self, path) -> dict:
        """
        Loads object from path
        """
        return self.mh.read(path)


class MetaHandler:
    """
    Handles the logic of dumping and loading json files
    """
    def read(self, path) -> dict:
        """
        Reads json from path

        Parameters:
        -----------
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
            enc = CustomEncoder()
            json.dump(enc.encode(obj), json_meta)
