from __future__ import annotations

import json
from typing import Any, Callable, Dict, Sequence, TypeVar
from ast import literal_eval


T = TypeVar("T", bound=Dict[str, Any])


def type_caster(prefix: str, cast_fun: Callable) -> Any:
    """Base type caster"""

    def _caster(value: str, fail_raises: bool = True) -> Any:
        """Cast value to base type"""
        if not value.startswith(prefix):
            if fail_raises:
                raise ValueError(f"Expect `@int:` prefix, got `{value}`")
            return value
        to_be_casted = value[len(prefix) :]
        try:
            return cast_fun(to_be_casted)
        except Exception:
            if fail_raises:
                raise
            return value

    return _caster


def _cast_none(value: str) -> None:
    """Cast None"""
    if value == "":
        return None

    raise ValueError(f"Expect `@none`, got `{value}`")


def _cast_bool(value: str) -> bool:
    """Cast bool"""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    raise ValueError(f"Expect `@bool:true` or `@bool:false`, got `{value}`")


def _cast_toml(value: str) -> Any:
    """Cast toml string"""
    from .utils import require_package

    toml = require_package("rtoml", "tomllib", "tomli")
    return toml.loads(value)


int_caster = type_caster("@int:", lambda x: int(float(x)))
float_caster = type_caster("@float:", float)
bool_caster = type_caster("@bool:", _cast_bool)
none_caster = type_caster("@none", _cast_none)
null_caster = type_caster("null", _cast_none)
python_caster = type_caster("@python:", literal_eval)
py_caster = type_caster("@py:", literal_eval)
json_caster = type_caster("@json:", json.loads)
toml_caster = type_caster("@toml:", _cast_toml)


def cast_value(value: Any, casters: Sequence[Callable]) -> Any:
    """Cast a single value"""
    if not isinstance(value, str):
        return value
    for caster in casters:
        try:
            return caster(value)
        except Exception:
            continue
    return value


def cast(conf: T, casters: Sequence[Callable]) -> T:
    """Cast the configuration"""
    for key, value in conf.items():
        if isinstance(value, dict):
            conf[key] = cast(value, casters)  # type: ignore[arg-type]
        else:
            conf[key] = cast_value(value, casters)
    return conf
