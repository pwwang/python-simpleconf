import sys
import pytest
from simpleconf.exceptions import FormatNotSupported
from simpleconf.utils import (
    config_to_ext,
    get_loader,
    require_package,
)

from diot import Diot


@pytest.mark.parametrize(
    "conf,ext",
    [
        ("test.ini", "ini"),
        ("test.ini.j2", "ini.j2"),
        ("test.j2.ini", "ini.j2"),
        ("test.ini.liquid", "ini.liq"),
        ("test.liq.ini", "ini.liq"),
        ("test.cfg", "ini"),
        ("test.cfg.jinja2", "ini.j2"),
        ("test.liquid.ini", "ini.liq"),
        ("test.conf", "ini"),
        ("test.config", "ini"),
        ("test.rc", "ini"),
        ("testrc", "ini"),
        ("test.json", "json"),
        ("test.toml", "toml"),
        ("test.toml.jinja", "toml.j2"),
        ("test.j2.toml", "toml.j2"),
        ("test.yaml", "yaml"),
        ("test.yml", "yaml"),
        ("test.yaml.liq", "yaml.liq"),
        ("test.j2.yml", "yaml.j2"),
        ("test.yml.liquid", "yaml.liq"),
        ("test.env", "env"),
        ("test.osenv", "osenv"),
        ({"a": 1}, "dict"),
        (Diot({"a": 1}), "dict"),
    ],
)
def test_config_to_ext(conf, ext):
    assert config_to_ext(conf) == ext


@pytest.mark.parametrize("ext", ["ini", "json", "toml", "yaml", "dict"])
def test_get_loader(ext):
    assert get_loader(ext).__class__.__name__ == f"{ext.capitalize()}Loader"


@pytest.mark.parametrize("ext", ["ini.j2", "json.j2", "toml.j2", "yaml.j2", "env.j2"])
def test_get_j2_loader(ext):
    assert (
        get_loader(ext).__class__.__name__
        == f"{ext.replace('.j2', '').capitalize()}J2Loader"
    )


@pytest.mark.parametrize(
    "ext",
    [
        "ini.liq",
        "json.liq",
        "toml.liq",
        "yaml.liq",
        "env.liq",
    ],
)
def test_get_liq_loader(ext):
    assert (
        get_loader(ext).__class__.__name__ ==
        f"{ext.replace('.liq', '').capitalize()}LiqLoader"
    )


def test_get_loader_error():
    with pytest.raises(FormatNotSupported):
        get_loader("not_supported")


def test_require_package():
    module = require_package("rtoml", "tomllib", "tomli")
    if sys.platform == "linux":
        assert module.__name__ == "rtoml"
    elif sys.version_info >= (3, 11):
        assert module.__name__ == "tomllib"
    else:
        assert module.__name__ == "tomli"

    with pytest.raises(ImportError):
        require_package("not_installed")

    # Try all fallbacks
    with pytest.raises(ImportError):
        require_package("not_installed", "not_installed2", "not_installed3")
