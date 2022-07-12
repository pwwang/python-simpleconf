
from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any

from .exceptions import FormatNotSupported

if TYPE_CHECKING:
    from .loaders import Loader

POOL_KEY = "_SIMPLECONF_POOL"
META_KEY = "_SIMPLECONF_META"


def config_to_ext(conf: Any) -> str:
    """Find the extension(flag) of the configuration"""
    if isinstance(conf, dict):
        return "dict"

    conf = Path(conf)
    out = conf.suffix.lstrip(".").lower()
    if not out and conf.name.lower().endswith("rc"):
        out = "rc"

    if out in ("ini", "rc", "cfg", "conf", "config"):
        return "ini"

    if out == "yml":
        return "yaml"

    return out


def get_loader(ext: str) -> "Loader":
    """Get the loader for the extension"""
    if ext == "dict":
        from .loaders.dict import DictLoader
        return DictLoader()
    if ext == "env":
        from .loaders.env import EnvLoader
        return EnvLoader()
    if ext == "ini":
        from .loaders.ini import IniLoader
        return IniLoader()
    if ext == "json":
        from .loaders.json import JsonLoader
        return JsonLoader()
    if ext == "osenv":
        from .loaders.osenv import OsenvLoader
        return OsenvLoader()
    if ext == "toml":
        from .loaders.toml import TomlLoader
        return TomlLoader()
    if ext == "yaml":
        from .loaders.yaml import YamlLoader
        return YamlLoader()

    raise FormatNotSupported(f"{ext} is not supported.")


def require_package(package: str) -> "ModuleType":
    """Require the package and return the module"""
    try:
        return import_module(package)
    except ModuleNotFoundError:
        raise ImportError(f"{package} is not installed.")
