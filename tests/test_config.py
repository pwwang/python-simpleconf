import pytest

from simpleconf import Config, ProfileConfig


pytest_plugins = ["tests.fixt_simpleconf"]


def test_nonprofile(ini_file, dict_obj):
    config = Config.load(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    with pytest.warns(UserWarning):
        config = Config.load({"a": {"b": 2}}, ini_file)
    assert config.a == 1
    assert config.b == 2


def test_profile(ini_file, ini_file_nodefault):
    config = ProfileConfig.load(ini_file, ini_file_nodefault)

    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert ProfileConfig.has_profile(config, "default")
    assert ProfileConfig.profiles(config) == ["default", "test"]
    assert ProfileConfig.pool(config) == {
        "default": {"a": 1, "b": 2},
        "test": {"a": 6}
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
