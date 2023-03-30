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

from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Union, Any
import pendulum

from ..base import HistoryLogger


@dataclass
class Assessor:
    """
    The container for the info on
    the people who were in charge of
    labeling process, their experience
    and other properties.

    This is a dataclass, so any additional
    fields will not be recorded if added.
    If it needs to be extended, please create
    a new class instead.
    """
    id: Union[str, None] = None
    position: Union[str, None] = None


@dataclass
class LabelingInfo:
    """
    The container for the information on labeling
    process, people involved, description of the
    process, documentation links.

    This is a dataclass, so any additional
    fields will not be recorded if added.
    If it needs to be extended, please create
    a new class instead.
    """
    who: Union[List[Assessor], None] = None
    process_desc: Union[str, None] = None
    docs: Union[str, None] = None


class DataCard:
    """
    The container for the information
    on dataset. The set of fields here
    is general and can be extended by providing
    new keywords into __init__.
    """
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
        """
        Parameters
        ----------
        name: Union[str, None], optional
            The name of dataset
        desc: Union[str, None], optional
            Short description
        source: Union[str, None], optional
            The source of data. Can be URL or textual
            description of source
        goal: Union[str, None], optional
            The datasets have a goal - what should be achieved
            using this data?
        labeling_info: Union[LabelingInfo, None], optional
            The instance of dataclass describing labeling process
            placed here
        size: Union[int, Tuple[int], None], optional
            This can usually be done automatically - number of items
            or shape of the table.
        metrics: Union[Dict[str, Any], None], optional
            Dictionary with names and values of metrics. Any quality metrics
            can be included
        schema: Union[Dict[Any, Any], None], optional
            Schema dictionary describing table datasets,
            their columns, data types, possible values, etc.
            Panderas schema objects can be used when converted into
            dictionaries
        """
        self.data = dict(
            name=name,
            desc=desc,
            source=source,
            goal=goal,
            labeling_info=asdict(labeling_info) if labeling_info is not None else labeling_info,
            size=size,
            metrics=metrics,
            schema=schema,
            **kwargs
        )


class DataRegistrator:
    """
    A tool for tracking lineage of datasets.
    I is useful if dataset is not a static object and
    has some properties changed during the time.
    """
    def __init__(self, filepath: str) -> None:
        self._logger = HistoryLogger(filepath)

    def register(
        self,
        card: DataCard
    ) -> None:
        """
        Each time this method is called - a new snapshot of
        gived card is done in the log.
        Call this method each time the dataset has changed automatically,
        for example in data update script which is preferable way or
        manually.

        Parameters
        ----------
        card: DataCard
            Container for all the info on data
            see DataCard documentation for additional info.

        See also
        --------
        cascade.meta.DataCard
        """
        now = str(pendulum.now(tz='UTC'))
        card.data['updated_at'] = now

        self._logger.log(card.data)
