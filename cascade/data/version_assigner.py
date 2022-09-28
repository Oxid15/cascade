import os
from hashlib import md5
from typing import Dict, List
from . import Dataset, Modifier
from ..base import MetaHandler, supported_meta_formats


class VersionAssigner(Modifier):
    def __init__(self, dataset: Dataset, path, *args, **kwargs) -> None:
        super().__init__(dataset, *args, **kwargs)
        self._mh = MetaHandler()
        self._assign_path(path)   

        self._versions = {}
        meta = self._dataset.get_meta()

        meta_str = str(meta)
        pipeline = ' '.join([m['name'] for m in meta])

        meta_hash = md5(str.encode(meta_str, 'utf-8')).hexdigest()
        pipe_hash = md5(str.encode(pipeline, 'utf-8')).hexdigest()
        if os.path.exists(self._root):
            self._versions = self._mh.read(self._root)    

            if pipe_hash in self._versions:
                if meta_hash in self._versions[pipe_hash]:
                    self.version = self._versions[pipe_hash][meta_hash]
                else:
                    last_ver = self._get_last_version_from_pipe(pipe_hash)
                    major, minor = self._split_ver(last_ver)
                    minor += 1
                    self.version = self._join_ver(major, minor)
                    self._versions[pipe_hash][meta_hash] = self.version
            else:
                last_ver = self._get_last_version()
                major, minor = self._split_ver(last_ver)
                major += 1
                self.version = self._join_ver(major, minor)
                self._versions[pipe_hash] = {meta_hash: self.version}

            self._mh.write(self._root, self._versions)
        else:
            self.version = '0.0'
            self._versions[pipe_hash] = {meta_hash: self.version}
            self._mh.write(self._root, self._versions)

    def _assign_path(self, path):
        _, ext = os.path.splitext(path)
        if ext == '':
            raise ValueError(f'Provided path {path} has no extension')

        assert ext in supported_meta_formats, f'Only {supported_meta_formats} are supported formats'
        self._root = path

    def _split_ver(self, ver):
        major, minor = ver.split('.')
        return int(major), int(minor)

    def _join_ver(self, major, minor):
        return f'{major}.{minor}'

    def _get_last_version_from_pipe(self, pipe_hash):
        versions = self._versions[pipe_hash].values()
        versions = sorted(versions)
        return versions[-1]

    def _get_last_version(self):
        versions_flat = []
        for pipe_hash in self._versions:
            versions_flat += self._versions[pipe_hash].values()
        versions = sorted(versions_flat)
        return versions[-1]

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0]['version'] = self.version
        return meta
