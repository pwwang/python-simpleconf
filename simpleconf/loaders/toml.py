from typing import Any
from simpleconf.utils import require_package
from diot import Diot

from ..caster import (
    none_caster,
    null_caster,
)
from . import Loader

rtoml = require_package("rtoml")


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

        with open(conf) as f:
            return Diot(rtoml.load(f))
