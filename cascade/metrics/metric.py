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
        """
        Creates Metric

        Parameters
        ----------
        name : str
            Name of the metric
        value : Union[MetricType, None], optional
            Scalar value of the metric, by default None
        dataset : Union[str, None], optional
            Dataset on which metric was computed, by default None
        split : Union[str, None], optional
            The split of the dataset for example train or test, by default None
        direction : Literal["up", "down", None], optional
            Is metric better when it is greater or less, by default None
        interval : Union[Tuple[MetricType, MetricType], None], optional
            Upper and lower boundaries of value, by default None
        extra : Union[Dict[str, MetricType], None], optional
            Extra values that needs to be stored with metric, by default None
        """
        self.name = name
        self.value = value
        self.dataset = dataset
        self.split = split
        self.direction = direction
        self.interval = interval
        self.created_at = pendulum.now(tz="UTC")
        self.extra = extra

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
        """
        Converts metric object into dict, omits fields that are None

        Returns
        -------
        Dict[str, Any]
        """
        keys = [
            "name",
            "value",
            "dataset",
            "split",
            "direction",
            "interval",
            "created_at",
            "extra",
        ]
        d = {key: getattr(self, key) for key in keys if getattr(self, key) is not None}
        return d

    def __repr__(self) -> str:
        s = f"{type(self).__name__}("
        info = self.to_dict()

        formatted = []
        for field in info:
            if info[field] is not None:
                formatted.append(f"{field}={info[field]}")
        s += ", ".join(formatted)
        s += ")"
        return s


class Loss(Metric):
    """
    Loss is the convenience metric
    which by default has name "loss"
    and is always directed down
    """
    def __init__(
        self,
        value: Union[MetricType, None] = None,
        name: str = "loss",
        dataset: Union[str, None] = None,
        split: Union[str, None] = None,
        **kwargs: Any
    ) -> None:
        """
        See also
        --------
        cascade.metrics.Metric
        """
        super().__init__(
            name=name,
            direction="down",
            value=value,
            dataset=dataset,
            split=split,
            **kwargs
        )
