import pytest

from simpleconf import Config, ProfileConfig


pytest_plugins = ["tests.fixt_simpleconf"]


def test_nonprofile(ini_file, ini_file_rc, dict_obj):
    config = Config.load(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    config = Config.load_one(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    with pytest.warns(UserWarning):
        config = Config.load({"a": {"b": 2}}, ini_file)
    assert config.a == 1
    assert config.b == 2

    config = Config.load_one(ini_file_rc, loader="toml")
    assert config.DEFAULT.a == 7
    assert config.TEST.a == 9

    config = Config.load(ini_file_rc, loader="toml")
    assert config.DEFAULT.a == 7
    assert config.TEST.a == 9

    config = ProfileConfig.load(ini_file_rc, loader="toml")
    assert config.a == 7
    assert config.b == 8


def test_nonprofile_file_handler(ini_file_noprofile):
    with open(ini_file_noprofile) as f:
        config = Config.load(f, loader="ini")

    assert config.a == 10
    assert config.h is None


def test_wrong_number_of_loaders(toml_file):
    with pytest.raises(ValueError):
        Config.load(toml_file, loader=["toml", "yaml"])

    with pytest.raises(ValueError):
        ProfileConfig.load(toml_file, loader=["toml", "yaml"])


def test_no_loader_for_stream(toml_file):
    with pytest.raises(ValueError):
        with open(toml_file) as f:
            Config.load(f)

    with pytest.raises(ValueError):
        with open(toml_file) as f:
            ProfileConfig.load(f)

    with pytest.raises(ValueError):
        with open(toml_file) as f:
            ProfileConfig.load_one(f)


def test_profile(ini_file, ini_file_rc, ini_file_nodefault):
    config = ProfileConfig.load(ini_file, ini_file_nodefault)

    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert ProfileConfig.has_profile(config, "default")
    assert ProfileConfig.profiles(config) == ["default", "test"]
    assert ProfileConfig.pool(config) == {
        "default": {"a": 1, "b": 2},
        "test": {"a": 6},
    }
    assert config.a == 1
    assert config.b == 2

    newconf = ProfileConfig.use_profile(config, "test", copy=True)
    assert newconf is not config
    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert config.a == 1
    assert config.b == 2
    assert ProfileConfig.current_profile(newconf) == "test"
    assert ProfileConfig.base_profile(newconf) == "default"
    assert newconf.a == 6
    assert newconf.b == 2

    ProfileConfig.use_profile(config, "test")
    assert ProfileConfig.current_profile(config) == "test"
    assert ProfileConfig.base_profile(config) == "default"
    assert config.a == 6
    assert config.b == 2

    ProfileConfig.use_profile(config, "default")
    oldconf = config.copy()
    with ProfileConfig.with_profile(config, "test") as newconf:
        assert newconf is config
        assert ProfileConfig.current_profile(newconf) == "test"
        assert ProfileConfig.base_profile(newconf) == "default"
        assert newconf.a == 6
        assert newconf.b == 2
    assert config == oldconf

    config = ProfileConfig.load_one(ini_file_rc)
    assert config.a == "7"

    config = ProfileConfig.load_one(ini_file_rc, loader="toml")
    assert config.a == 7


def test_use_profile_base_none():
    config = ProfileConfig.load(
        {"default": {"a": 1, "b": 2}, "p1": {"a": 6}, "p2": {"a": 7}}
    )
    ProfileConfig.use_profile(config, "p1", None)
    assert config.a == 6
    assert "b" not in config

    ProfileConfig.use_profile(config, "default")
    conf2 = ProfileConfig.use_profile(config, "p2", None, copy=True)
    assert conf2.a == 7
    assert "b" not in conf2

    assert config.a == 1
    assert config.b == 2


def test_detach():
    config = ProfileConfig.load(
        {"default": {"a": 1, "b": [2, 3]}, "p1": {"a": 6}}
    )
    ProfileConfig.use_profile(config, "p1")
    diot = ProfileConfig.detach(config)
    assert diot.a == 6
    assert diot.b == [2, 3]
    assert len(diot) == 2
    diot.b[0] = 10
    assert config.b == [2, 3]
