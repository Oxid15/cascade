"""
Copyright 2022-2025 Ilia Moiseev

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

from typing import Any, Dict, Optional, Sequence, Tuple

from ..metric import Metric, MetricType


class Accuracy(Metric):
    """
    Accuracy metric - the number of correct answers
    divided by the number of all

    By default name is ``accuracy``, can be changed
    Direction is always up

    Can be computed iteratively using ``compute_add``
    """
    def __init__(
            self,
            value: Optional[MetricType] = None,
            name: str = "accuracy",
            dataset: Optional[str] = None,
            split: Optional[str] = None,
            interval: Optional[Tuple[MetricType, MetricType]] = None,
            extra: Optional[Dict[str, MetricType]] = None,
            **kwargs: Any
    ) -> None:
        super().__init__(name, value=value, dataset=dataset, split=split,
                         direction="up", interval=interval, extra=extra, **kwargs)
        self._running_sum = 0
        self._running_count = 0

    def compute(self, gt: Sequence[Any], pred: Sequence[Any]) -> MetricType:
        if len(gt) != len(pred):
            raise ValueError(f"Length of gt and pred should match, got {len(gt)} and {len(pred)}")
        self.value = sum([g == p for g, p in zip(gt, pred)]) / len(gt)
        return self.value

    def compute_add(self, gt: Sequence[Any], pred: Sequence[Any]) -> MetricType:
        self._running_sum += sum([g == p for g, p in zip(gt, pred)])
        self._running_count += len(gt)
        self.value = self._running_sum / self._running_count
        return self.value
