from dataclasses import dataclass
from typing import Union, Any, Literal, SupportsFloat, Tuple


@dataclass
class Metric:
    """
    Base class for every metric, defines the way of computation
    and serves as the value and metadata storage
    """
    name: str
    value: Union[SupportsFloat, None] = None
    dataset: Union[str, None] = None
    split: Union[str, None] = None
    direction: Literal["up", "down", None] = None
    interval: Union[Tuple[SupportsFloat, SupportsFloat], None] = None

    def compute(self, *args: Any, **kwargs: Any) -> SupportsFloat:
        """
        The method to compute metric's value. Should always populate
        the internal `self.value` field and return it.
        """
        raise NotImplementedError()

    def compute_add(self, *args: Any, **kwargs: Any) -> SupportsFloat:
        """
        The method to compute the metric incrementally.
        Should always populate the internal `self.value` field and return it.
        """
        raise NotImplementedError()
