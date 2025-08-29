from __future__ import annotations

import warnings
from typing import Any, Dict
from pathlib import Path
from diot import Diot

from ..utils import require_package
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
from . import Loader, NoConvertingPathMixin

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

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from an ini-like file"""
        if hasattr(conf, "read"):
            content = conf.read()
            return iniconfig.IniConfig("<config>", content).sections

        if not self._exists(conf, ignore_nonexist):
            return {"default": {}}

        return iniconfig.IniConfig(conf).sections

    def load(self, conf: Any, ignore_nonexist: bool = False) -> Diot:
        """Load and cast the configuration from an ini-like file"""
        sections = self.loading(conf, ignore_nonexist)
        keys = list(sections)

        if hasattr(conf, "read"):
            pathname = "<config>"
        else:
            pathname = Path(conf).name

        # only load the default section
        if len(keys) > 1:
            warnings.warn(
                f"{pathname}: More than one section found, "
                "only the default section will be loaded. "
                "Use ProfileConfig.load() if you want to sections as profiles."
            )

        if len(keys) == 0 or keys[0].lower() != "default":
            raise ValueError(
                f"{pathname}: Only the default section can be loaded."
            )

        return cast(Diot(sections[keys[0]]), self.__class__.CASTERS)

    def load_with_profiles(  # type: ignore[override]
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load and cast the configuration from an ini-like file with profiles"""
        sections = self.loading(conf, ignore_nonexist)
        out = Diot()
        for k, v in sections.items():
            out[k.lower()] = cast(v, self.__class__.CASTERS)
        return out


class InisLoader(NoConvertingPathMixin, IniLoader):
    """Ini-like string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from an ini-like file"""
        return iniconfig.IniConfig("<config>", conf).sections
