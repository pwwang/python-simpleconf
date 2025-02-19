import sys
import pytest
from simpleconf.exceptions import FormatNotSupported
from simpleconf.utils import (
    config_to_ext,
    get_loader,
    require_package,
)

from diot import Diot


@pytest.mark.parametrize("conf,ext", [
    ("test.ini", "ini"),
    ("test.cfg", "ini"),
    ("test.conf", "ini"),
    ("test.config", "ini"),
    ("test.rc", "ini"),
    ("testrc", "ini"),
    ("test.json", "json"),
    ("test.toml", "toml"),
    ("test.yaml", "yaml"),
    ("test.yml", "yaml"),
    ("test.env", "env"),
    ("test.osenv", "osenv"),
    ({"a": 1}, "dict"),
    (Diot({"a": 1}), "dict"),
])
def test_config_to_ext(conf, ext):
    assert config_to_ext(conf) == ext


@pytest.mark.parametrize("ext", ["ini", "json", "toml", "yaml", "dict"])
def test_get_loader(ext):
    assert get_loader(ext).__class__.__name__ == f"{ext.capitalize()}Loader"


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
