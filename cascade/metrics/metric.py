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

from typing import Union, Any, Literal, SupportsFloat, Tuple, Dict

import pendulum

MetricType = SupportsFloat


class Metric:
    """
    Base class for every metric, defines the way of computation
    and serves as the value and metadata storage

    Metrics should always be scalar. If your metric returns some
    complex types like dicts or lists consider using multiple
    Metric objects. Or if values are connected, use extra keyword.
    """

    def __init__(
        self,
        name: str,
        *args: None,
        value: Union[MetricType, None] = None,
        dataset: Union[str, None] = None,
        split: Union[str, None] = None,
        direction: Literal["up", "down", None] = None,
        interval: Union[Tuple[MetricType, MetricType], None] = None,
        extra: Union[Dict[str, MetricType], None] = None,
        **kwargs: Any
    ) -> None:
        self.name = name
        self.value = value
        self.dataset = dataset
        self.split = split
        self.direction = direction
        self.interval = interval
        self.created_at = pendulum.now(tz="UTC")
        self.extra = extra

        super().__init__(*args, **kwargs)

    def compute(self, *args: Any, **kwargs: Any) -> MetricType:
        """
        The method to compute metric's value. Should always populate
        the internal `self.value` field and return it.
        """
        raise NotImplementedError()

    def compute_add(self, *args: Any, **kwargs: Any) -> MetricType:
        """
        The method to compute the metric incrementally.
        Should always populate the internal `self.value` field and return it.
        """
        raise NotImplementedError()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Metric):
            # Compare all fields without `value` and `created_at`
            if (
                __value.name == self.name
                and __value.dataset == self.dataset
                and __value.split == self.split
                and __value.direction == self.direction
                and __value.interval == self.interval
            ):
                return True
            return False
        return NotImplemented

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "dataset": self.dataset,
            "split": self.split,
            "direction": self.direction,
            "interval": self.interval,
            "created_at": self.created_at,
            "extra": self.extra,
        }
