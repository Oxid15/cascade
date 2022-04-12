import os
from . import MetaHandler


class MetaViewer:
    """
    The class to read and write meta data.
    """
    def __init__(self, root) -> None:
        """
        Parameters
        ----------
        root:
            path to the folder containing meta files in .json format
            to dump and load .json files MetaHandler is used
        See also
        --------
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
        Returns
        -------
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
