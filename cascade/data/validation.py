import inspect
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Literal, Tuple

SupportedProviders = Literal["pydantic"]


class ValidationError(Exception):
    pass


class ValidationProvider:
    def __init__(self, types: Dict[str, Tuple[Any, Any]]) -> None:
        self._types = types

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()


class PydanticValidator(ValidationProvider):
    def __init__(self, types: Dict[str, Tuple[Any, Any]]) -> None:
        super().__init__(types)

        try:
            from pydantic import ValidationError, create_model
        except ImportError as e:
            raise ImportError(
                "Cannot import `pydantic` - it is optional dependency for general type checking"
            ) from e
        else:
            self._exc_type = ValidationError
            self._model = create_model("pydantic_validator", **types)  # type: ignore

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        from_args = dict()
        for name, arg in zip(self._types, args):
            from_args[name] = arg

        try:
            self._model(**from_args, **kwargs)
        except self._exc_type as e:
            raise ValidationError() from e


class Validator:
    def __init__(self, types: Dict[str, Tuple[Any, Any]]) -> None:
        providers = {"pydantic": PydanticValidator}
        provider_to_args = defaultdict(dict)
        for name in types:
            provider = self._resolve_validator(types[name][0])
            provider_to_args[provider][name] = types[name]

        self._validators = []
        for name in provider_to_args:
            validator = providers[name](provider_to_args[name])
            self._validators.append(validator)

    def _resolve_validator(self, type: Any) -> SupportedProviders:
        return "pydantic"

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        for validator in self._validators:
            validator(*args, **kwargs)


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
    v = Validator(args)

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any):
        v(*args, **kwargs)
        return f(*args, **kwargs)

    return wrapper
