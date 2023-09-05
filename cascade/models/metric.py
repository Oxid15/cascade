from dataclasses import dataclass
from typing import Union, Any, Literal, SupportsFloat, Tuple, Callable


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


class FnMetric(Metric):
    def __init__(self, fn: Callable[[Any], MetricType], *args: Any, **kwargs: Any) -> None:
        """
        See cascade.models.Metric
        """
        super().__init__(*args, name=fn.__name__, **kwargs)
        self.compute = fn
