from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


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

    id: Optional[str] = None
    position: Optional[str] = None


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

    who: Optional[List[Assessor]] = None
    process_desc: Optional[str] = None
    docs: Optional[str] = None


class DataCard:
    """
    The container for the information
    on dataset. The set of fields here
    is general and can be extended by providing
    new keywords into __init__.

    Example
    -------
    >>> from cascade.data import DataCard, Assessor, LabelingInfo, DataRegistrator
    >>> person = Assessor(id=0, position="Assessor")
    >>> info = LabelingInfo(who=[person], process_desc="Labeling description")
    >>> dc = DataCard(
    ...     name="Dataset",
    ...     desc="Example dataset",
    ...     source="Database",
    ...     goal="Every dataset should have a goal",
    ...     labeling_info=info,
    ...     size=100,
    ...     metrics={"quality": 100},
    ...     schema={"label": "value"},
    ...     custom_field="hello")
    >>> dr = DataRegistrator('data_log.yml')
    >>> dr.register(dc)
    """

    def __init__(
        self,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        source: Optional[str] = None,
        goal: Optional[str] = None,
        labeling_info: Optional[LabelingInfo] = None,
        size: Union[int, Tuple[int], None] = None,
        metrics: Optional[Dict[str, Any]] = None,
        schema: Optional[Dict[Any, Any]] = None,
        **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        name: Optional[str]
            The name of dataset
        desc: Optional[str]
            Short description
        source: Optional[str]
            The source of data. Can be URL or textual
            description of source
        goal: Optional[str]
            The datasets have a goal - what should be achieved
            using this data?
        labeling_info: Optional[LabelingInfo]
            The instance of dataclass describing labeling process
            placed here
        size: Union[int, Tuple[int], None]
            This can usually be done automatically - number of items
            or shape of the table.
        metrics: Optional[Dict[str, Any]]
            Dictionary with names and values of metrics. Any quality metrics
            can be included
        schema: Optional[Dict[Any, Any]]
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
            labeling_info=asdict(labeling_info)
            if labeling_info is not None
            else labeling_info,
            size=size,
            metrics=metrics,
            schema=schema,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        return self.data
