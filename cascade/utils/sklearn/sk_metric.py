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

from typing import Any, Dict, Optional, Tuple

from sklearn import metrics
from typing_extensions import Literal

from ...metrics import Metric, MetricType

METRIC_ALIASES = {
    "acc": "accuracy_score",
    "accuracy": "accuracy_score",
    "precision": "precision_score",
    "recall": "recall_score",
    "f1": "f1_score",
    "mse": "mean_squared_error",
    "mae": "mean_absolute_error",
}


class SkMetric(Metric):
    def __init__(
        self,
        name: str,
        *args: Any,
        value: Optional[MetricType] = None,
        dataset: Optional[str] = None,
        split: Optional[str] = None,
        direction: Optional[Literal["up", "down"]] = None,
        interval: Optional[Tuple[MetricType, MetricType]] = None,
        extra: Optional[Dict[str, MetricType]] = None,
        **kwargs: Any,
    ) -> None:
        self._args = args
        self._kwargs = kwargs
        super().__init__(
            name,
            value=value,
            dataset=dataset,
            split=split,
            direction=direction,
            interval=interval,
            extra=extra,
        )

    def compute(self, *args: Any, **kwargs: Any) -> MetricType:
        try:
            name = self.name
            if self.name in METRIC_ALIASES:
                name = METRIC_ALIASES[self.name]
            metric = getattr(metrics, name)
        except AttributeError as e:
            raise AttributeError(
                f"SkMetric accepts only names defined in module sklearn.metrics "
                f"as the list of aliases: {METRIC_ALIASES}"
            ) from e

        value = metric(*self._args, *args, **self._kwargs, **kwargs)
        self.value = value
        return value
