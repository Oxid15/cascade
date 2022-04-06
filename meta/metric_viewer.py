import os
import pandas as pd

from . import MetaViewer


class MetricViewer:
    """
    Interface for viewing metrics in model meta files
    uses ModelRepo to extract metrics of all models if any
    constructs a `pd.DataFrame` of metrics internally, which is showed in `__repr__`
    """
    def __init__(self, repo):
        """
        Parameters:
        -----------
        repo: ModelRepo
            ModelRepo object to extract metrics from
        """
        self.repo = repo

        self.metrics = []
        for name in self.repo.lines:
            viewer_root = os.path.join(self.repo.root, name)
            view = MetaViewer(viewer_root)

            for i in range(len(view)):
                metric = {'line': name, 'num': i}
                meta = view[i]
                if 'metrics' in meta:
                    metric.update(meta['metrics'])

                self.metrics.append(metric)
        self.table = pd.DataFrame(self.metrics)

    def __repr__(self):
        return repr(self.table)
