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

import inspect
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from typing_extensions import Literal

SupportedProviders = Literal["pydantic"]

TypeDict = Dict[str, Tuple[Any, Any]]


class ValidationError(Exception):
    """
    Base class to raise if data
    validation failed

    Can provide additional information about the fail
    """

    def __init__(
        self, message: Optional[str] = None, error_index: Optional[int] = None
    ) -> None:
        self.error_index = error_index

        if message is not None and self.error_index is not None:
            message = f"Error on index {self.error_index}: " + message
        super().__init__(message)


class ValidationProvider:
    def __init__(self, schema: Any) -> None:
        self._schema = schema

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()


class PydanticValidator(ValidationProvider):
    def __init__(self, schema: Any) -> None:
        super().__init__(schema)

        try:
            from pydantic import BaseModel, ValidationError
        except ImportError as e:
            raise ImportError(
                "Cannot import `pydantic` - it is optional dependency for general type checking"
            ) from e
        else:
            self._base_model_cls = BaseModel
            self._exc_type = ValidationError

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        if (
            len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], self._base_model_cls)
        ):
            try:
                self._schema.model_validate(args[0])
            except self._exc_type as e:
                raise ValidationError("Validation failed, see traceback above") from e
        else:
            from_args = dict()
            for name, arg in zip(self._schema.model_fields, args):
                from_args[name] = arg

            try:
                self._schema(**from_args, **kwargs)
            except self._exc_type as e:
                raise ValidationError("Validation failed, see traceback above") from e


class Validator:
    def __init__(self) -> None:
        self.providers = {"pydantic": PydanticValidator}
        self._validators = []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        for validator in self._validators:
            validator(*args, **kwargs)


class SchemaValidator(Validator):
    def __init__(self, schema: Any) -> None:
        super().__init__()

        name = self._resolve_validator(schema)
        self._validators.append(self.providers[name](schema))

    def _resolve_validator(self, *args: Any, **kwargs: Any) -> SupportedProviders:
        return "pydantic"


class SchemaFactory:
    @classmethod
    def build(cls, types: TypeDict, provider: SupportedProviders) -> Any:
        if provider == "pydantic":
            try:
                from pydantic import create_model
            except ImportError as e:
                raise ImportError(
                    "Cannot import ``pydantic`` - it is optional dependency"
                    " for general type checking"
                    "\nYou can install it with ``pip install 'pydantic==2.6.4'``"
                ) from e
            else:
                return create_model(
                    "pydantic_validator",
                    __config__=dict(arbitrary_types_allowed=True),
                    **types,
                )  # type: ignore


class TypesValidator(Validator):
    def __init__(self, types: TypeDict) -> None:
        super().__init__()
        provider_to_args = defaultdict(dict)
        for name in types:
            provider = self._resolve_validator(types[name][0])
            provider_to_args[provider][name] = types[name]

        for provider in provider_to_args:
            schema = SchemaFactory.build(provider_to_args[provider], provider)
            validator = self.providers[provider](schema)
            self._validators.append(validator)

    def _resolve_validator(self, type: Any) -> SupportedProviders:
        return "pydantic"


def validate_in(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Data validation decorator for callables. In each call
    validates only the input schema using type annotations
    if present. Does not check return value.

    Parameters
    ----------
    f : Callable[[Any], Any]
        Function to wrap

    Returns
    -------
    Callable[[Any], Any]
        Decorated function
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any):
        sig = inspect.signature(f)
        sig_args = {
            key: (
                (
                    sig.parameters[key].annotation
                    if sig.parameters[key].annotation is not sig.empty
                    else Any
                ),
                (
                    sig.parameters[key].default
                    if sig.parameters[key].annotation is not sig.empty
                    else ...
                ),
            )
            for key in sig.parameters
        }
        v = TypesValidator(sig_args)
        v(*args, **kwargs)
        return f(*args, **kwargs)

    return wrapper
