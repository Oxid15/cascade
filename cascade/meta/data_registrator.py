import os
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Union, Any
import pendulum

from ..base import MetaHandler


@dataclass
class Assessor:
    id: Union[str, None] = None
    position: Union[str, None] = None


@dataclass
class LabelingInfo:
    who: Union[List[Assessor], None] = None
    process_desc: Union[str, None] = None
    docs: Union[str, None] = None


class DataCard:
    def __init__(
        self,
        name: Union[str, None] = None,
        desc: Union[str, None] = None,
        source: Union[str, None] = None,
        goal: Union[str, None] = None,
        labeling_info: Union[LabelingInfo, None] = None,
        size: Union[int, Tuple[int], None] = None,
        metrics: Union[Dict[str, Any], None] = None,
        schema: Union[Dict[Any, Any], None] = None,
        **kwargs: Any
    ) -> None:

        self.data = dict(
            name=name,
            desc=desc,
            source=source,
            goal=goal,
            labeling_info=asdict(labeling_info),
            size=size,
            metrics=metrics,
            schema=schema,
            **kwargs
        )


class DataRegistrator:
    def __init__(self, path: str) -> None:
        self._path = path
        self._mh = MetaHandler()

        if os.path.exists(path):
            try:
                self._meta_log = self._mh.read(path)
            except IOError as e:
                raise IOError(f'Failed to read log file: {path}') from e
        else:
            self._meta_log = {}

    def register(
        self,
        card: DataCard,
        **kwargs: Any
    ) -> None:
        now = str(pendulum.now(tz='UTC'))

        self._meta_log[now] = {**kwargs}
        self._meta_log[now].update(card.data)

        try:
            self._mh.write(self._path, self._meta_log)
        except IOError as e:
            raise IOError(f'Failed to read log file: {self._path}') from e
