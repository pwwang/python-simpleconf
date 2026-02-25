from panpath import PanPath
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


async def test_dict_a_loader():
    loader = get_loader("dict")

    loaded = await loader.a_load({"a": 1})
    assert loaded == loader.load({"a": 1})


def test_dicts_loader():
    loader = get_loader("dicts")

    loaded = loader.load('{"a": 1, "b": 2}')
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1, "b": 2}

    loaded = loader.load_with_profiles('{"a": 1, "b": 2}')
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1, "b": 2}


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


async def test_env_a_loader(env_file):
    loader = get_loader("env")
    loaded = await loader.a_load(env_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default_a": 1, "b": 2}

    with pytest.warns(UserWarning):
        loaded = await loader.a_load_with_profiles(env_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}}

    with pytest.raises(FileNotFoundError):
        await loader.a_load("env_file_not_exist")

    loaded = await loader.a_load("env_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_envs_loader(env_file):
    loader = get_loader("envs")
    loaded = loader.load(env_file.read_text())
    assert isinstance(loaded, Diot)
    assert loaded == {"default_a": 1, "b": 2}


def test_env_loader_file_handler(env_file):
    loader = get_loader("env")
    with open(env_file) as f:
        loaded = loader.load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"default_a": 1, "b": 2}


async def test_env_a_loader_file_handler(env_file):
    loader = get_loader("env")
    env_file = PanPath(env_file)
    async with env_file.a_open("rb") as f:
        loaded = await loader.a_load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"default_a": 1, "b": 2}


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


def test_ini_j2_loader(ini_j2_file_nondefault):
    loader = get_loader("ini.j2")
    loaded = loader.load(ini_j2_file_nondefault)
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 2, "b": 4}


async def test_ini_a_loader(ini_file_noprofile, ini_file, ini_file_nodefault):
    loader = get_loader("ini")
    loaded = await loader.a_load(ini_file_noprofile)
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

    loaded = await loader.a_load_with_profiles(ini_file_noprofile)
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
        loaded = await loader.a_load(ini_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"a": 1, "b": 2}

    with pytest.raises(ValueError, match="Only the default section"):
        await loader.a_load(ini_file_nodefault)

    with pytest.raises(FileNotFoundError):
        await loader.a_load("ini_file_not_exist")

    loaded = await loader.a_load("ini_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_ini_loader_file_handler(ini_file_noprofile):
    loader = get_loader("ini")
    with open(ini_file_noprofile) as f:
        loaded = loader.load(f)
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


async def test_ini_a_loader_file_handler(ini_file_noprofile):
    loader = get_loader("ini")
    ini_file_noprofile = PanPath(ini_file_noprofile)
    async with ini_file_noprofile.a_open("rb") as f:
        loaded = await loader.a_load(f)
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


def test_inis_loader(ini_file_noprofile):
    loader = get_loader("inis")
    loaded = loader.load(ini_file_noprofile.read_text())
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


def test_json_liq_loader(json_liq_file):
    loader = get_loader("json.liq")

    loaded = loader.load(json_liq_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 2}}


async def test_json_a_loader(json_file):
    loader = get_loader("json")

    loaded = await loader.a_load(json_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = await loader.a_load_with_profiles(json_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = await loader.a_load("json_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_jsons_loader(json_file):
    loader = get_loader("jsons")
    loaded = loader.load(json_file.read_text())
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


def test_json_loader_file_handler(json_file):
    loader = get_loader("json")
    with open(json_file) as f:
        loaded = loader.load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


async def test_json_a_loader_file_handler(json_file):
    loader = get_loader("json")
    json_file = PanPath(json_file)
    async with json_file.a_open("rb") as f:
        loaded = await loader.a_load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


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


def test_toml_liq_loader(toml_liq_file):
    loader = get_loader("toml.liq")

    loaded = loader.load(toml_liq_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 2, "b": 12}}

    loaded = loader.load_with_profiles(toml_liq_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 2, "b": 12}}

    loaded = loader.load("toml_liq_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


async def test_toml_a_loader(toml_file):
    loader = get_loader("toml")

    loaded = await loader.a_load(toml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}

    loaded = await loader.a_load_with_profiles(toml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}

    loaded = await loader.a_load("toml_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_toml_loader_file_handler(toml_file):
    loader = get_loader("toml")
    with open(toml_file) as f:
        loaded = loader.load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}


async def test_toml_a_loader_file_handler(toml_file):
    loader = get_loader("toml")
    toml_file = PanPath(toml_file)
    async with toml_file.a_open("rb") as f:
        loaded = await loader.a_load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}


def test_tomls_loader(toml_file):
    loader = get_loader("tomls")
    loaded = loader.load(toml_file.read_text())
    assert isinstance(loaded, Diot)
    assert loaded == {"b": 2, "default": {"a": 1}}


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


def test_yaml_j2_loader(yaml_j2_file):
    loader = get_loader("yaml.j2")

    loaded = loader.load(yaml_j2_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 2}, "b": 4}

    loaded = loader.load_with_profiles(yaml_j2_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 2}, "b": 4}

    loaded = loader.load("yaml_j2_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


async def test_yaml_a_loader(yaml_file):
    loader = get_loader("yaml")

    loaded = await loader.a_load(yaml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = await loader.a_load_with_profiles(yaml_file)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}

    loaded = await loader.a_load("yaml_file_not_exist", ignore_nonexist=True)
    assert loaded == {}


def test_yaml_loader_file_handler(yaml_file):
    loader = get_loader("yaml")
    with open(yaml_file) as f:
        loaded = loader.load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


async def test_yaml_a_loader_file_handler(yaml_file):
    loader = get_loader("yaml")
    yaml_file = PanPath(yaml_file)
    async with yaml_file.a_open("rb") as f:
        loaded = await loader.a_load(f)
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


def test_yamls_loader(yaml_file):
    loader = get_loader("yamls")
    loaded = loader.load(yaml_file.read_text())
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


async def test_yamls_a_loader(yaml_file):
    loader = get_loader("yamls")
    loaded = await loader.a_load(yaml_file.read_text())
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"a": 1}, "b": 2}


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


async def test_osenv_a_loader():
    envs = environ
    envs["SIMPLECONF_TEST_A"] = "1"
    envs["SIMPLECONF_TEST_DEFAULT_B"] = "2"

    loader = get_loader("osenv")
    loaded = await loader.a_load("SIMPLECONF_TEST.osenv")
    assert isinstance(loaded, Diot)
    assert loaded == {"A": "1", "DEFAULT_B": "2"}

    loaded = await loader.a_load(".osenv")
    assert isinstance(loaded, Diot)
    assert len(loaded) > 2
    assert loaded.SIMPLECONF_TEST_A == "1"
    assert loaded.SIMPLECONF_TEST_DEFAULT_B == "2"

    with pytest.warns(UserWarning, match="No profile name found"):
        loaded = await loader.a_load_with_profiles("SIMPLECONF_TEST.osenv")
    assert isinstance(loaded, Diot)
    assert loaded == {"default": {"B": "2"}}
