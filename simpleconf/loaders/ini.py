import warnings
from typing import Any
from pathlib import Path
from simpleconf.utils import require_package
from diot import Diot

from ..caster import (
    cast,
    int_caster,
    float_caster,
    bool_caster,
    none_caster,
    python_caster,
    py_caster,
    json_caster,
    toml_caster,
)
from . import Loader

iniconfig = require_package("iniconfig")


class IniLoader(Loader):
    """Ini-like file loader"""

    CASTERS = [
        int_caster,
        float_caster,
        bool_caster,
        none_caster,
        python_caster,
        py_caster,
        json_caster,
        toml_caster,
    ]

    def loading(self, conf: Any) -> dict:
        """Load the configuration from an ini-like file"""
        return iniconfig.IniConfig(conf).sections

    def load(self, conf: Any) -> "Diot":
        """Load and cast the configuration from an ini-like file"""
        sections = self.loading(conf)
        # only load the default section
        if len(sections) > 1:
            warnings.warn(
                f"{Path(conf).name}: More than one section found, "
                "only the default section will be loaded."
            )
        key = list(sections)[0]
        if key.lower() != "default":
            raise ValueError(
                f"{Path(conf).name}: Only the default section can be loaded."
            )

        return cast(Diot(sections[key]), self.__class__.CASTERS)

    def load_with_profiles(self, conf: Any) -> Diot:
        """Load and cast the configuration from an ini-like file with profiles
        """
        sections = self.loading(conf)
        out = Diot()
        for k, v in sections.items():
            out[k.lower()] = cast(v, self.__class__.CASTERS)
        return out
