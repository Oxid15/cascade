from typing import Any, Dict, Sequence, Tuple, Union
from ..metric import Metric, MetricType


class Accuracy(Metric):
    """
    Accuracy metric - the number of correct answers
    divided by the number of all

    By default name is `accuracy`, can be changed
    Direction is always up

    Can be computed iteratively using `compute_add`
    """
    def __init__(
            self,
            value: Union[MetricType, None] = None,
            name: str = "accuracy",
            dataset: Union[str, None] = None,
            split: Union[str, None] = None,
            interval: Union[Tuple[MetricType, MetricType], None] = None,
            extra: Union[Dict[str, MetricType], None] = None,
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
