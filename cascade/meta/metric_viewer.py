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
import pandas as pd

from . import MetaViewer


class MetricViewer:
    """
    Interface for viewing metrics in model meta files
    uses ModelRepo to extract metrics of all models if any
    constructs a `pd.DataFrame` of metrics internally, which is showed in `__repr__`
    """
    def __init__(self, repo) -> None:
        """
        Parameters
        ----------
        repo: ModelRepo
            ModelRepo object to extract metrics from
        """
        self.repo = repo

        self.metrics = []
        for name in self.repo.lines:
            line = self.repo[name]
            viewer_root = os.path.join(self.repo.root, name)

            for i, model_name in enumerate(line.model_names):
                view = MetaViewer(os.path.join(viewer_root, os.path.dirname(model_name)))
                metric = {'line': name, 'num': i}
                meta = view[0][-1]

                if 'metrics' in meta:
                    metric.update(meta['metrics'])
                if 'params' in meta:
                    metric.update(meta['params'])

                self.metrics.append(metric)
        self.table = pd.DataFrame(self.metrics)

    def __repr__(self) -> str:
        return repr(self.table)
