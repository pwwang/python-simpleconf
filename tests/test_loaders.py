import pytest

from os import environ
from diot import Diot
from simpleconf.utils import get_loader
from simpleconf.loaders.dict import DictLoader

pytest_plugins = ["tests.fixt_simpleconf"]


def test_dict_loader():
    loader = get_loader("dict")

    loaded = loader.load({"a": 1})
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1}

    loaded = loader.load_with_profiles({"a": 1})
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1}


def test_direct_loader():
    loader = get_loader(DictLoader())

    loaded = loader.load({"a": 1})
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1}

    loaded = loader.load_with_profiles({"a": 1})
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1}


def test_env_loader(env_file):
    loader = get_loader("env")
    loaded = loader.load(env_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default_a": 1, "b": 2}

    with pytest.warns(UserWarning):
        loaded = loader.load_with_profiles(env_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}}

    with pytest.raises(FileNotFoundError):
        loader.load("env_file_not_exist")

    loaded = loader.load("env_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_ini_loader(ini_file_noprofile, ini_file, ini_file_nodefault):
    loader = get_loader("ini")
    loaded = loader.load(ini_file_noprofile)
    assert isinstance(loaded, Diot)
    assert loaded == {
        "a": 10,
        "b": "11",
        "c": "x:y",
        "d": 12,
        "e": 13.1,
        "f": True,
        "g": "csv:a,b,c",
        "h": None,
        "i": 1e-3,
        "j": "true",
        "k": "k",
    }

    loaded = loader.load_with_profiles(ini_file_noprofile)
    assert isinstance(loaded, Diot)
    assert loaded == {
        "default": {
            "a": 10,
            "b": "11",
            "c": "x:y",
            "d": 12,
            "e": 13.1,
            "f": True,
            "g": "csv:a,b,c",
            "h": None,
            "i": 1e-3,
            "j": "true",
            "k": "k",
        }
    }

    with pytest.warns(UserWarning, match="More than one section found"):
        loaded = loader.load(ini_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1, "b": 2}

    with pytest.raises(ValueError, match="Only the default section"):
        loader.load(ini_file_nodefault)

    with pytest.raises(FileNotFoundError):
        loader.load("ini_file_not_exist")

    loaded = loader.load("ini_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_json_loader(json_file):
    loader = get_loader("json")

    loaded = loader.load(json_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = loader.load_with_profiles(json_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = loader.load("json_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_toml_loader(toml_file):
    loader = get_loader("toml")

    loaded = loader.load(toml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}

    loaded = loader.load_with_profiles(toml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}

    loaded = loader.load("toml_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_yaml_loader(yaml_file):
    loader = get_loader("yaml")

    loaded = loader.load(yaml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = loader.load_with_profiles(yaml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = loader.load("yaml_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_osenv_loader():
    envs = environ
    envs["SIMPLECONF_TEST_A"] = "1"
    envs["SIMPLECONF_TEST_DEFAULT_B"] = "2"

    loader = get_loader("osenv")
    loaded = loader.load("SIMPLECONF_TEST.osenv")
    assert isinstance(loaded, Diot)
    assert loaded == {"A": "1", "DEFAULT_B": "2"}

    loaded = loader.load(".osenv")
    assert isinstance(loaded, Diot)
    assert len(loaded) > 2
    assert loaded.SIMPLECONF_TEST_A == "1"
    assert loaded.SIMPLECONF_TEST_DEFAULT_B == "2"

    with pytest.warns(UserWarning, match="No profile name found"):
        loaded = loader.load_with_profiles("SIMPLECONF_TEST.osenv")
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"B": "2"}}
