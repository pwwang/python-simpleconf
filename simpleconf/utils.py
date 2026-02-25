from __future__ import annotations

from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import Any

from .exceptions import FormatNotSupported
from .loaders import Loader

POOL_KEY = "_SIMPLECONF_POOL"
META_KEY = "_SIMPLECONF_META"


def config_to_ext(conf: Any, secondary: bool = True) -> str:
    """Find the extension(flag) of the configuration"""
    if isinstance(conf, dict):
        return "dict"

    conf = Path(conf)
    out = conf.suffix.lstrip(".").lower()
    if out in ('j2', 'jinja2', 'jinja'):
        # x.toml.j2
        return config_to_ext(conf.stem) + '.j2'
    if out in ('liq', 'liquid'):
        # x.toml.liq
        return config_to_ext(conf.stem) + '.liq'

    if secondary:
        secondary_suffix = conf.with_suffix("").suffix.lstrip(".").lower()
        # x.j2.toml
        if secondary_suffix in ('j2', 'jinja2', 'jinja'):
            return config_to_ext(conf, secondary=False) + '.j2'
        if secondary_suffix in ('liq', 'liquid'):
            return config_to_ext(conf, secondary=False) + '.liq'

    if not out and conf.name.lower().endswith("rc"):
        out = "rc"

    if out in ("ini", "rc", "cfg", "conf", "config"):
        return "ini"

    if out == "yml":
        return "yaml"

    return out


def get_loader(ext: str | Loader) -> Loader:
    """Get the loader for the extension"""
    if isinstance(ext, Loader):
        return ext

    if ext == "dict":
        from .loaders.dict import DictLoader
        return DictLoader()

    if ext == "dicts":
        from .loaders.dict import DictsLoader
        return DictsLoader()

    if ext == "env":
        from .loaders.env import EnvLoader
        return EnvLoader()

    if ext == "env.j2":
        from .loaders.env import EnvJ2Loader
        return EnvJ2Loader()

    if ext == "env.liq":
        from .loaders.env import EnvLiqLoader
        return EnvLiqLoader()

    if ext == "envs":
        from .loaders.env import EnvsLoader
        return EnvsLoader()

    if ext == "ini":
        from .loaders.ini import IniLoader
        return IniLoader()

    if ext == "ini.j2":
        from .loaders.ini import IniJ2Loader
        return IniJ2Loader()

    if ext == "ini.liq":
        from .loaders.ini import IniLiqLoader
        return IniLiqLoader()

    if ext == "inis":
        from .loaders.ini import InisLoader
        return InisLoader()

    if ext == "json":
        from .loaders.json import JsonLoader
        return JsonLoader()

    if ext == "json.j2":
        from .loaders.json import JsonJ2Loader
        return JsonJ2Loader()

    if ext == "json.liq":
        from .loaders.json import JsonLiqLoader
        return JsonLiqLoader()

    if ext == "jsons":
        from .loaders.json import JsonsLoader
        return JsonsLoader()

    if ext == "osenv":
        from .loaders.osenv import OsenvLoader
        return OsenvLoader()

    if ext == "toml":
        from .loaders.toml import TomlLoader
        return TomlLoader()

    if ext == "toml.j2":
        from .loaders.toml import TomlJ2Loader
        return TomlJ2Loader()

    if ext == "toml.liq":
        from .loaders.toml import TomlLiqLoader
        return TomlLiqLoader()

    if ext == "tomls":
        from .loaders.toml import TomlsLoader
        return TomlsLoader()

    if ext == "yaml":
        from .loaders.yaml import YamlLoader
        return YamlLoader()

    if ext == "yaml.j2":
        from .loaders.yaml import YamlJ2Loader
        return YamlJ2Loader()

    if ext == "yaml.liq":
        from .loaders.yaml import YamlLiqLoader
        return YamlLiqLoader()

    if ext == "yamls":
        from .loaders.yaml import YamlsLoader
        return YamlsLoader()

    raise FormatNotSupported(f"{ext} is not supported.")


def require_package(package: str, *fallbacks: str) -> ModuleType:
    """Require the package and return the module"""
    try:
        return import_module(package)
    except ModuleNotFoundError:
        for fallback in fallbacks:
            try:
                return import_module(fallback)
            except ModuleNotFoundError:
                pass

        if fallbacks:
            raise ImportError(
                f"Neither '{package}' nor its fallbacks "
                f"`{', '.join(fallbacks)}` is installed."
            ) from None
        else:
            raise ImportError(f"'{package}' is not installed.") from None
