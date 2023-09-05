from dataclasses import dataclass, field
from typing import Union, Any, Literal, SupportsFloat, Tuple

import pendulum

MetricType = SupportsFloat


@dataclass
class Metric:
    """
    Base class for every metric, defines the way of computation
    and serves as the value and metadata storage
    """

    name: str
    value: Union[MetricType, None] = None
    dataset: Union[str, None] = None
    split: Union[str, None] = None
    direction: Literal["up", "down", None] = None
    interval: Union[Tuple[MetricType, MetricType], None] = None
    created_at: str = field(init=False)

    def __post_init__(self):
        self.created_at = str(pendulum.now(tz="UTC"))

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
