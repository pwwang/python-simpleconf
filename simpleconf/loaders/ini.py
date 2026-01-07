from __future__ import annotations

import warnings
from typing import Any, Awaitable, Dict
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

        conf = self.__class__._convert_path(conf)
        content = conf.read_text()

        return iniconfig.IniConfig(conf, content).sections

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from an ini-like file"""
        if hasattr(conf, "read"):
            content = conf.read()
            if isinstance(content, Awaitable):
                content = await content
            if isinstance(content, bytes):
                content = content.decode()
            return iniconfig.IniConfig("<config>", content).sections

        if not await self._a_exists(conf, ignore_nonexist):
            return {"default": {}}

        conf = self.__class__._convert_path(conf)
        content = await conf.a_read_text()

        return iniconfig.IniConfig(conf, content).sections

    @classmethod
    def _convert(  # type: ignore[override]
        cls,
        conf: Any,
        loaded: Dict[str, Any],
    ) -> Diot:
        keys = list(loaded)

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
            raise ValueError(f"{pathname}: Only the default section can be loaded.")

        return cast(Diot(loaded[keys[0]]), cls.CASTERS)

    @classmethod
    def _convert_with_profiles(  # type: ignore[override]
        cls,
        conf: Any,
        loaded: Dict[str, Any],
    ) -> Diot:
        out = Diot()
        for k, v in loaded.items():
            out[k.lower()] = cast(v, cls.CASTERS)
        return out


class InisLoader(NoConvertingPathMixin, IniLoader):  # type: ignore[misc]
    """Ini-like string loader"""

    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from an ini-like file"""
        return iniconfig.IniConfig("<config>", conf).sections
