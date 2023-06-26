from typing import Any
from simpleconf.utils import require_package
from diot import Diot

from ..caster import (
    none_caster,
    null_caster,
)
from . import Loader

toml = require_package("rtoml", "tomllib", "tomli")


class TomlLoader(Loader):
    """Toml file loader"""

    CASTERS = [
        none_caster,
        null_caster,
    ]

    def loading(self, conf: Any, ignore_nonexist: bool) -> Diot:
        """Load the configuration from a toml file"""
        if not self._exists(conf, ignore_nonexist):
            return Diot()

        if toml.__name__ in ("tomli", "tomllib"):  # pragma: no cover
            with open(conf, "rb") as f:
                return Diot(toml.load(f))

        with open(conf, "r") as f:
            return Diot(toml.load(f))
