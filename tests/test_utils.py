import sys
import pytest
from simpleconf.exceptions import FormatNotSupported
from simpleconf.utils import (
    config_to_ext,
    detect_loader_directive,
    get_loader,
    require_package,
)

from diot import Diot

pytest_plugins = ["tests.fixt_simpleconf"]


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
        get_loader(ext).__class__.__name__
        == f"{ext.replace('.liq', '').capitalize()}LiqLoader"
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


def test_detect_loader_directive_short_alias(toml_with_liq_directive):
    # "liq" alias → toml.liq
    result = detect_loader_directive(toml_with_liq_directive, "toml")
    assert result == "toml.liq"


def test_detect_loader_directive_liquid_alias(yaml_with_liquid_directive):
    # "liquid" alias → yaml.liq
    result = detect_loader_directive(yaml_with_liquid_directive, "yaml")
    assert result == "yaml.liq"


def test_detect_loader_directive_explicit(toml_with_explicit_liq_directive):
    # explicit "toml.liq" directive
    result = detect_loader_directive(toml_with_explicit_liq_directive, "toml")
    assert result == "toml.liq"


def test_detect_loader_directive_no_directive(toml_file):
    # plain toml file without directive → unchanged
    result = detect_loader_directive(toml_file, "toml")
    assert result == "toml"


def test_detect_loader_directive_dict():
    # dicts are passed through unchanged
    result = detect_loader_directive({"a": 1}, "dict")
    assert result == "dict"


def test_detect_loader_directive_nonexistent():
    # non-existent file → unchanged
    result = detect_loader_directive("/nonexistent/path/x.toml", "toml")
    assert result == "toml"


def test_detect_loader_directive_strips_existing_template_suffix(
    toml_with_liq_directive,
):
    # Even if current_ext already carries a template suffix, the directive wins
    result = detect_loader_directive(toml_with_liq_directive, "toml.j2")
    assert result == "toml.liq"


def test_detect_loader_directive_j2_alias(tmp_path):
    # "j2" alias → yaml.j2
    f = tmp_path / "config.yaml"
    f.write_text("# simpleconf-loader: j2\ndefault:\n  a: 1\n")
    result = detect_loader_directive(f, "yaml")
    assert result == "yaml.j2"


def test_detect_loader_directive_jinja_alias(tmp_path):
    # "jinja" alias → toml.j2
    f = tmp_path / "config.toml"
    f.write_text("# simpleconf-loader: jinja\nb = 1\n")
    result = detect_loader_directive(f, "toml")
    assert result == "toml.j2"


def test_detect_loader_directive_jinja2_alias(tmp_path):
    # "jinja2" alias → ini.j2
    f = tmp_path / "config.ini"
    f.write_text("# simpleconf-loader: jinja2\n[default]\na = 1\n")
    result = detect_loader_directive(f, "ini")
    assert result == "ini.j2"


def test_detect_loader_directive_read_error(tmp_path, monkeypatch):
    # When the file cannot be read, current_ext is returned unchanged
    f = tmp_path / "config.toml"
    f.write_text("# simpleconf-loader: liq\nb = 1\n")

    import pathlib

    def bad_read_text(self, *args, **kwargs):
        raise OSError("simulated read error")

    monkeypatch.setattr(pathlib.Path, "read_text", bad_read_text)
    result = detect_loader_directive(f, "toml")
    assert result == "toml"
