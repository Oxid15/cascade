"""
Copyright 2022-2024 Ilia Moiseev

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

from typing import Any, Optional

from .dataset import Dataset
from .modifier import Modifier
from .validation import SchemaValidator, ValidationError


class SchemaModifier(Modifier):
    """
    Data validation modifier

    When ``self._dataset`` is called and has
    self.in_schema defined, wraps ``self._dataset`` into
    validator, which is another ``Modifier`` that
    checks the output of ``__getitem__`` of the
    dataset that was wrapped.

    In the end it will look like this:
        If ``in_schema`` is not None:
            ``dataset = SchemaModifier(ValidationWrapper(dataset))``
        If ``in_schema`` is None:
            ``dataset = SchemaModifier(dataset)``

    How to use it:
    1. Define pydantic schema of input

    ```python
    import pydantic

    class AnnotImage(pydantic.BaseModel):
        image: List[List[List[float]]]
        segments: List[List[int]]
        bboxes: List[Tuple[int, int, int, int]]
    ```

    2. Use schema as ``in_schema``

    ```python
    from cascade.data import SchemaModifier

    class ImageModifier(SchemaModifier):
        in_schema = AnnotImage
    ```

    3. Create a regular ``Modifier`` by
    subclassing ImageModifier.

    ```python
    class IDoNothing(ImageModifier):
        def __getitem__(self, idx):
            item = self._dataset[idx]
            return item
    ```

    4. That's all. Schema check will be held
    automatically every time ``self._dataset[idx]`` is
    accessed. If it is not ``AnnotImage``, cascade.data.ValidationError
    will be raised.

    """

    in_schema: Optional[Any] = None

    def __getattribute__(self, __name: str) -> Any:
        if __name == "_dataset" and self.in_schema is not None:
            return ValidationWrapper(super().__getattribute__(__name), self.in_schema)
        if __name == "get_meta":

            def get_meta(self):
                meta = super().get_meta()
                if self.in_schema:
                    meta[0]["in_schema"] = self.in_schema.model_json_schema()
                return meta

            return lambda: get_meta(self)

        return super().__getattribute__(__name)


class ValidationWrapper(Modifier):
    def __init__(self, dataset: Dataset, schema: Any, *args: Any, **kwargs: Any) -> None:
        self.validator = SchemaValidator(schema)
        super().__init__(dataset, *args, **kwargs)

    def __getitem__(self, index: Any):
        item = super().__getitem__(index)
        try:
            self.validator(item)
        except ValidationError as e:
            raise ValidationError(
                f"Got incorrect input data from {self._dataset}",
                error_index=index
            ) from e
        return item
