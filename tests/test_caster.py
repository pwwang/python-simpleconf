import pytest

from simpleconf.caster import (
    int_caster,
    float_caster,
    bool_caster,
    json_caster,
    toml_caster,
    python_caster,
    none_caster,
    null_caster,
    cast,
    cast_value,
)

ALL_CASTERS = [
    int_caster,
    float_caster,
    bool_caster,
    json_caster,
    toml_caster,
    python_caster,
    none_caster,
    null_caster,
]

@pytest.mark.parametrize("caster,value,fail_raises,expected", [
    (int_caster, "@int:1", True, 1),
    (int_caster, "@int:1.0", True, 1),
    (int_caster, "@int:1.1", True, 1),
    (int_caster, "@int:a", True, ValueError),
    (int_caster, "@int:a", False, "@int:a"),
    (int_caster, "@int:", True, ValueError),
    (int_caster, "1", True, ValueError),
    (int_caster, "1", False, "1"),
    (float_caster, "@float:1", True, 1.0),
    (float_caster, "@float:1.0", True, 1.0),
    (float_caster, "@float:1.1", True, 1.1),
    (float_caster, "@float:1e-1", True, 0.1),
    (float_caster, "@float:a", True, ValueError),
    (float_caster, "@float:", True, ValueError),
    (float_caster, "1", True, ValueError),
    (float_caster, "1", False, "1"),
    (bool_caster, "@bool:true", True, True),
    (bool_caster, "@bool:false", True, False),
    (bool_caster, "@bool:True", True, True),
    (bool_caster, "@bool:False", True, False),
    (bool_caster, "@bool:TRUE", True, True),
    (bool_caster, "@bool:FALSE", True, False),
    (bool_caster, "@bool:", True, ValueError),
    (bool_caster, "true", True, ValueError),
    (bool_caster, "true", False, "true"),
    (none_caster, "@none", True, None),
    (none_caster, "@none:a", True, ValueError),
    (null_caster, "null", True, None),
    (python_caster, '@python:1', True, 1),
    (json_caster, '@json:{"a": 1}', True, {"a": 1}),
    (toml_caster, '@toml:a=1', True, {"a": 1}),

])
def test_caster(caster,value,fail_raises,expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            caster(value, fail_raises)
    else:
        assert caster(value, fail_raises) == expected


@pytest.mark.parametrize("value,casters,expected", [
    ("1", ALL_CASTERS, "1"),
    (1, ALL_CASTERS, 1),
    (1.0, ALL_CASTERS, 1.0),
    (True, ALL_CASTERS, True),
    (False, ALL_CASTERS, False),
    (None, ALL_CASTERS, None),
    ({"a": 1}, ALL_CASTERS, {"a": 1}),
    ("@int:1", ALL_CASTERS, 1),
    ("@float:1", [float_caster], 1.0),
    ("@float:1", [bool_caster], "@float:1"),
])
def test_cast_value(value,casters,expected):
    assert cast_value(value, casters) == expected


@pytest.mark.parametrize("value,casters,expected", [
    ({"a": "@int:1"}, ALL_CASTERS, {"a": 1}),
    ({"a": {"b": "@int:1"}}, ALL_CASTERS, {"a": {"b": 1}}),
    ({"a": {"b": "null"}}, [null_caster], {"a": {"b": None}}),
])
def test_cast(value, casters, expected):
    assert cast(value, casters) == expected
