from typing import Any, Dict

from ..utils import require_package
from ..caster import (
    none_caster,
    null_caster,
)
from . import Loader, NoConvertingPathMixin

toml = require_package("rtoml", "tomllib", "tomli")


class TomlLoader(Loader):
    """Toml file loader"""

    CASTERS = [
        none_caster,
        null_caster,
    ]

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a toml file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return toml.loads(content)

        if not self._exists(conf, ignore_nonexist):
            return {}

        if toml.__name__ in ("tomli", "tomllib"):  # pragma: no cover
            with open(conf, "rb") as f:
                return toml.load(f)

        with open(conf, "r") as f:  # rtoml
            return toml.load(f)


class TomlsLoader(NoConvertingPathMixin, TomlLoader):
    """Toml string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from a toml file"""
        return toml.loads(conf)
