import inspect
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Literal, Tuple, Union

SupportedProviders = Literal["pydantic"]

TypeDict = Dict[str, Tuple[Any, Any]]


class ValidationError(Exception):
    pass


class ValidationProvider:
    def __init__(self, schema: Any) -> None:
        self._schema = schema

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()


class PydanticValidator(ValidationProvider):
    def __init__(self, schema: Any) -> None:
        super().__init__(schema)

        try:
            from pydantic import ValidationError
        except ImportError as e:
            raise ImportError(
                "Cannot import `pydantic` - it is optional dependency for general type checking"
            ) from e
        else:
            self._exc_type = ValidationError

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        from_args = dict()
        for name, arg in zip(self._schema.model_fields, args):
            from_args[name] = arg

        try:
            self._schema(**from_args, **kwargs)
        except self._exc_type as e:
            raise ValidationError() from e


class Validator:
    providers = {"pydantic": PydanticValidator}
    _validators = []

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        for validator in self._validators:
            validator(*args, **kwargs)


class SchemaValidator(Validator):
    def __init__(self, schema: Any) -> None:
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
                    "Cannot import `pydantic` - it is optional dependency for general type checking"
                ) from e
            else:
                return create_model("pydantic_validator", **types)  # type: ignore


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
    sig = inspect.signature(f)
    args = {
        key: (
            (
                sig.parameters[key].annotation
                if sig.parameters[key].annotation is not sig.empty
                else Any
            ),
            sig.parameters[key].default if sig.parameters[key].annotation is not sig.empty else ...,
        )
        for key in sig.parameters
    }
    v = TypesValidator(args)

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any):
        v(*args, **kwargs)
        return f(*args, **kwargs)

    return wrapper
